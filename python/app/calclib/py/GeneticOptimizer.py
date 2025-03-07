import numpy as np
import app.calclib.py.py_optimizer as pylib
import app.calclib.py.cpp_optimizer as clib

class Optimizer:
    def __init__(self,npopul_=10,bound_=0.,data_=np.array([]).reshape(-1,2),
                 threshold_=0.7,inh_threshold_=0.1,epsilon_=1e-3,mutate_cell_=1,tolerance_=0.7,
                 cast_number_=3,allow_count_=5,engine='cpp',mutate_random_=False,njobs_=1):
        assert ((type(npopul_)==int)&(npopul_>0)),"npopul_ must be a posivive integer "
        assert (type(mutate_cell_) == int)&(mutate_cell_>=0), "mutate_cell_ must be a not negative integer "
        assert (type(allow_count_) == int) & (allow_count_ > 0), "allow_count_ must be a posivive integer "
        assert (type(cast_number_) == int) & (cast_number_ > 0), "allow_count_ must be a posivive integer "
        assert (type(threshold_) == float) & (threshold_ > 0.) & (threshold_ <=1.), "threshold_ must be a posivive float in (0,1] "
        assert (type(inh_threshold_) == float) & (inh_threshold_>= 0.) & (inh_threshold_ <= 1.), "inheritance hreshold_ must be a posivive float in [0,1] "
        assert (type(tolerance_) == float) & (tolerance_ > 0.) & (tolerance_ <= 1.), "tolerance_ must be a posivive float in (0,1] "
        assert (type(epsilon_) == float) & (tolerance_ > 0.), "epsilon_ must be a posivive float "
        assert (type(bound_) == float) , "bound_ must be a  float "
        assert (type(mutate_random_) == bool), "mutate_random_ must be a boolean "
        assert (type(njobs_) == int) & (njobs_> 0), "njobs_ must be a posivive integer "
        self.npopul=npopul_
        self.bound=bound_
        self.mutate_cell=mutate_cell_
        self.allow_count=allow_count_
        self.cast_number=cast_number_
        self.tolerance=tolerance_
        self.epsilon=epsilon_
        self.threshold=threshold_
        self.inh_threshold=inh_threshold_
        self.niter=0
        self.mutate_random=mutate_random_
        self.njobs=njobs_

        assert (type(data_)==np.ndarray) and (data_.shape[1]==2)&(data_.shape[0]>0),"data mast be a positive defined numpy array with shape (-1,2) "
        if data_.dtype!=np.float32:
            self.data=data_.astype(np.float32)
        else:
            self.data=data_
        self.optimizer=None
        if engine=="cpp":
            if self.njobs>1:
                self.optimizer=clib.MultiJobsOptimizer()
            else:
                self.optimizer=clib.Optimizer()
        else:
            self.optimizer=pylib.Population(size=self.npopul,bound=self.bound,x=self.data[:,0],y=self.data[:,1],threshold=self.threshold,epsilon=self.epsilon,
                                            mutate_cell=self.mutate_cell,cast_number=self.cast_number)
        self.solution=None

    def optimize(self):
        if type(self.optimizer)==clib.Optimizer:
            code=np.zeros(self.data.shape[0],dtype=np.int32)
            self.optimizer.optimize(self.data,code,self.npopul,self.bound,self.threshold,self.inh_threshold,self.epsilon,self.tolerance,self.mutate_cell,self.cast_number,self.allow_count,self.mutate_random)
            self.solution=pylib.Individual(size=self.data.shape[0],bound=self.bound)
            self.solution.code=code.astype(bool)
            self.solution.val=self.optimizer.value
            self.solution.rest = self.optimizer.rest
            self.niter=self.optimizer.niter

        if type(self.optimizer) == clib.MultiJobsOptimizer:
            code = np.zeros(self.data.shape[0], dtype=np.int32)
            self.optimizer.optimize(self.data, code, self.npopul, self.bound, self.threshold, self.inh_threshold,
                                    self.epsilon, self.tolerance, self.mutate_cell, self.cast_number, self.allow_count,
                                    self.mutate_random, self.njobs)
            self.solution=pylib.Individual(size=self.data.shape[0],bound=self.bound)
            self.solution.code=code.astype(bool)
            self.solution.val=self.optimizer.value
            self.solution.rest = self.optimizer.rest
            self.niter=self.optimizer.niter

        elif type(self.optimizer) == pylib.Population:
            self.optimizer.optimize(self.allow_count)
            self.solution=self.optimizer.solution
            self.niter=self.optimizer.niter




class GeneralizedOptimizer:
    def __init__(self,npopul_=10,xarray_=np.array([],dtype=np.float32).reshape(-1),yarray_=np.array([],dtype=np.float32).reshape(-1),
                 bounds_=np.array([],dtype=np.float32).reshape(-1),
                 threshold_=0.7,inh_threshold_=0.1,epsilon_=1e-7,mutate_cell_=3,tolerance_=0.7,
                 cast_number_=3,allow_count_=5,random_mutate_=True,njobs_=1,penalty_degree=2.):
        assert ((type(npopul_)==int)&(npopul_>0)),"npopul_ must be a posivive integer "
        assert (type(mutate_cell_) == int)&(mutate_cell_>=0), "mutate_cell_ must be a not negative integer "
        assert (type(allow_count_) == int) & (allow_count_ > 0), "allow_count_ must be a posivive integer "
        assert (type(cast_number_) == int) & (cast_number_ > 0), "allow_count_ must be a posivive integer "
        assert (type(threshold_) == float) & (threshold_ > 0.) & (threshold_ <=1.), "threshold_ must be a posivive float in (0,1] "
        assert (type(inh_threshold_) == float) & (inh_threshold_>= 0.) & (inh_threshold_ <= 1.), "inheritance hreshold_ must be a posivive float in [0,1] "
        assert (type(tolerance_) == float) & (tolerance_ > 0.) & (tolerance_ <= 1.), "tolerance_ must be a posivive float in (0,1] "
        assert (type(epsilon_) == float) & (tolerance_ > 0.), "epsilon_ must be a posivive float "
        assert (type(random_mutate_) == bool), "random_mutate_ must be a boolean "
        assert (type(njobs_) == int) & (njobs_> 0), "njobs_ must be a posivive integer "
        assert (len(yarray_.shape)==1),"Expect a one-dimensional array yarray_"
        assert (len(xarray_.shape) == 1), "Expect a one-dimensional array xarray_"
        assert (len(bounds_.shape) == 1), "Expect a one-dimensional array bounds_"
        assert (xarray_.shape[0]==yarray_.shape[0]*bounds_.shape[0]),"xarray_ length must be equal y_array.shape[0]*bounds_.shape[0]"
        assert(xarray_.dtype==np.float32),"xarray_ dtype must be np.float32"
        assert (yarray_.dtype == np.float32), "yarray_ dtype must be np.float32"
        assert (bounds_.dtype == np.float32), "bounds_ dtype must be np.float32"
        assert (type(penalty_degree)==float),"penalty_degree must be a float "
        self.xarray=xarray_
        self.yarray=yarray_
        self.bounds=bounds_
        self.npopul=npopul_
        self.mutate_cell=mutate_cell_
        self.allow_count=allow_count_
        self.cast_number=cast_number_
        self.tolerance=tolerance_
        self.epsilon=epsilon_
        self.threshold=threshold_
        self.inh_threshold=inh_threshold_
        self.niter=0
        self.random_mutate=random_mutate_
        self.njobs=njobs_
        self.optimizer=clib.GeneralizedOptimizer()
        self.code=np.empty(shape=self.yarray.shape[0],dtype=np.int32)
        self.penalty_degree=penalty_degree
        self.val=0
        self.rest=0
        self.metric=0
    def optimize(self):

        self.optimizer.optimize(self.xarray,self.yarray,self.bounds,self.code,self.npopul,
                                self.threshold,self.inh_threshold,self.epsilon,self.tolerance,
                                self.mutate_cell,self.cast_number,self.allow_count,self.random_mutate,self.penalty_degree)

        self.val=self.optimizer.value
        self.rest=self.optimizer.rest
        self.niter = self.optimizer.niter
        self.metric=self.optimizer.metric












