from flask import request,abort,jsonify
from app import app_flask
from flask_restful import Api, Resource
from app.calclib.py import event_optimizer as ev
from app.logging_format import log_ as formatted_log
from app.cef import cef_log

#import json


api = Api(app_flask)

class Optimizer(Resource):
    def __init__(self, **kwargs):
        self.optimizer=None

    def post(self,*args,**kwargs):

        cef_=cef_log()
        cef_.fit_request(request)
        tag=cef_.tag
        token=cef_.jwt_validation
        msg=cef_.decoded
        #token=True
        if token:
            name="JWT token validation on {tag} ".format(tag=tag)
            lmsg=cef_(success=True,msg=name)
            app_flask.logger.info(lmsg)
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
                name="Calculation on {tag} ".format(tag=tag)
                lmsg = cef_(success=True, msg=name)
                app_flask.logger.info(lmsg)
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
                if len(log)>0:
                    name = "Calculation on {tag}.See log for details".format(tag=tag)
                    lmsg = cef_(success=False, msg=name)
                    app_flask.logger.info(lmsg)

                return jsonify({"data": res, "log": log,"validation":validation})



        else:
            name="JWT token validation on {tag} ".format(tag=tag)
            lmsg=cef_(success=False,msg=name)
            app_flask.logger.info(lmsg)
            return abort(401, description=msg)

api.add_resource(Optimizer, "/optimizer/")

class UniformOptimizer(Resource):
    def __init__(self, **kwargs):
        self.optimizer=None

    def post(self,*args,**kwargs):
        cef_=cef_log()
        cef_.fit_request(request)
        tag=cef_.tag
        token=cef_.jwt_validation
        msg=cef_.decoded
        #token=True
        if token:
            name="JWT token validation on {tag} ".format(tag=tag)
            lmsg=cef_(success=True,msg=name)
            app_flask.logger.info(lmsg)
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

                result = self.optimizer.optimize()
                res = [{"id": i, "assigned": int(result.at[i, 'assigned'])} for i in
                          result.index]
                name="Calculation on {tag} ".format(tag=tag)
                lmsg = cef_(success=True, msg=name)
                app_flask.logger.info(lmsg)
            except KeyError:
                item=formatted_log("input json error",None,"Can't find fields data or kwargs")
                log.append(item.get())


            except TypeError as err:
                item=formatted_log("input json error",None,"Argument type error: {0}".format(err))
                log.append(item.get())

            except AssertionError as err:
                item=formatted_log("Assertion error",None,str(err))
                log.append(item.get())


            finally:
                if len(log)>0:
                    name = "Calculation on {tag}.See log for details".format(tag=tag)
                    lmsg = cef_(success=False, msg=name)
                    app_flask.logger.info(lmsg)
                return jsonify({"data": res, "log": log,"validation":validation})

        else:
            name = "JWT token validation on {tag} ".format(tag=tag)
            lmsg = cef_(success=False, msg=name)
            app_flask.logger.info(lmsg)
            return abort(401, description=msg)

api.add_resource(UniformOptimizer, "/uniform_optimizer/")