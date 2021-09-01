import logging
import os
import time

DEBUG = False
API_URL_PREFIX = "/ulca/apis/asr"
HOST = '0.0.0.0'
PORT = 5001

ENABLE_CORS = False

vakyansh_audiouri_link          =       os.environ.get("VAKYANSH_AUDIO_URI","https://speech-recog-model-api-gateway-new-h3dqga4.ue.gateway.dev/v1/recognize/")
vakyansh_audicontent_link       =       os.environ.get("VAKYANSH_AUDIO_CONTENT_URI","https://speech-recog-model-api-gateway-new-h3dqga4.ue.gateway.dev/v1/recognize/")
shared_storage_path             =       os.environ.get("ULCA_SHARED_STORAGE_PATH","/opt/")



