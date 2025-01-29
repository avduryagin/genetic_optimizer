from app.calclib.py import event_optimizer as ev
import json
import os
path_="/home/ois.ru/avduryagin/Code/data"
file_name='input_optimizer5.json'
fpath=os.path.join(path_,file_name)
with open(fpath,'r') as file:
    json_data=json.load(file)
#json_data['data'][-1]['type']='EVPSPIR'
#json_data['data'][-2]['type']='EVPSPIR'
wrapper=ev.DataWrapperRawJson(json_data)
wrapper.fit()
print(wrapper.log)
jfile=wrapper.data_
data=jfile["data"]
kwargs=jfile["kwargs"]

optimizer=None
log=[]
try:

    optimizer=ev.GeneralizedOptimizer(data,**kwargs)
    log = optimizer.log[:]
    assert len(optimizer.log) == 0, "Data initializing error"
    #optimizer=ev.UniformOptimizer(data,**kwargs)
    result=optimizer.optimize()
    validation = optimizer.validate(wrapper.target_group)

except AssertionError as err:
    print(err)
print(log)
print('fine')