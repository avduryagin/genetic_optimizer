from flask import request
from app import app_flask

import numpy as np
from flask_restful import Api, Resource
from app.calclib.py import event_optimizer as ev
#import json


api = Api(app_flask)

class Optimizer(Resource):
    def __init__(self, **kwargs):
        self.optimizer=None

    def post(self,*args,**kwargs):
        x=request.json
        data=x["main"]
        kwargs=x["kwargs"]
        self.optimizer=ev.GeneralizedOptimizer(data,**kwargs)
        result=self.optimizer.optimize()
        res = result.loc[:, 'assigned'].to_dict()
        return res

api.add_resource(Optimizer, "/optimizer/")

class UniformOptimizer(Resource):
    def __init__(self, **kwargs):
        self.optimizer=None

    def post(self,*args,**kwargs):
        x=request.json
        data=x["main"]
        kwargs=x["kwargs"]
        self.optimizer=ev.UniformOptimizer(data,**kwargs)
        result=self.optimizer.optimize()
        res=result.loc[:,'assigned'].to_dict()
        return res

api.add_resource(UniformOptimizer, "/uniform_optimizer/")