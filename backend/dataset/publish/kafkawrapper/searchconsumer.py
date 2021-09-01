import json
import logging
import random
import string
from logging.config import dictConfig

from service.parallel import ParallelService
from service.asr import ASRService
from service.ocr import OCRService
from service.monolingual import MonolingualService
from service.asrunlabeled import ASRUnlabeledService

from configs.configs import kafka_bootstrap_server_host, search_input_topic, publish_search_consumer_grp, \
    dataset_type_asr_unlabeled
from configs.configs import dataset_type_parallel, dataset_type_asr, dataset_type_ocr, dataset_type_monolingual
from kafka import KafkaConsumer
from repository.datasetrepo import DatasetRepo

log = logging.getLogger('file')


# Method to instantiate the kafka consumer
def instantiate(topics):
    consumer = KafkaConsumer(*topics,
                             bootstrap_servers=list(str(kafka_bootstrap_server_host).split(",")),
                             api_version=(1, 0, 0),
                             group_id=publish_search_consumer_grp,
                             auto_offset_reset='latest',
                             enable_auto_commit=True,
                             value_deserializer=lambda x: handle_json(x))
    return consumer


# Method to read and process the requests from the kafka queue for dataset search action
def search_consume():
    try:
        topics = [search_input_topic]
        consumer = instantiate(topics)
        repo = DatasetRepo()
        p_service, m_service, a_service, o_service, au_service = ParallelService(), MonolingualService(), ASRService(), OCRService(), ASRUnlabeledService()
        rand_str = ''.join(random.choice(string.ascii_letters) for i in range(4))
        prefix = "DS-SEARCH-" + "(" + rand_str + ")"
        log.info(f'{prefix} -- Running..........')
        while True:
            for msg in consumer:
                try:
                    data = msg.value
                    if data:
                        log.info(f'{prefix} | Received on Topic: {msg.topic} | Partition: {str(msg.partition)}')
                        if repo.search([data["serviceRequestNumber"]]):
                            log.info(f'RELAY record in SEARCH --- {data["serviceRequestNumber"]}')
                            break
                        else:
                            repo.upsert(data["serviceRequestNumber"], {"query": data}, True)
                        log.info(f'PROCESSING - start - SRN: {data["serviceRequestNumber"]}')
                        if data["datasetType"] == dataset_type_parallel:
                            p_service.get_parallel_dataset(data)
                        if data["datasetType"] == dataset_type_ocr:
                            o_service.get_ocr_dataset(data)
                        if data["datasetType"] == dataset_type_asr:
                            a_service.get_asr_dataset(data)
                        if data["datasetType"] == dataset_type_monolingual:
                            m_service.get_monolingual_dataset(data)
                        if data["datasetType"] == dataset_type_asr_unlabeled:
                            au_service.get_asr_unlabeled_dataset(data)
                        log.info(f'PROCESSING - end - SRN: {data["serviceRequestNumber"]}')
                        break
                except Exception as e:
                    log.exception(f'{prefix} Exception in ds search consumer while consuming: {str(e)}', e)
    except Exception as e:
        log.exception(f'Exception in ds search consumer while consuming: {str(e)}', e)


# Method that provides a deserialiser for the kafka record.
def handle_json(x):
    try:
        return json.loads(x.decode('utf-8'))
    except Exception as e:
        log.exception(f'Exception while deserialising: {str(e)}', e)
        return {}

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