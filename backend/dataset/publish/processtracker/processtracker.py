import logging
import uuid
from datetime import datetime
from logging.config import dictConfig
from configs.configs import pt_publish_tool, pt_inprogress_status, pt_success_status, pt_failed_status
from .ptrepo import PTRepo

log = logging.getLogger('file')

mongo_instance = None
repo = PTRepo()

class ProcessTracker:
    def __init__(self):
        pass

    def create_task_event(self, data):
        try:
            log.info(f'Publishing pt event for -- {data["serviceRequestNumber"]}')
            task_event = self.search_task_event(data, pt_publish_tool)
            if task_event:
                return self.update_task_event(data, task_event)
            task_event = {"id": str(uuid.uuid4()), "tool": pt_publish_tool, "serviceRequestNumber": data["serviceRequestNumber"], "status": pt_inprogress_status,
                          "startTime": str(datetime.now()), "lastModified": str(datetime.now())}
            if data["status"] == "SUCCESS":
                processed_count = [{"type": "success", "count": 1}, {"type": "failed", "typeDetails": {}, "count": 0}]
            else:
                processed_count = [{"type": "failed", "typeDetails": {data["code"]: 1}, "count": 1}, {"type": "success", "count": 0}]
            details = {"currentRecordIndex": data["currentRecordIndex"], "processedCount": processed_count, "timeStamp": str(datetime.now())}
            task_event["details"] = details
            repo.insert(task_event)
        except Exception as e:
            log.exception(e)

    def update_task_event(self, data, task_event):
        task_event = task_event[0]
        processed = task_event["details"]["processedCount"]
        if data["status"] == "SUCCESS":
            for value in processed:
                if value["type"] == "success":
                    value["count"] += 1
        else:
            found = False
            for value in processed:
                if value["type"] == "failed":
                    type_details = value["typeDetails"]
                    for key in type_details:
                        if key == data["code"]:
                            type_details[key] += 1
                            found = True
                    if not found:
                        type_details[data["code"]] = 1
                    value["count"] += 1
        details = {"currentRecordIndex": data["currentRecordIndex"], "processedCount": processed, "timeStamp": str(datetime.now())}
        task_event["details"] = details
        task_event["lastModified"] = str(datetime.now())
        repo.update(task_event)
        return None

    def search_task_event(self, data, tool):
        query = {"serviceRequestNumber": data["serviceRequestNumber"], "tool": tool}
        exclude = {"_id": False}
        result = repo.search(query, exclude, None, None)
        return result



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