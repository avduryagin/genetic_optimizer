#include "bind.h"

optimizer::optimizer() {};
optimizer::~optimizer()
{
	if (this->x != nullptr) { delete[] this->x; }
	if (this->y != nullptr) { delete[] this->y; }
};

void optimizer::init(f_array* data_ptr_, int_array& indices, unsigned int npopul_, float bound_, float threshold_ = 0.7f, float inh_threshold_ = 0.1f, float epsilon_ = 1e-3f, float tolerance_ = 0.7f, unsigned int mutate_cell_ = 1, unsigned int cast_number_ = 3, unsigned int allow_count_ = 5, bool mutate_random_ = false) 
{
	this->data_ptr = data_ptr_;
	if (this->data_ptr->shape(1) != 2) { return; }
	this->length = this->data_ptr->shape(0);
	this->x = new float[this->length];
	this->y = new float[this->length];
	this->allow_count = size_t(allow_count_);
	this->npopul = size_t(npopul_);
	this->mutate_cell = size_t(mutate_cell_);
	this->bound = bound_;
	this->threshold = threshold_;
	this->inh_threshold = inh_threshold_;
	this->epsilon = epsilon_;
	this->tolerance = tolerance_;
	this->mutate_random = mutate_random_;

	size_t i = 0;
	while (i < this->length)
	{
		this->x[i] = data_ptr->at(i, 0);
		this->y[i] = data_ptr->at(i, 1);		
		++i;
	}

};
void optimizer::optimize(f_array* data_ptr_, int_array& indices, unsigned int npopul_, float bound_, float threshold_ = 0.7f, float inh_threshold_ = 0.1f, float epsilon_ = 1e-3f, float tolerance_ = 0.7f, unsigned int mutate_cell_ = 1, unsigned int cast_number_ = 3, unsigned int allow_count_ = 5,bool mutate_random_=false)
{
	this->init(data_ptr_, indices, npopul_, bound_, threshold_, inh_threshold_, epsilon_, tolerance_, mutate_cell_, cast_number_, allow_count_, mutate_random_);
	
	std::string log;
	std::string path;
	std::ofstream out;
	path = "//app//log_file_.txt";	
	out.open(path);
	log.append("length: " + std::to_string(this->length)+"\n");
	log.append("npopul: " + std::to_string(this->npopul) + "\n");
	log.append("mutate_cell: " + std::to_string(this->mutate_cell) + "\n");
	log.append("allow_count: " + std::to_string(this->allow_count) + "\n");
	log.append("bound: " + std::to_string(this->bound) + "\n");
	log.append("threshold: " + std::to_string(this->threshold) + "\n");
	log.append("epsilon: " + std::to_string(this->epsilon) + "\n");
	log.append("tolerance: " + std::to_string(this->tolerance) + "\n");
	log.append("njobs: " + std::to_string(this->njobs) + "\n");
	

	Population optimizer_ = Population(this->npopul, this->bound, this->x, this->y, this->length, this->threshold, this->inh_threshold, this->epsilon, this->tolerance, this->mutate_cell, this->cast_number, this->mutate_random,true);
	optimizer_.optimize(this->allow_count);
	std::shared_ptr<Individ> pointer = optimizer_.optimal_individ;
	Individ* individ = pointer.get();
	this->val = individ->get_val();
	this->rest = individ->get_rest();

	size_t i = 0;
	while (i < this->length)
	{
		indices.mutable_at(i) = int(individ->at(i));
		++i;
	}
	this->optimizer_ptr = &optimizer_;
	this->niter = optimizer_.niter_();
	//out << log;


	
};
void multijobs_optimizer::init(f_array* data_ptr_, int_array& indices, unsigned int npopul_, float bound_, float threshold_ = 0.7f, float inh_threshold_ = 0.1f, float epsilon_ = 1e-3f, float tolerance_ = 0.7f, unsigned int mutate_cell_ = 1, unsigned int cast_number_ = 3, unsigned int allow_count_ = 5, bool mutate_random_ = false, unsigned int njobs_ = 1)
{
	optimizer::init(data_ptr_, indices, npopul_, bound_, threshold_, inh_threshold_, epsilon_, tolerance_, mutate_cell_, cast_number_, allow_count_, mutate_random_);
	this->njobs = njobs_;
};
multijobs_optimizer::multijobs_optimizer() :optimizer{} {};
multijobs_optimizer::~multijobs_optimizer() {};
void multijobs_optimizer::optimize(f_array* data_ptr_, int_array& indices, unsigned int npopul_, float bound_, float threshold_ = 0.7f, float inh_threshold_ = 0.1f, float epsilon_ = 1e-3f, float tolerance_ = 0.7f, unsigned int mutate_cell_ = 1, unsigned int cast_number_ = 3, unsigned int allow_count_ = 5, bool mutate_random_ = false, unsigned int njobs_ = 1)
{
	this->init(data_ptr_, indices, npopul_, bound_, threshold_, inh_threshold_, epsilon_, tolerance_, mutate_cell_, cast_number_, allow_count_, mutate_random_,njobs_);
	std::string log;
	std::string path;
	std::ofstream out;
	path = "//app//log_file_.txt";	
	out.open(path);
	log.append("length: " + std::to_string(this->length) + "\n");
	log.append("npopul: " + std::to_string(this->npopul) + "\n");
	log.append("mutate_cell: " + std::to_string(this->mutate_cell) + "\n");
	log.append("allow_count: " + std::to_string(this->allow_count) + "\n");
	log.append("bound: " + std::to_string(this->bound) + "\n");
	log.append("threshold: " + std::to_string(this->threshold) + "\n");
	log.append("epsilon: " + std::to_string(this->epsilon) + "\n");
	log.append("tolerance: " + std::to_string(this->tolerance) + "\n");
	log.append("njobs: " + std::to_string(this->njobs) + "\n");
	out << log;
	out.close();
	
	PopulationParallel optimizer_ = PopulationParallel(this->npopul, this->bound, this->x, this->y, this->length, this->threshold, this->inh_threshold, this->epsilon, this->tolerance, this->mutate_cell, this->cast_number, this->mutate_random, this->njobs);
	try {

		optimizer_.optimize(this->allow_count);
		std::shared_ptr<Individ>  pointer = optimizer_.optimal_individ;
		if (pointer == nullptr) { throw std::invalid_argument("Empty answer"); log.append("thrown an exception "); out << log; out.close(); }
		Individ* individ = pointer.get();

		this->val = individ->get_val();		
		this->rest = individ->get_rest();		
		this->niter = optimizer_.niter_();		
		size_t i = 0;
		while (i < this->length)
		{
			indices.mutable_at(i) = int(individ->at(i));			
			++i;
		}

	}
	catch (...)
	{
		log.append("error");
		out << log;
		out.close();
	}
};
generalized_optimizer::generalized_optimizer() {}
generalized_optimizer::~generalized_optimizer() {}
void generalized_optimizer::optimize(f_array* x, f_array* y, f_array* b, int_array& code, unsigned int npopul_, 
	float threshold_ = 0.7f, float inh_threshold_ = 0.1f, float epsilon_ = 1e-3f, float tolerance_ = 0.7f, 
	unsigned int mutate_cell_ = 1, unsigned int cast_number_ = 3, unsigned int allow_count_ = 5, bool random_mutate_ = false, float penalty_degree_=2)
{
	std::string log;
	std::string path;
	std::ofstream out;
	//path = "//app//log_file_.txt";
	path = "C:\\Users\\avduryagin\\PycharmProjects\\GeneticOptimizer\\data\\log_file_.txt";
	out.open(path);

	size_t nrow = 0,ncell=0,i=0;	
	this->allow_count = size_t(allow_count_);
	this->npopul = size_t(npopul_);
	this->mutate_cell = size_t(mutate_cell_);	
	this->threshold = threshold_;
	this->inh_threshold = inh_threshold_;
	this->epsilon = epsilon_;
	this->tolerance = tolerance_;
	this->random_mutate = random_mutate_;
	this->penalty_degree = penalty_degree_;
	this->xarray = x;
	this->yarray = y;
	this->bounds = b;
	this->penalty_degree = penalty_degree_;
	nrow = this->yarray->shape(0);
	ncell= this->bounds->shape(0);
	this->xarray_ = std::shared_ptr<float []>(new float[ncell * nrow]);
	this->yarray_ = std::shared_ptr<float[]>(new float[nrow]);
	this->bounds_= std::shared_ptr<float[]>(new float[ncell]);
	//this->xarray_ = std::make_shared<float[]>(ncell*nrow);
	//this->yarray_ = std::make_shared<float[]>(nrow);
	//this->bounds_ = std::make_shared<float[]>(ncell);

	try {
		i = 0;
		while (i < ncell)
		{
			this->bounds_[i] = this->bounds->at(i);
			++i;
		}
		i = 0;
		while (i < nrow)
		{
			this->yarray_[i] = this->yarray->at(i);
			++i;
		}
		i = 0;
		while (i < nrow * ncell)
		{
			this->xarray_[i] = this->xarray->at(i);
			++i;
		}

		GeneralizedPopulation optimizer = GeneralizedPopulation(this->npopul, this->bounds_, ncell, this->yarray_, nrow, this->xarray_,
			this->threshold, this->inh_threshold, this->epsilon, this->tolerance, this->mutate_cell,
			this->cast_number, this->random_mutate, this->penalty_degree);
		optimizer.optimize(this->allow_count);
		this->niter = optimizer.niter_();
		GeneralizedIndivid* solution = optimizer.optimal_individ.get();
		if (solution == nullptr) { throw std::invalid_argument("Empty answer"); log.append("thrown an exception "); out << log; out.close(); }
		i = 0;
		while(i<nrow)
		{
			code.mutable_at(i) = solution->get_index(i);
			++i;
		
		}
		this->metric_ = solution->metric();
		this->val = solution->get_val();
		this->rest= solution->get_rest();
		


	}
	catch (...)
	{
		log.append("error");
		out << log;
		out.close();
	}
	
}