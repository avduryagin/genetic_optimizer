from app.calclib.py import event_optimizer as ev
import json
import os
path_="/home/ois.ru/avduryagin/Code/data"
file_name='optimizer2_.json'
fpath=os.path.join(path_,file_name)
with open(fpath,'r') as file:
    jfile=json.load(file)
data=jfile["data"]
kwargs=jfile["kwargs"]

optimizer=ev.GeneralizedOptimizer(data,**kwargs)
#optimizer=ev.UniformOptimizer(data,**kwargs)
result=optimizer.optimize()

print('fine')