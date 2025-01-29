from app.calclib.py import event_optimizer as ev
import json
import os
path_="/home/ois.ru/avduryagin/Code/data"
file_name='input_optimizer7.json'
fpath=os.path.join(path_,file_name)
with open(fpath,'r') as file:
    json_data=json.load(file)
#json_data['data'][-1]['type']='EVPSPIR'
#json_data['data'][-2]['type']='EVPSPIR'
log=[]
try:
    wrapper=ev.DataWrapperRawJson(json_data,log,uniform_mode=False)
    wrapper.fit()
    #print(wrapper.log)
    jfile=wrapper.data_
    data=jfile["data"]
    kwargs=jfile["kwargs"]
    optimizer=ev.GeneralizedOptimizer(data,log,**kwargs)
    #optimizer=ev.UniformOptimizer(data,log,**kwargs)

    result=optimizer.optimize()
    validation = optimizer.validate(wrapper.target_group)
    print(optimizer.data.data.loc[:,"assigned"])

except AssertionError as err:
    print("error", err)
print("log",log)
print('fine')