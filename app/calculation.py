from flask import request,abort,jsonify
from app import app_flask
import numpy as np
from flask_restful import Api, Resource
from app.calclib.py import event_optimizer as ev
from app.logging_format import log_ as formatted_log
from app.oauth2validation import jwt_token
from app.decorators import add_headers

#import json


api = Api(app_flask)

class Optimizer(Resource):
    def __init__(self, **kwargs):
        self.optimizer=None

    def post(self,*args,**kwargs):
        #token,msg=jwt_token(request)
        msg='Unauthorized'
        token=True
        if token:
            json_data=request.json
            res=[]
            log=[]
            validation=[]
            try:
                wrapper=ev.DataWrapperRawJson(json_data,log,uniform_mode=False)
                wrapper.fit()
                data = wrapper.data_['data']
                kwargs = wrapper.data_['kwargs']
                self.optimizer = ev.GeneralizedOptimizer(data,log, **kwargs)

                result = self.optimizer.optimize()
                validation=self.optimizer.validate(wrapper.target_group)
                res = [{"id": i, "assigned": int(result.at[i, 'assigned'])} for i in
                          result.index]
                #res = result.loc[:, 'assigned'].to_dict()
            except KeyError:
                item=formatted_log("input json error",None,"Can't find fields data or kwargs")
                log.append(item.get())

            except TypeError as err:
                item=formatted_log("input json error",None,"Argument type error: {0}".format(err))
                log.append(item.get())

            except AssertionError as err:
                item=formatted_log("Assertion error",None,str(err))
                log.append(item.get())
                #log.extend(wrapper.log)
                #log.extend(self.optimizer.log)

            finally:
                return jsonify({"data": res, "log": log,"validation":validation})



        else:
            return abort(401, description=msg)

api.add_resource(Optimizer, "/optimizer/")

class UniformOptimizer(Resource):
    def __init__(self, **kwargs):
        self.optimizer=None

    def post(self,*args,**kwargs):
        #token,msg=jwt_token(request)
        msg='Unauthorized'
        token=True

        if token:
            json_data=request.json
            res=[]
            log=[]
            validation=[]
            try:
                wrapper=ev.DataWrapperRawJson(json_data,log,uniform_mode=True)
                wrapper.fit()
                data = wrapper.data_['data']
                kwargs = wrapper.data_['kwargs']
                self.optimizer=ev.UniformOptimizer(data,log,**kwargs)
                #log = self.optimizer.log[:]
                #assert len(self.optimizer.log)==0,"Data initializing error"
                result = self.optimizer.optimize()
                res = [{"id": i, "assigned": int(result.at[i, 'assigned'])} for i in
                          result.index]


            except KeyError:
                item=formatted_log("input json error",None,"Can't find fields data or kwargs")
                log.append(item.get())


            except TypeError as err:
                item=formatted_log("input json error",None,"Argument type error: {0}".format(err))
                log.append(item.get())

            except AssertionError as err:
                item=formatted_log("Assertion error",None,str(err))
                log.append(item.get())
                #log.extend(wrapper.log)
                #log.extend(self.optimizer.log)

            finally:
                return jsonify({"data": res, "log": log,"validation":validation})

        else:
            return abort(401, description=msg)

api.add_resource(UniformOptimizer, "/uniform_optimizer/")