from flask import request
import os
import time
from app.oauth2validation import jwt_token


class cef_log:
    def __init__(self):
        self.CEF=0
        self.deviceVendor="ASUPROJECT"
        self.deviceProduct = "OIS PIPE"
        self.deviceVersion = "0.0"
        self.deviceEventClassId=0
        self.agentSeverity="INFO"
        self.user='user'
        self.msg=""
        self.shost=""
        self.dhost=""
        self.src=""
        self.dst=""
        self.outcome='success'
        self.decoded=None
        self.jwt_validation=False
        self.tag=""



    def fit_env(self):
        try:
            self.deviceVendor=os.environ.get('deviceVendor')
            self.deviceProduct = os.environ.get('deviceProduct')
            self.deviceVersion = os.environ.get('deviceVersion')
        except KeyError:
            pass
    def fit_request(self,request):
        self.user=request.remote_user
        self.dhost=request.origin
        self.shost=request.host
        self.src=request.remote_addr
        if len(request.server)>1:
            dst=request.server[0]
        else:
            dst=request.server
        self.dst=dst
        self.tag=request.url_rule
        self.__parse_token__(request)

    def __parse_token__(self,request):
        self.jwt_validation,self.decoded=jwt_token(request)
        #self.outcome=self.jwt_validation

    def __fill__(self):
        return ("CEF:{CEF}|{deviceVendor}|{deviceProduct}|{deviceVersion}|{deviceEventClassId}|{Severity}|"
                "user:{user}|dhost:{dhost}|dst:{dst}|shost:{shost}|src:{src}|{msg}|{outcome}|end:{end:.0f}".format(
            CEF=self.CEF,deviceProduct=self.deviceProduct,deviceVendor=self.deviceVendor,
            deviceVersion=self.deviceVersion,deviceEventClassId=self.deviceEventClassId,Severity=self.agentSeverity,
            user=self.user,dhost=self.dhost,dst=self.dst,shost=self.shost,src=self.src,msg=self.msg,outcome=self.outcome,end=time.time()
        ))



    def __call__(self,success=False,msg="",Severity="INFO"):
        if success:
            self.outcome='success'
        else:
            self.outcome = 'failed'
        self.agentSeverity=Severity
        self.msg=msg
        return self.__fill__()




