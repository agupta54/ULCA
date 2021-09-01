
from flask import jsonify
import uuid
import time

def post_error(status_code, message,error_type=None):
        message = {
            'code':status_code,
            'message':message,
            'errorID' :str(uuid.uuid4()),
            'timeStamp':eval(str(time.time()).replace('.', '')[0:13])
        }
        return message

class APIResponse :
    def __init__(self, statuscode, data,count=None):
        self.statuscode = statuscode
        self.statuscode['data']     = data
        self.statuscode['count']    = count
    
    def getres(self):
        return jsonify(self.statuscode)

    def getresjson(self):
        return self.statuscode
