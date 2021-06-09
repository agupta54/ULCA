import logging
import multiprocessing
import threading
import time
from functools import partial
from logging.config import dictConfig
from configs.configs import parallel_ds_batch_size, no_of_parallel_processes, aws_asr_prefix, \
    sample_size, offset, limit, asr_immutable_keys, asr_non_tag_keys, dataset_type_asr, user_mode_pseudo
from repository.asr import ASRRepo
from utils.datasetutils import DatasetUtils
from kafkawrapper.producer import Producer
from events.error import ErrorEvent
from processtracker.processtracker import ProcessTracker

log = logging.getLogger('file')

mongo_instance = None
repo = ASRRepo()
utils = DatasetUtils()
prod = Producer()
error_event = ErrorEvent()
pt = ProcessTracker()

class ASRService:
    def __init__(self):
        pass

    # Method to load ASR Dataset
    def load_asr_dataset(self, request):
        log.info("Loading ASR Dataset.....")
        try:
            metadata = request
            record = request["record"]
            ip_data = [record]
            batch_data, error_list, pt_list = [], [], []
            total, count, updates, batch = len(ip_data), 0, 0, parallel_ds_batch_size
            if ip_data:
                func = partial(self.get_enriched_asr_data, metadata=metadata)
                pool_enrichers = multiprocessing.Pool(no_of_parallel_processes)
                enrichment_processors = pool_enrichers.map_async(func, ip_data).get()
                for result in enrichment_processors:
                    if result:
                        if result[0] == "INSERT":
                            if len(batch_data) == batch:
                                if metadata["datasetMode"] != user_mode_pseudo:
                                    persist_thread = threading.Thread(target=repo.insert, args=(batch_data,))
                                    persist_thread.start()
                                    persist_thread.join()
                                count += len(batch_data)
                                batch_data = []
                            batch_data.append(result[1])
                            pt_list.append({"status": "SUCCESS", "serviceRequestNumber": metadata["serviceRequestNumber"],
                                            "currentRecordIndex": metadata["currentRecordIndex"]})
                        elif result[0] == "FAILED":
                            error_list.append({"record": result[1], "code": "UPLOAD_FAILED",
                                               "datasetType": dataset_type_asr, "serviceRequestNumber": metadata["serviceRequestNumber"],
                                               "message": "Upload to s3 bucket failed"})
                            pt_list.append({"status": "FAILED", "code": "UPLOAD_FAILED", "serviceRequestNumber": metadata["serviceRequestNumber"],
                                            "currentRecordIndex": metadata["currentRecordIndex"]})
                        elif result[0] == "UPDATE":
                            pt_list.append({"status": "SUCCESS", "serviceRequestNumber": metadata["serviceRequestNumber"],
                                            "currentRecordIndex": metadata["currentRecordIndex"]})
                            updates += 1
                        else:
                            error_list.append({"record": result[1], "code": "DUPLICATE_RECORD", "originalRecord": result[2],
                                               "datasetType": dataset_type_asr, "serviceRequestNumber": metadata["serviceRequestNumber"],
                                               "message": "This record is already available in the system"})
                            pt_list.append({"status": "FAILED", "code": "DUPLICATE_RECORD", "serviceRequestNumber": metadata["serviceRequestNumber"],
                                            "currentRecordIndex": metadata["currentRecordIndex"]})
                pool_enrichers.close()
                if batch_data:
                    if metadata["datasetMode"] != user_mode_pseudo:
                        persist_thread = threading.Thread(target=repo.insert, args=(batch_data,))
                        persist_thread.start()
                        persist_thread.join()
                    count += len(batch_data)
            if error_list:
                error_event.create_error_event(error_list)
            for pt_rec in pt_list:
                pt.create_task_event(pt_rec)
            log.info(f'Done! -- INPUT: {total}, INSERTS: {count}, UPDATES: {updates}, "ERROR_LIST": {error_list}')
        except Exception as e:
            log.exception(e)
            return {"message": "EXCEPTION while loading dataset!!", "status": "FAILED"}
        return {"status": "SUCCESS", "total": total, "inserts": count, "updates": updates, "invalid": error_list}


    # Method to enrich asr dataset
    def get_enriched_asr_data(self, data, metadata):
        try:
            record = self.get_asr_dataset_internal({"audioHash": data["audioHash"], "textHash": data["textHash"]})
            if record:
                dup_data = self.enrich_duplicate_data(data, record, metadata)
                if dup_data:
                    repo.update(dup_data)
                    return "UPDATE", data, record
                else:
                    return "DUPLICATE", data, record
            insert_data = data
            for key in insert_data.keys():
                if key not in asr_immutable_keys:
                    if not isinstance(insert_data[key], list):
                        insert_data[key] = [insert_data[key]]
            insert_data["datasetType"] = metadata["datasetType"]
            insert_data["datasetId"] = [metadata["datasetId"]]
            insert_data["tags"] = self.get_tags(insert_data)
            if metadata["datasetMode"] != 'pseudo':
                epoch = eval(str(time.time()).replace('.', '')[0:13])
                s3_file_name = f'{data["audioFilename"]}|{metadata["datasetId"]}|{epoch}'
                object_store_path = utils.upload_file(data["audioFilePath"], f'{aws_asr_prefix}{s3_file_name}')
                if not object_store_path:
                    return "FAILED", insert_data, insert_data
                insert_data["objStorePath"] = object_store_path
            return "INSERT", insert_data, insert_data
        except Exception as e:
            log.exception(e)
            return None

    def enrich_duplicate_data(self, data, record, metadata):
        db_record = record
        found = False
        for key in data.keys():
            if key not in asr_immutable_keys:
                if key not in db_record.keys():
                    found = True
                    db_record[key] = [data[key]]
                elif isinstance(data[key], list):
                    pairs = zip(data[key], db_record[key])
                    if any(x != y for x, y in pairs):
                        found = True
                        db_record[key].extend(data[key])
                else:
                    if isinstance(db_record[key], list):
                        if data[key] not in db_record[key]:
                            found = True
                            db_record[key].append(data[key])
        if found:
            db_record["datasetId"].append(metadata["datasetId"])
            db_record["tags"] = self.get_tags(record)
            return db_record
        else:
            return False

    def get_tags(self, insert_data):
        tag_details = {}
        for key in insert_data:
            if key not in asr_non_tag_keys:
                tag_details[key] = insert_data[key]
        return list(utils.get_tags(tag_details))

    # Method for deduplication
    def get_asr_dataset_internal(self, query):
        try:
            exclude = {"_id": False}
            data = repo.search(query, exclude, None, None)
            if data:
                return data[0]
            else:
                return None
        except Exception as e:
            log.exception(e)
            return None

    # Method for searching asr datasets
    def get_asr_dataset(self, query):
        log.info(f'Fetching datasets....')
        try:
            off = query["offset"] if 'offset' in query.keys() else offset
            lim = query["limit"] if 'limit' in query.keys() else limit
            db_query, tags = {}, []
            if 'language' in query.keys():
                tags.append(query["language"])
            if 'collectionMode' in query.keys():
                tags.append(query["collectionMode"])
            if 'collectionSource' in query.keys():
                tags.append(query["collectionMode"])
            if 'license' in query.keys():
                tags.append(query["licence"])
            if 'domain' in query.keys():
                tags.append(query["domain"])
            if 'channel' in query.keys():
                tags.append(query["channel"])
            if 'gender' in query.keys():
                tags.append(query["gender"])
            if 'datasetId' in query.keys():
                tags.append(query["datasetId"])
            if tags:
                db_query["tags"] = {"$in": tags}
            exclude = {"_id": False}
            data = repo.search(db_query, exclude, off, lim)
            result, query, count = data[0], data[1], data[2]
            log.info(f'Result --- Count: {count}, Query: {query}')
            path = utils.push_result_to_s3(result, query["serviceRequestNumber"])
            if path:
                size = sample_size
                if count <= 10:
                    size = count
                op = {"serviceRequestNumber": query["serviceRequestNumber"], "count": count, "sample": result[:size], "dataset": path}
            else:
                log.error(f'There was an error while pushing result to S3')
                op = {"serviceRequestNumber": query["serviceRequestNumber"], "count": 0, "sample": [], "dataset": None}
            #prod.produce(op, search_output_topic, None)
            log.info(f'Done!')
            return op
        except Exception as e:
            log.exception(e)
            return {"message": str(e), "status": "FAILED", "dataset": "NA"}

    def delete_asr_dataset(self, delete_req):
        log.info(f'Deleting datasets....')
        records = self.get_asr_dataset({"datasetId": delete_req["datasetId"]})
        d, u = 0, 0
        for record in records:
            if len(record["datasetId"]) == 1:
                repo.delete(record["id"])
                utils.delete_from_s3(record["objStorePath"])
                d += 1
            else:
                record["datasetId"].remove(delete_req["datasetId"])
                record["tags"].remove(delete_req["datasetId"])
                repo.update(record)
                u += 1
        op = {"serviceRequestNumber": delete_req["serviceRequestNumber"], "deleted": d, "updated": u}
        #prod.produce(op, delete_output_topic, None)
        log.info(f'Done!')
        return op


# Log config
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] {%(filename)s:%(lineno)d} %(threadName)s %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {
        'info': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filename': 'info.log'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'stream': 'ext://sys.stdout',
        }
    },
    'loggers': {
        'file': {
            'level': 'DEBUG',
            'handlers': ['info', 'console'],
            'propagate': ''
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['info', 'console']
    }
})