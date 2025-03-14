import numpy as np
import pandas as pd
from collections.abc import Iterable
import app.calclib.py.GeneticOptimizer as op
from app.logging_format import log_ as formatted_log



class DataWrapper:
    log=[]
    def __init__(self,json_data):
        self.data=None
        self.means=None
        self.grouped=None
        self.cells=None
        self.groups=None
        self.types_=None
        self.index=None
        self.dtypes={'group': np.int32, 'cell': np.int32,
                     'assigned': np.int32, 'order': np.float32,
                      'cost': np.float32, 'type': np.int32}
        self.data_field=self.dtypes.keys()
        self.target_field='target'
        self.json_data=json_data
        self.log=[]

    def fit(self):
        try:
            assert type(self.json_data) == dict, "Expect serialized json data as dict. Got {0} dtype".format(type(self.json_data))
            data_={k:self.json_data[k] for k in self.data_field }
            self.data=pd.DataFrame.from_dict(data_).astype(self.dtypes)
            #self.set_index()
            #self.data.index=self.data.index.astype(np.int32)
            self.index=self.data.index
            self.data.loc[:, 'mask'] = False
            self.means=pd.DataFrame.from_dict(self.json_data[self.target_field],dtype=np.float32)
            self.means.index=self.means.index.astype(self.data["type"].dtype)
            self.means.columns = self.means.columns.astype(self.data["assigned"].dtype)
            self.means.fillna(0., inplace=True)
            row=None
            try:
                row=self.means.loc[-1]
            except KeyError:
                row=self.means.sum(axis=0)
                self.means.loc[-1]=row
            self.assertion_()
            self.grouped=self.data.groupby(["group","type"]).groups
            self.cells=np.unique(self.means.columns)
            assert self.cells.shape[0]==len(self.means.columns),"Invalid json. Expect only unique values of target"
            self.types_ = np.unique(self.means.index)
            assert self.types_.shape[0] == self.means.index.shape[0],"Invalid json. Expect only unique values of types"
            self.groups=np.unique(self.data.loc[:,"group"])

        except KeyError as err:
            item = formatted_log("input json error", None, str(err))
            self.log.append(item.get())
            raise KeyError("Invalid json. Couldn't find one of fields: data, target. Got fields {0}".format(self.json_data.keys()))
        except AssertionError as err:
            item = formatted_log("input json error", None, str(err))
            self.log.append(item.get())

    def set_index(self):
        try:
            indices=list(self.json_data['id'].values())
            index=np.array(indices,dtype=np.int32)
            self.data.index=index
        except Exception:
            self.data.index = self.data.index.astype(np.int32)

    def check_types(self):
        lost=np.array([],dtype=np.int32)
        if self.data is not None:
            mask=~self.data.loc[:,"type"].isin(self.means.index)
            lost=mask[mask].index
            return lost
        return lost






    def assertion_(self):

        dtype = self.data["group"].dtype
        assert dtype == np.int64 or dtype == np.int32 or dtype == np.int16 or dtype == int, "Datatype error! Expect group as integer"
        dtype = self.data["type"].dtype
        assert dtype == np.int64 or dtype == np.int32 or dtype == np.int16 or dtype == int, "Datatype error! Expect type as integer"
        dtype = self.data["cell"].dtype
        assert dtype == np.int64 or dtype == np.int32 or dtype == np.int16 or dtype == int, "Datatype error! Expect cell as integer"
        dtype = self.data["assigned"].dtype
        assert dtype == np.int64 or dtype == np.int32 or dtype == np.int16 or dtype == int, "Datatype error! Expect assigned as integer"
        dtype = self.data["order"].dtype
        assert dtype == np.float64 or dtype == np.float32 or dtype == np.float16 or dtype == float, "Datatype error! Expect cost as float"
        dtype = self.data["cost"].dtype
        assert dtype == np.float64 or dtype == np.float32 or dtype == np.float16 or dtype == float, "Datatype error! Expect cost as float"
        dtype = self.data["mask"].dtype
        assert dtype == bool, "Datatype error! Expect mask as boolean"

        for c in self.means.columns:
            dtype = self.means[c].dtype
            assert dtype == np.float64 or dtype == np.float32 or dtype == np.float16 or dtype == float, "Datatype error! Expect target in cell {0} as float".format(c)

    def get_index(self,cell_,group_,type_):
        try:
            indices=self.grouped[(group_,type_)]
            mask=(~self.data.loc[indices,"mask"])&(self.data.loc[indices,"cell"]<=cell_)
            index=indices[mask]
            return index
        except KeyError:
            return np.array([],dtype=np.int32)

    def assign_index(self,cell_,index_=np.array([],dtype=np.int32)):
        self.data.loc[index_,["assigned",'mask']]=(cell_,True)

    def get_mean(self,cell_,type_):
        try:
            return min(self.means.at[type_,cell_],self.means.at[-1,cell_])
        except KeyError:
            return None
    def set_mean(self,cell_,type_,val_=0):
        self.means.at[-1, cell_] += val_
        if type_<0:
            return
        try:
            self.means.at[type_,cell_]+=val_
            self.means.at[type_,cell_]=min(self.means.at[type_,cell_],self.means.at[-1,cell_])
        except KeyError:
            return

    def loc(self,index=np.array([],dtype=np.int32)):
        if (self.data is None) or (index is None) or(index.shape[0]==0):
            return DataWrapper(dict())
        data_dict=self.data.loc[index].to_dict()
        target_dict=self.means.to_dict()
        main_dict={self.data_field:data_dict,self.target_field:target_dict}
        wrp=DataWrapper(main_dict)
        return wrp
    def at(self,index,column):
        return self.data.at[index,column]

class DataWrapperExp(DataWrapper):

    def __init__(self,json_data):
        super().__init__(json_data)
        self.types_index=None
        self.other_types=None
        self.types_mask=None
        self.group_distance=None

    def fit(self):
        super().fit()
        self.types_index=self.types_[1:]
        mask=self.data.loc[:,'type'].isin(self.types_index)
        self.other_types=self.data.loc[~mask,'type'].value_counts().keys()
        self.types_mask=self.means.loc[self.types_index]>0
        self.group_distance=self.data.loc[:,["group","cell"]].groupby("group").max()

    def types_rating(self,cell=0):
        index=self.types_index[~self.types_mask.loc[:,cell]]
        return index
        #columns=self.cells[(cell+1):]
        #return self.means.loc[index,columns].sum(axis=1).sort_values(ascending=False).index

    def get_index(self,cell_,group_,type_,alpha=1):
        if not isinstance(type_,Iterable):
            index=super().get_index(cell_,group_,type_)
        else:
            indices=[]
            for _type in type_:
                _index = super().get_index(cell_, group_, _type)
                indices.extend(_index)
            index=np.array(indices,dtype=np.int32)
        n = int(index.shape[0] * alpha)
        return index[:n]

class DataWrapperRawJson:
    raw_data=None
    raw_target=None
    raw_target_group=None
    target_=None
    target_group=None
    kwargs=None
    data_=None
    dtypes={'npopul': int,'epsilon': float, 'threshold': float, 'tolerance': float,
             'allow_count': int, 'mutate_cell': int, 'mutate_random': bool, 'cast_number': int, 'njobs': int, 'ncell': int}
    log=[]
    def __init__(self,raw_json,log,uniform_mode=True):
        self.raw_json=raw_json
        self.raw_data = None
        self.raw_target = None
        self.raw_target_group = None
        self.target_ = None
        self.target=None
        self.target_group = None
        self.kwargs = None
        self.data_ = None
        self.data=None
        self.log = log
        self.uniform_mode=uniform_mode
        self.codes=None
        self.uniques=None

    def fit(self):
        try:
            self.raw_data=self.raw_json['data']
            self.kwargs = self.raw_json['kwargs']
            self.__kwargs_assertion__()
            self.data = pd.DataFrame.from_dict(self.raw_data)
            self.data.index=self.data.loc[:,'id'].astype(np.int32)
            if self.uniform_mode:
                self.data.loc[:,'type']=0
            else:
                self.data.rename(columns={"type": "type_"}, inplace=True)
                self.codes, self.uniques = pd.factorize(self.data["type_"])
                self.data["type"] = self.codes

        except KeyError as err:
            item = formatted_log("input json error", None, str(err))
            self.log.append(item.get())
            raise KeyError(
                "Invalid json. Couldn't find one of fields: data, kwargs. Got fields {0}".format(self.raw_json.keys()))
        if  self.uniform_mode:
            self.data_ = {'data': self.data.to_dict(), 'kwargs': self.kwargs}
            self.data_['data']['target'] = []
            return


        try:
            self.raw_target=self.raw_json['target']
            codes_dict = {u: None for u in self.uniques}
            for i in self.data.index:
                type_ = self.data.at[i, 'type_']
                if codes_dict[type_] is None:
                    code = self.data.at[i, 'type']
                    codes_dict[type_] = code

            index = [row['type'] for row in self.raw_target]
            cost = [row['cost'] for row in self.raw_target]
            target = pd.DataFrame(index=index, data=cost)
            target['code'] = np.nan
            codes_dict[-1]=-1
            for code in codes_dict.keys():
                val = codes_dict[code]
                target.at[code, 'code'] = val
            mask = target.loc[:, 'code'].isnull()
            target = target.loc[~mask]
            target.index = target.loc[:, 'code'].astype(np.int32)
            del target['code']
            summ_ = target.isnull().sum(axis=1)
            mask = summ_ < target.shape[1]
            self.target=target.loc[mask]
            self.target_ = self.target.to_dict()
        except KeyError:
            pass

        try:
            self.raw_target_group = self.raw_json['target_group']
            self.target_group = pd.DataFrame.from_dict(self.raw_target_group)
            self.target_group.index = self.target_group.loc[:, 'group'].astype(np.int32)
            del self.target_group['group']
            mask=self.target_group.loc[:,'period'].isnull()
            self.target_group.loc[mask,'period']=self.target.shape[1]+1
            #if mask[mask].shape[0]>0:
                #item = formatted_log("Argument type error", None, "Target group has an empty period for groups {group}".format(group=mask[mask].index.tolist()))
                #self.log.append(item.get())
                #raise AssertionError


        except KeyError:
            pass


        self.data_ = {'data': self.data.to_dict(), 'kwargs': self.kwargs}
        self.data_['data']['target'] = self.target_
        self.__check_types__()

    def __kwargs_assertion__(self):
        raise_error = False
        if self.kwargs is not None:
            for key in self.kwargs.keys():
                arg=self.kwargs[key]
                try:
                    dtype=self.dtypes[key]
                    if not type(arg)==dtype:
                        raise_error=True
                        item = formatted_log("Argument type error", None, "Expect argument {key} as type {dtype}. Got as type {type_}".format(key=key,dtype=dtype,type_=type(arg)))
                        self.log.append(item.get())
                except KeyError:
                    raise_error = True
                    item = formatted_log("Argument type error", None,
                                         "Unknown argument {key}:{dtype}".format(key=key, dtype=arg))
                    self.log.append(item.get())
                    continue
        if raise_error:
            raise AssertionError

    def __check_types__(self):
        lost=np.array([],dtype=np.int32)
        if self.data is not None:
            mask=~self.data.loc[:,"type"].isin(self.target.index)
            lost=mask[mask].index
        if lost.shape[0]>0:
            item = formatted_log("input json error", None,
                                 "The types of ids {id_} are not in target".format(id_=lost.tolist()))
            self.log.append(item.get())
            raise AssertionError("input json error")











class Optimizer:
    def __init__(self,data=pd.DataFrame([],columns=['group', 'cell', 'assigned', 'order', 'cost','mask']),
                 means=pd.DataFrame([],columns=[0,1,2,3,4]),
                 groupby=["cell","group"]):
        self.log=[]
        try:
            dtype=data["group"].dtype
            assert dtype==np.int64 or dtype==np.int32 or dtype==np.int16 or dtype==int,"Datatype error! Expect group as integer"
            dtype=data["type"].dtype
            assert dtype==np.int64 or dtype==np.int32 or dtype==np.int16 or dtype==int,"Datatype error! Expect type as integer"
            dtype = data["cell"].dtype
            assert  dtype==np.int64 or dtype==np.int32 or dtype==np.int16 or dtype==int, "Datatype error! Expect cell as integer"
            dtype = data["assigned"].dtype
            assert dtype==np.int64 or dtype==np.int32 or dtype==np.int16 or dtype==int, "Datatype error! Expect assigned as integer"
            dtype = data["order"].dtype
            assert dtype == np.float64 or dtype== np.float32 or dtype == np.float16 or dtype == float, "Datatype error! Expect cost as float"
            dtype = data["cost"].dtype
            assert dtype == np.float64 or dtype== np.float32 or dtype == np.float16 or dtype == float, "Datatype error! Expect cost as float"
            dtype = data["mask"].dtype
            assert dtype== bool ,"Datatype error! Expect mask as boolean"
            self.data=data
            self.means=means
            self.ncell=means.shape[0]
            self.grouped=data.groupby(groupby)
            self.data.loc[:,'mask']=False
        except AssertionError as err:
            item = formatted_log("input data error", None, str(err))
            self.log.append(item.get())

    def reduce(self):
        for i in self.data.index:
            cell=self.data.at[i,"assigned"]
            if cell>=0:
                type_=self.data.at[i,"type"]
                delta=self.means.at[type_,cell]-self.data.at[i,"cost"]
                if delta>=0:
                    self.means.at[type_,cell]-=self.data.at[i,"cost"]
                    self.data.at[i,'mask']=True
    def get_unassigned(self,cell=0):
        mask=(~self.data.loc[:,'mask'])&(self.data.loc[:,"cell"]<=cell)
        return self.data.index[mask]



    def optimize(self,npopul=100,epsilon = 1e-3,threshold = 0.7,tolerance = 0.7,allow_count = 5,mutate_cell = 1,mutate_random=True,cast_number = 1,njobs=1):
        self.reduce()
        i=0
        while i<self.ncell:
            index_=self.get_unassigned(i)
            grouped=self.data.loc[index_].groupby("group").groups
            for k in grouped.keys():
                index=grouped[k]
                n=index.shape[0]
                if n>0:
                    bound=float(self.means[i])
                    x = self.data.loc[index,"cost"].values*-1
                    y = np.zeros(n, dtype=np.float32)
                    w=np.vstack([x,y],dtype=np.float32).T
                    optimizer=op.Optimizer(data_=w, npopul_=npopul, bound_=bound, threshold_=threshold, epsilon_=epsilon,
                                 tolerance_=tolerance, mutate_cell_=mutate_cell,mutate_random_=mutate_random, cast_number_=cast_number,
                                 allow_count_=allow_count, engine="cpp", njobs_=njobs)
                    optimizer.optimize()
                    solution=optimizer.solution
                    indices=index[solution.code]
                    self.data.loc[indices, "mask"] = True
                    self.data.loc[indices,"assigned"]=i
                    self.means[i] += solution.val
                    if indices.shape[0]!=index.shape[0]:
                        break
            i+=1
        return



class GeneralizedOptimizer:
    log = []
    def __init__(self,json_data, log,check_target=False,npopul=100,epsilon = 1e-3,
                 threshold = 0.7,tolerance = 0.7,allow_count = 5,
                 mutate_cell = 1,mutate_random=True,cast_number = 1,njobs=1,ncell=5):

        try:
            self.log=log
            self.json_data=json_data
            self.npopul=npopul
            self.epsilon=epsilon
            self.threshold=threshold
            self.tolerance=tolerance
            self.allow_count=allow_count
            self.mutate_cell=mutate_cell
            self.mutate_random=mutate_random
            self.cast_number=cast_number
            self.njobs=njobs
            self.alpha=1.
            self.data=None
            self.data=DataWrapperExp(self.json_data)
            self.data.fit()
            self.modes=["type","force","all"]
            self.log.extend(self.data.log)
            if check_target:
                lost_types=self.data.check_types()
                if lost_types.shape[0]>0:
                    item = formatted_log("input json error", None, "The types of ids {id_} are not in target".format(id_=lost_types.tolist()))
                    self.log.append(item.get())


        except Exception as err:
            item = formatted_log("Argument data error. DataFrame has type {0}. Error type {1}".format(self.data.data.dtypes,err), None, str(err))
            self.log.append(item.get())
        finally:
            assert len(self.log)==0, "Input data error"


    def reduce(self):
        for i in self.data.index:
            cell=self.data.at(i,"assigned")
            if cell>=0:
                type_=self.data.at(i,"type")
                val=self.data.at(i,"cost")
                self.data.set_mean(cell,type_,-val)
                self.data.data.at[i,'mask']=True

    def optimize(self,mode="even"):
        #self.alpha=alpha
        if mode=="odd":
            data=self.optimize_odd()
        else:
            data=self.optimize_eve()
        return data

    def optimize_odd(self):
        self.reduce()
        optimizer=OddOptimizer(self.data)
        optimizer.optimize(npopul=self.npopul,epsilon=self.epsilon,threshold=self.threshold,tolerance=self.tolerance,
                           allow_count=self.allow_count,mutate_cell=self.mutate_cell,mutate_random=self.mutate_random,
                           cast_number=self.cast_number,njobs=self.njobs)
        mask=~self.data.data.loc[:,'mask']
        index=self.data.index[mask]
        self.data.data.loc[index,"type"]=-1
        data_=self.data.loc(index)
        data_.fit()
        optimizer=OddOptimizer(data_)
        optimizer.optimize(npopul=self.npopul,epsilon=self.epsilon,threshold=self.threshold,tolerance=self.tolerance,
                           allow_count=self.allow_count,mutate_cell=self.mutate_cell,mutate_random=self.mutate_random,
                           cast_number=self.cast_number,njobs=self.njobs)
        self.data.data.loc[index,'assigned']=data_.data.loc[:,"assigned"]

        return self.data.data
    def optimize_eve(self):
        self.reduce()
        optimizer=EvenOptimizer(self.data)
        optimizer.modes=self.modes
        optimizer.optimize(npopul=self.npopul,epsilon=self.epsilon,threshold=self.threshold,tolerance=self.tolerance,
                           allow_count=self.allow_count,mutate_cell=self.mutate_cell,mutate_random=self.mutate_random,
                           cast_number=self.cast_number,njobs=self.njobs,alpha=self.alpha)

        return self.data.data

    def validate(self,target_group=None):
        if target_group is None:
            return []
        self.data.data.loc[:,'assigned_']=self.data.data.loc[:,'assigned']
        mask=self.data.data.loc[:,'assigned']<0
        ceil=self.data.means.shape[1]
        self.data.data.loc[mask, 'assigned_']=ceil
        assigned = self.data.data.loc[:, ['group', 'assigned_']].groupby('group').max()
        target_group.loc[:,'valid']=False
        target_group.loc[:, 'missed'] = True

        for g in assigned.index:
            cell = assigned.at[g, 'assigned_']
            try:
                cell_ = target_group.at[g, 'period']
                target_group.at[g, 'missed'] = False
                if np.isnan(cell_) or cell_ < 1 or (cell_>=ceil+1):
                    target_group.at[g, 'valid'] = True
                    continue
                if cell<cell_:
                    target_group.at[g, 'valid'] = True
            except KeyError:
                continue
        for g in target_group.index:
            if target_group.at[g,'missed']:
                target_group.at[g, 'valid']=True
        #del target_group['missed']
        valid_list=[{"group":i,"valid":bool(target_group.at[i,'valid'])} for i in target_group.index]
        return valid_list



class OddOptimizer:
    def __init__(self,data=DataWrapper(dict())):
        self.data=data
        self.log=[]
    def optimize(self,npopul=100,epsilon = 1e-3,threshold = 0.7,tolerance = 0.7,allow_count = 5,mutate_cell = 1,mutate_random=True,cast_number = 1,njobs=1):

        #leave_cell=False
        for cell in self.data.cells:
            #leave_cell=False
            for group in self.data.groups:
                #if leave_cell:
                    #break
                for type_ in self.data.types_:
                    bound=float(self.data.get_mean(cell,type_))
                    if not (bound>0):
                        continue
                    index=self.data.get_index(cell,group,type_)
                    n=index.shape[0]
                    if n==0:
                        continue

                    x = self.data.data.loc[index,"cost"].values*-1
                    y = np.zeros(n, dtype=np.float32)
                    w=np.vstack([x,y],dtype=np.float32).T
                    optimizer=op.Optimizer(data_=w, npopul_=npopul, bound_=bound, threshold_=threshold, epsilon_=epsilon,
                                 tolerance_=tolerance, mutate_cell_=mutate_cell,mutate_random_=mutate_random, cast_number_=cast_number,
                                 allow_count_=allow_count, engine="cpp", njobs_=njobs)
                    optimizer.optimize()
                    solution=optimizer.solution
                    indices=index[solution.code]
                    self.data.set_mean(cell, type_, solution.val)
                    self.data.assign_index(cell,indices)

                    #if indices.shape[0]!=index.shape[0]:
                        #leave_cell=True
                        #break

        return



class EvenOptimizer(OddOptimizer):

    def __init__(self,data=DataWrapperExp(dict())):
        super().__init__(data)
        self.modes=["type","force","all"]
        self.alpha=1.

    def optimize(self, npopul=100, epsilon=1e-3, threshold=0.7, tolerance=0.7, allow_count=5, mutate_cell=1,
                 mutate_random=True, cast_number=3, njobs=1,alpha=0.7):
        if (alpha>=0)&(alpha<=1):
            self.alpha=alpha
        cell=0
        for group in self.data.groups:
            cell_=self.fill_by_group(group,cell,npopul=npopul, epsilon=epsilon, threshold=threshold,
                                     tolerance=tolerance, allow_count=allow_count, mutate_cell=mutate_cell,
                                     mutate_random=mutate_random, cast_number=cast_number, njobs=njobs)
            if not (cell_<self.data.cells.shape[0]):
                break
            cell=cell_

    def __fill_by_types__(self,cell,group,mode="type",npopul=100, epsilon=1e-3,
                      threshold=0.7, tolerance=0.7, allow_count=5, mutate_cell=1,
                      mutate_random=True, cast_number=3, njobs=1):
        alpha = 1
        if mode=="type":
            types=self.data.types_index
            main_types=types



        elif mode=="force":
            types=(self.data.types_rating(cell),)
            main_types=(-1,)
            alpha=self.alpha

        else:
            types=(self.data.other_types,)
            main_types = (-1,)


        leave_cell = False
        for type_,main_type in zip(types,main_types):
            bound = float(self.data.get_mean(cell, main_type))
            if not (bound > 0):
                continue
            index = self.data.get_index(cell, group, type_,alpha)

            n = index.shape[0]
            if n == 0:
                continue
            xmin=self.data.data.loc[index, "cost"].values.min()

            if xmin>bound:
                if (mode!="type"):leave_cell=True
                continue
            xsum=self.data.data.loc[index, "cost"].values.sum()
            _val=0
            if xsum<=bound:
                indices=index
                _val=-xsum
            else:
                x = self.data.data.loc[index, "cost"].values * -1
                y = np.zeros(n, dtype=np.float32)
                w = np.vstack([x, y], dtype=np.float32).T
                optimizer = op.Optimizer(data_=w, npopul_=npopul, bound_=bound, threshold_=threshold, epsilon_=epsilon,
                                         tolerance_=tolerance, mutate_cell_=mutate_cell, mutate_random_=mutate_random,
                                         cast_number_=cast_number,
                                         allow_count_=allow_count, engine="cpp", njobs_=njobs)

                optimizer.optimize()
                solution = optimizer.solution
                indices = index[solution.code]
                _val=solution.val
            self.data.set_mean(cell, main_type, _val)
            self.data.assign_index(cell, indices)
            if (mode=="all")&(index.shape[0]!=indices.shape[0]):
                leave_cell=True
                #return leave_cell
        return leave_cell

    def fill_by_types(self,cell,group,mode="type",npopul=100, epsilon=1e-3,
                      threshold=0.7, tolerance=0.7, allow_count=5, mutate_cell=1,
                      mutate_random=True, cast_number=3, njobs=1):
        alpha = 1
        if mode=="type":
            types=self.data.types_index
            main_types=types



        elif mode=="force":
            types=(self.data.types_rating(cell),)
            main_types=(-1,)
            alpha=self.alpha

        else:
            types=(self.data.other_types,)
            main_types = (-1,)


        leave_cell = True
        for type_,main_type in zip(types,main_types):
            bound = float(self.data.get_mean(cell, main_type))
            if not (bound > 0):
                continue
            index = self.data.get_index(cell, group, type_,alpha)

            n = index.shape[0]
            if n == 0:
                continue
            xmin=self.data.data.loc[index, "cost"].values.min()

            if xmin>bound:
                continue

            xsum=self.data.data.loc[index, "cost"].values.sum()
            _val=0
            if xsum<=bound:
                indices=index
                _val=-xsum
            else:
                x = self.data.data.loc[index, "cost"].values * -1
                y = np.zeros(n, dtype=np.float32)
                w = np.vstack([x, y], dtype=np.float32).T
                optimizer = op.Optimizer(data_=w, npopul_=npopul, bound_=bound, threshold_=threshold, epsilon_=epsilon,
                                         tolerance_=tolerance, mutate_cell_=mutate_cell, mutate_random_=mutate_random,
                                         cast_number_=cast_number,
                                         allow_count_=allow_count, engine="cpp", njobs_=njobs)

                optimizer.optimize()
                solution = optimizer.solution
                indices = index[solution.code]
                _val=solution.val

            if indices.shape[0] > 0:
                leave_cell=False
                self.data.set_mean(cell, main_type, _val)
                self.data.assign_index(cell, indices)

        return leave_cell

    def fill_by_group(self,group,cell_=0,npopul=100, epsilon=1e-3,
                      threshold=0.7, tolerance=0.7, allow_count=5, mutate_cell=1,
                      mutate_random=True, cast_number=3, njobs=1)->int:

        #group_distance=self.data.group_distance.at[group,"cell"]
        cell=cell_
        while cell< self.data.cells.shape[0]:
            leave_cell = True
            for mode in self.modes:
                leave_cell_=self.fill_by_types(cell,group,mode=mode,npopul=npopul, epsilon=epsilon, threshold=threshold,
                                         tolerance=tolerance, allow_count=allow_count, mutate_cell=mutate_cell,
                                         mutate_random=mutate_random, cast_number=cast_number, njobs=njobs)
                leave_cell=leave_cell&leave_cell_

            if leave_cell:
                cell+=1
            else:
                cell_=cell
                continue
        return cell_



class UniformOptimizer:
    log = []
    def __init__(self,json_data,log,ncell=5,maxiter=100, npopul=100,epsilon = 1e-3,
                 threshold = 0.7,tolerance = 0.7,allow_count = 5,
                 mutate_cell = 1,mutate_random=True,cast_number = 1,njobs=1):

        try:
            self.log=log
            self.json_data=json_data
            self.ncell=ncell
            self.npopul=npopul
            self.maxiter=maxiter
            self.epsilon=epsilon
            self.threshold=threshold
            self.tolerance=tolerance
            self.allow_count=allow_count
            self.mutate_cell=mutate_cell
            self.mutate_random=mutate_random
            self.cast_number=cast_number
            self.njobs=njobs
            self.niter=0
            self.modes=['all']
            self.fit()
        except Exception as err:
            item = formatted_log("Argument data error", None, str(err))
            self.log.append(item.get())
        finally:
            assert len(self.data.log) == 0, "Input data error"



    def fit(self):
        target={k:{-1:0.} for k in np.arange(self.ncell,dtype=np.float32)}
        self.json_data["target"]=target
        self.data = DataWrapperExp(self.json_data)
        self.log.extend(self.data.log)
        self.data.fit()
        mask=self.data.data.loc[:,"cell"]<self.ncell
        self.data.data=self.data.data.loc[mask]

    def __mean(self,i=0, x=np.array([])):
        if i == x.shape[0] - 1:
            return x[i]
        delta = self.__mean(i + 1, x)
        j = x.shape[0] - i
        return x[i] + (j - 1) * delta / j

    def optimize(self):
        amask = self.data.data.loc[:, "assigned"] < 0
        dtype_=self.data.data["cost"].dtype
        cell_frame = pd.DataFrame(data=np.zeros(shape=(self.ncell, 1),dtype=dtype_), index=np.arange(self.ncell), columns=["cost"])
        self.niter=0
        while self.niter<self.maxiter:
            mask = self.data.data.loc[:, "assigned"] < 0
            missed_number = mask[mask].shape[0]
            #self.log.append([self.niter,missed_number])
            if missed_number == 0:
                break
            agg_cell = self.data.data.loc[mask, ["cell", "cost"]].groupby("cell").sum()
            agg_cell.loc[:, "cost_"] = agg_cell.loc[:, "cost"] / (self.ncell - agg_cell.index).astype(dtype_)
            cell_frame.values.fill(0)
            cell_frame.loc[agg_cell.index, "cost"] = agg_cell.loc[:, "cost_"]
            val_ = self.__mean(0, x=cell_frame.loc[:, "cost"].values)
            rval=self.data.data.loc[mask,'cost'].max()
            lval=self.data.means.at[-1,0]+val_
            val=max(rval,lval)
            self.data.means.loc[-1]=val
            self.data.data.loc[amask, "assigned"] = -1
            #json_data = {"data": self.data.data.to_dict(), "target": self.data.means.to_dict()}
            json_data=self.data.data.to_dict()
            json_data['target']=self.data.means.to_dict()
            optimizer = GeneralizedOptimizer(json_data,self.log,check_target=False,npopul=self.npopul,epsilon=self.epsilon,threshold=self.threshold,tolerance=self.tolerance,
                                             allow_count=self.allow_count,mutate_cell=self.mutate_cell,mutate_random=self.mutate_random,cast_number=self.cast_number,njobs=self.njobs)
            optimizer.modes=self.modes
            self.data.data = optimizer.optimize()
            self.niter+=1
        return self.data.data


