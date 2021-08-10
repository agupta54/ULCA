from flask_restful import Resource
from flask import request
from models.response import CustomResponse
from models.status import Status
import config
import logging
from services import NotifierService

log = logging.getLogger('file')
service = NotifierService()
# rest request for block merging individual service
class NotifierResource(Resource):

    # reading json request and reurnung final response
    def post(self):
        log.info("Request received for notifiying the users")
        body    =   request.get_json()
        emails  =   body["emails"]
        
        try:
            service.notify_user(emails)
            res = CustomResponse(Status.SUCCESS.value,None,None)
            log.info("response successfully generated.")
            return res.getres()
        except Exception as e:
            log.info(f'Exception on NotifierResource {e}')