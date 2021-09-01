from flask import Blueprint
from flask_restful import Api
from resources import ASRComputeResource

# end-point for independent service
ASR_COMPUTE_BLUEPRINT = Blueprint("asr-model-compute", __name__)
api = Api(ASR_COMPUTE_BLUEPRINT)
api.add_resource(ASRComputeResource, "/v1/model/compute")
