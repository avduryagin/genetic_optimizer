#include "generalized_optimizer.h"
GeneralizedIndivid::GeneralizedIndivid(size_t nrow_, size_t ncell_, std::random_device& rd,float penalty_degree_=1) 
{
	
	this->ncell = ncell_;
	this->nrow = nrow_;
	this->size = this->ncell * this->nrow;;
	this->val_ = 0;
	this->penalty_degree = penalty_degree_;
	this->code_ = std::make_unique<bool[]>(this->size);
	std::fill_n(this->code_.get(), this->size, false);

	this-> rests= std::make_unique<float[]>(this->ncell);
	std::fill_n(this->rests.get(), this->ncell, 0.f);

	this->values = std::make_unique<float[]>(this->ncell);
	std::fill_n(this->values.get(), this->ncell, 0.f);

	this->cells = std::make_unique<bool[]>(this->ncell);
	std::fill_n(this->cells.get(), this->ncell, true);


	this->indices = std::make_unique<signed int[]>(this->nrow);
	std::fill_n(this->indices.get(), this->nrow, -1);
	size_t i = 0;
	
	while (i < this->nrow)
	{
		this->shuffled.push_back(i);
		++i;
	}

	this->randint_ = std::uniform_int_distribution<size_t>(0, this->size - 1);
	this->random_generator_.seed(rd());
};

GeneralizedIndivid::GeneralizedIndivid() {}
GeneralizedIndivid::~GeneralizedIndivid() {}

const size_t GeneralizedIndivid::x_axis(size_t index) const {
	
	return (size_t)std::floor(index / this->ncell);
};
const size_t GeneralizedIndivid::y_axis(size_t index) const {
	
	return index - this->x_axis(index) * this->ncell;
};

const size_t GeneralizedIndivid::index(size_t x_axis, size_t y_axis) const 
{
	return y_axis+this->ncell*x_axis;

};

bool GeneralizedIndivid::at(size_t x_axis, size_t y_axis) const
{
	size_t index = this->index(x_axis, y_axis);
	return this->at(index);
};

bool GeneralizedIndivid::at(size_t index) const 
{
	return Individ::at(index);
}

void GeneralizedIndivid::fit(const shfloat_ xarray_, size_t x_size, const shfloat_ yarray_, size_t y_size,const shfloat_ bounds_, size_t b_size)
{
	if (!isvalid(x_size, y_size,b_size)) { return; }
	this->xarray = xarray_;
	this->yarray = yarray_;
	this->bounds = bounds_;
	std::vector<size_t> index;
	size_t i = 0, j = 0,col=0,row=0;

	while (i < this->size)
	{
		index.push_back(i);
		++i;
	}
	this->shuffle(index);

	i = 0;
	float s = 0;
	while (i < this->size)
	{
		j = index[i];
		col = this->y_axis(j);
		row = this->x_axis(j);
		
		if (!(this->indices[row]<0)||!this->cells[col]||this->code_[j]) { ++i; continue; }

		s = this->rests[col];
		s += std::abs(this->yarray[row]);

		if (s <= this->bounds[col])
		{
			this->code_[j] = true;
			this->indices[row] = (signed int)col;			
			this->rests[col]=s;		
		}
		
		++i;
	}
	return;

};
const bool GeneralizedIndivid::isvalid(size_t x_size, size_t y_size,size_t b_size) const
{
	if ((x_size == this->size) && (y_size == this->nrow)&&(b_size==this->ncell)) { return true; }
	return false;
}


const float GeneralizedIndivid::value() 
{

	size_t i = 0,  col = 0, row = 0;
	float penalty = (float)this->nrow;
	
	std::fill_n(this->rests.get(), this->ncell, 0.f);
	std::fill_n(this->values.get(), this->ncell, 0.f);

	i = 0;	
	bool alpha = false;
	this->rest_ = 0.f;
	while (i < this->size)
	{
		col = this->y_axis(i);
		row= this->x_axis(i);
		alpha = this->at(row,col);
		this->rests[col] += std::abs(this->yarray[row]) * alpha;
		this->values[col] += this->xarray[i] * alpha;
		penalty -= alpha;
		this->rest_ += this->rests[col];
		++i;
	}
	i = 0;
	//float penalty_ = std::powf(penalty, 2);
	this->val_ = std::pow(penalty, this->penalty_degree);
	while(i<this->ncell)
	{
		this->val_ += this->values[i];
		++i;
	}	
	return this->val_;

};
bool GeneralizedIndivid::valid() const
{
	bool valid__ = true;	
	size_t i = 0;
	while (i<this->ncell)
	{
		//rest__ = bound[i]-std::abs(this->get_rest(i));
		if (std::abs(this->get_rest(i)) > this->bounds[i]) { valid__ = false; break; }
		++i;
	}

	return valid__;

};
const float GeneralizedIndivid::get_rest(size_t index) const 
{
	if (index < this->ncell) { return this->rests[index]; }
	else return 0.f;
};
const float GeneralizedIndivid::get_val(size_t index) const 
{
	if (index < this->ncell) { return this->values[index]; }
	else return 0.f;
};
const float GeneralizedIndivid::get_rest() const
{
	size_t i = 0;
	float rest_ = 0.f;
	while (i<this->ncell)
	{
		rest_ += this->get_rest(i);
		++i;
	}
	return rest_;
}
const float GeneralizedIndivid::get_val() const
{
	size_t i = 0;
	float val_ = 0.f;
	while (i < this->ncell)
	{
		val_ += this->get_val(i);
		++i;
	}
	return val_;
}
const float GeneralizedIndivid::metric() const
{
	return this->val_;
};

const size_t GeneralizedIndivid::randint() 
{
	return Individ::randint();

};


void GeneralizedIndivid::inherit__(const GeneralizedIndivid* mparent, const GeneralizedIndivid* fparent)
{
	size_t row, col, _col, index, i;
	this->inheritance_slice = this->randint();
	row = this->x_axis(this->inheritance_slice);
	col = this->y_axis(this->inheritance_slice);

	_col = col > this->ncell / 2 ? 0 : this->ncell - 1;
	index = this->index(row, _col);
	if (_col > 0) { ++index; }
	//this->inheritance_slice = index;
	row = this->x_axis(index);
	col = this->y_axis(index);
	i = 0;
	while (i < index)
	{
		this->code_[i] = mparent->at(i);
		++i;
	}
	i = index;
	while (i < this->size)
	{
		this->code_[i] = fparent->at(i);
		++i;
	}

	i = 0;
	while (i < row)
	{
		this->indices[i] = mparent->get_index(i);
		++i;
	}
	i = row;
	while (i < this->nrow)
	{
		this->indices[i] = fparent->get_index(i);
		++i;
	}

};

void GeneralizedIndivid::copy_row(size_t row, const GeneralizedIndivid* parent) 
{
	if (!(row < this->nrow)) { return; }
	size_t i = 0,index=0;
	while(i<this->ncell)
	{
		index = this->index(row, i);
		this->code_[index] = parent->at(index);
		++i;
	}

};
void GeneralizedIndivid::__inherit(const GeneralizedIndivid* mparent, const GeneralizedIndivid* fparent)
{
	size_t  count, i,row;
	signed int index;
	bool valid_ = true;
	this->inheritance_slice = this->randint();
	count = (this->x_axis(this->inheritance_slice) + this->y_axis(this->inheritance_slice)) % this->nrow;
	Individ::shuffle(this->shuffled);
	i = 0;
	while(i<this->size)
	{
		this->code_[i] = mparent->at(i);
		++i;
	}
	i = 0;
	while(i<this->ncell)
	{
		this->rests[i] = mparent->get_rest(i);
		++i;
	}
	i = 0;
	while (i < this->nrow)
	{
		this->indices[i] = mparent->get_index(i);
		++i;
	}
	this->bounds = mparent->bounds;
	this->xarray = mparent->xarray;
	this->yarray = mparent->yarray;

	i = 0;	
	while(i<count)
	{
		row = this->shuffled[i];
		index = fparent->get_index(row);
		if(this->if_move(row,index))
		{
			this->move(row, index);
			valid_ = this->valid();
		}
		++i;
	
	}
};

bool GeneralizedIndivid::if_move(const size_t row, const signed int col) const
{
	if (col < 0) { return true; }
	float _rest = this->get_rest(col) + this->yarray[row];
	if (_rest <= this->bounds[col]) { return true; }
	else return false;
};
void GeneralizedIndivid::move(const size_t row, const signed int col) const
{	
	signed int current = this->indices[row];
	if (current == col) { return; }
	size_t index_;
	
	//this->print_row(row);
	this->indices[row] = col;
	if (!(current <0))
	{
		index_ = this->index(row, current);
		this->code_[index_] = 0;
		this->rests[current] -= this->yarray[row];
	}
	if (!(col < 0))
	{
		index_ = this->index(row, col);
		this->code_[index_] = 1;
		this->rests[col] += this->yarray[row];
	}
	//this->print_row(row);
};

const signed int GeneralizedIndivid::get_index(size_t irow) const 
{
	if (irow < this->nrow) { return this->indices[irow]; }
	else return -1;
};

const size_t GeneralizedIndivid::get_inheritance_slice() const 
{
	return this->inheritance_slice;
};

void GeneralizedIndivid::mutate(size_t ncell)
{
	size_t i = 0, index = 0,row=0,col=0;	
	while(i<ncell)
	{ 
		index = this->randint();
		row = this->x_axis(index);
		col= this->y_axis(index);
		//this->print_row(row);
		this->__mutate(row, col);

		//this->print_row(row);
		//std::cout << "----------------\n";
		++i;
	}
}
void GeneralizedIndivid::__mutate(size_t row,size_t col)
{
	if (!(row < this->nrow)||!(col<this->ncell)) { return; }
	signed int _col = 0;
	size_t index = 0;
	_col = this->get_index(row);
	if (_col==col)
	{
		index = this->index(row, col);
		this->code_[index] = 0;
		this->indices[row] = -1;
		return;
	}
	if (!(_col < 0))
	{
		index = this->index(row, _col);
		this->code_[index] = 0;

	}
	index = this->index(row, col);
	this->indices[row] = (signed int)col;
	this->code_[index] = 1;

};

void GeneralizedIndivid::print_row(size_t row) const 
{
	if (row >= this->nrow) { std::cout << "row out of range\n"; }
	size_t i = 0;
	signed int col = 0;
	col = this->get_index(row);
	std::cout << "row " << row<< " ,col  "<<col<<" : ";
	while(i<this->ncell)
	{
		std::cout << this->at(row, i)<<" , ";
		++i;
	}
	std::cout << "\n";
};
void GeneralizedIndivid::inherit(const GeneralizedIndivid* mparent, const GeneralizedIndivid* fparent, const size_t mutate_cell)
{
	this->__inherit(mparent, fparent);
	this->mutate(mutate_cell);

};

GeneralizedPopulation::GeneralizedPopulation(size_t npopul_, shfloat_ bound_, size_t ncell_, shfloat_ y_, size_t nrow_,
	shfloat_ x_, float threshold_ , float inh_threshold_ , float epsilon_ , float tolerance_ , size_t mutate_cell_ , size_t cast_number_ , bool random_mutate_,float penalty_degree_=1  )
{

	this->random_device = new std::random_device();
	this->random_ = uniform_(0.f, 1.f);
	size_t seed = (*this->random_device)();
	this->random_generator_.seed(seed);
	this->npopul = npopul_;
	this->bound = bound_;
	this->x = x_;
	this->y = y_;
	this-> nrow = nrow_;
	this-> ncell = ncell_;	
	this->length = this->nrow*this->ncell;
	this->threshold = threshold_;
	this->inh_threshold = inh_threshold_;
	this->epsilon = epsilon_;
	this->mutate_cell = mutate_cell_;
	this->tolerance = tolerance_;
	this->cast_number = cast_number_;
	this->random_mutate = random_mutate_;
	this->penalty_degree = penalty_degree_;
	this->set_mutator(this->mutate_cell, this->random_mutate);
	this->fit();



};

GeneralizedPopulation::~GeneralizedPopulation()
{
	//this->out->close();
};
void GeneralizedPopulation::set_limits()
{
	this->minval = this->inf;
	this->maxval = -this->inf;
};

void GeneralizedPopulation::set_mutator(size_t ncell, bool random_mutate)
{
	if (this->mutator_ != nullptr) { delete this->mutator_; }

	if (random_mutate && (this->mutate_cell > 1))
	{
		this->mutator_ = new RandomMutator(this->mutate_cell, *this->random_device);
	}
	else
	{
		if (this->mutate_cell > 0)
		{
			this->mutator_ = new Mutator(this->mutate_cell);
		}
		else { this->mutator_ = new Mutator(1); }
	}
};
 void GeneralizedPopulation::fit()
{
	size_t i = 0;
	float val = 0;
	this->set_limits();

	while (i < this->npopul)	{
		
		individ_ptr pointer = std::make_shared<GeneralizedIndivid>(this->nrow, this->ncell, *this->random_device,this->penalty_degree);
		GeneralizedIndivid* individ = pointer.get();
		individ->fit(this->x, this->length, this->y, this->nrow,this->bound,this->ncell);
		val = individ->value();
		if (val < this->minval)
		{
			this->minval = val;
			this->individ_index = i;
		}
		if (val > this->maxval) { this->maxval = val; }

		this->add_individ(i, pointer, &this->population_);		
		++i;
	}
	this->log.append(std::to_string(this->minval) + ",");
	this->optimal_individ = this->population_[this->individ_index];

	//(*this->out) << this->log;
}
void GeneralizedPopulation::add_individ(size_t index, individ_ptr individ_, dictionary_* population) {

	(*population)[index] = individ_;
};

std::shared_ptr<GeneralizedIndivid> GeneralizedPopulation::cross(individ_ptr mparent, individ_ptr fparent)
{

	individ_ptr pointer = std::make_shared<GeneralizedIndivid>(this->nrow, this->ncell, *this->random_device,this->penalty_degree);
	GeneralizedIndivid* child = pointer.get();
	child->inherit(mparent.get(), fparent.get(),this->mutate_cell);
	float val = child->value();
	if (!child->valid()) 
	{   val=0.;
		return nullptr;
	}
	return pointer;

};

void GeneralizedPopulation::selection(vector_* indices)
{
	dictionary_iterator iter = this->population_.begin();
	size_t index = 0;
	float delta = 0;
	delta = (this->maxval - this->minval) * this->threshold + this->minval;
	while (iter != this->population_.end())
	{
		index = iter->first;
		GeneralizedIndivid* individ = iter->second.get();
		if (!(individ->metric() > delta))
		{
			indices->push_back(index);
		}
		++iter;
	}
};
void GeneralizedPopulation::inherit(dictionary_* new_population, vector_* indices, size_t& ninherited, size_t& optimal_index, float& minval, float& maxval, size_t start)
{
	GeneralizedIndivid* current = nullptr;
	size_t ninherited_ = 0;
	float delta = (this->maxval - this->minval) * this->inh_threshold + this->minval, val = 0;
	vector_::iterator iter = indices->begin();
	while (iter != indices->end())
	{
		current = this->population_[*iter].get();
		val = current->metric();
		if (val < delta)
		{

			this->add_individ(start + ninherited_, this->population_[*iter], new_population);

			if (val < minval) { minval = val; optimal_index = ninherited_; }
			if (val > maxval) { maxval = val; }
			++ninherited_;
		}
		++iter;
	}
	ninherited = ninherited_;
};
const size_t GeneralizedPopulation::cast(const vector_& indices, individ_ptr generator_) const
{
	//size_t length_ = indices.size();
	GeneralizedIndivid* generator = generator_.get();
	GeneralizedIndivid* sample = nullptr;

	size_t i = 0, j = 0, index = 0, optimal_index = 0;
	float minval = this->inf, val = 0;
	while (i < this->cast_number)
	{
		j = generator->randint();
		index = indices.at(j);
		sample = this->population_.at(index).get();
		val = sample->metric();
		if (val < minval)
		{
			minval = val;
			optimal_index = index;
		}
		++i;
	}
	return optimal_index;
};

void GeneralizedPopulation::get_new_population(dictionary_* new_population, size_t& optimal_index, float& minval, float& maxval, size_t start=0)
{
	vector_ indices;
	GeneralizedIndivid* current = nullptr;
	individ_ptr fparent = nullptr; individ_ptr mparent = nullptr;
	size_t mparent_index = 0, fparent_index = 0, optimal_index_ = 0,ncol=1;
	this->selection(&indices);

	if (indices.size() == 0) { return; }

	float minval_ = this->inf, maxval_ = -this->inf, val = 0;
	size_t i = 0, k = 0, index = 0, length_ = 0;
	this->inherit(new_population, &indices, k, optimal_index_, minval_, maxval_, start);
	length_ = indices.size();
	individ_ptr generator_ = std::make_shared<GeneralizedIndivid>(length_, ncol, *this->random_device);

	while ((k < this->npopul) && (i < this->maxiter))
	{
		fparent_index = this->cast(indices, generator_);
		mparent_index = fparent_index;
		if (indices.size() > 1)
		{
			while (mparent_index == fparent_index)
			{
				mparent_index = this->cast(indices, generator_);
			}
		}



		++i;
		if (this->frandom() < this->tolerance) {

			mparent = this->population_[mparent_index];
			fparent = this->population_[fparent_index];
			individ_ptr child = this->cross(mparent, fparent);
			if (child != nullptr)
			{
				index = start + k;
				this->add_individ(index, child, new_population);
				current = child.get();
				val = current->metric();
				if (val < minval_)
				{
					minval_ = val;
					optimal_index_ = index;

				}
				if (val > maxval_) { maxval_ = val; }
				++k;
			}
		}


	}
	maxval = maxval_;
	minval = minval_;
	optimal_index = optimal_index_;
};
const float GeneralizedPopulation::frandom()
{
	return this->random_(this->random_generator_);
};

void GeneralizedPopulation::update_population(dictionary_* new_population, size_t optimal_index, float minval, float maxval)
{
	if (new_population == nullptr) { return; }
	this->population_ = *new_population;
	this->minval = minval;
	this->maxval = maxval;
	this->individ_index = optimal_index;
	//this->optimal_individ = this->population_[this->individ_index];

};

void GeneralizedPopulation::print_population(dictionary_* population)
{
	if (population == nullptr) { return; }
	typename dictionary_::iterator iter = population->begin();
	size_t i = 0;
	GeneralizedIndivid* current = nullptr;
	while (iter != population->end())
	{
		current = iter->second.get();
		//current->pint_to_log(this->log, i);
		++iter;
		++i;
	}
};
 void GeneralizedPopulation::optimize(const size_t allow_count)
{
	this->niter = 0;
	size_t count = 0;
	float local_val = this->inf;
	individ_ptr local_individ = nullptr;
	individ_ptr solution = nullptr;
	float main_val = this->minval;
	//std::string path = "//app//log_file_";
	std::string path = "C:\\Users\\avduryagin\\PycharmProjects\\GeneticOptimizer\\data\\";
	std::string path_ = "";
	std::string extension = ".txt";
	std::ofstream out;
	path_ = path + std::to_string(this->niter) + extension;
	out.open(path_);
	//this->out = &out;
	try {

		while (this->niter < this->epoch)
		{
			count = 0;
			local_val = this->inf;
			local_individ = nullptr;


			while (count < allow_count)
			{
				try {
					dictionary_ population;
					size_t optimal_index;
					float maxval_ = -this->inf;
					float minval_ = this->inf;

					this->get_new_population(&population, optimal_index, minval_, maxval_);
					this->update_population(&population, optimal_index, minval_, maxval_);
					this->log.append(std::to_string(this->minval) + ",");


					if ((minval_ < local_val) && (std::abs(minval_ - local_val) > this->epsilon))
					{
						local_val = minval_;
						local_individ = this->population_[this->individ_index];

					}
					++count;
					++this->niter;
					//path_ = path + std::to_string(this->niter) + extension;
					//out.open(path_);
				}
				
				catch (std::exception ex)
				 {
					log.append(ex.what());
					out << log;
					out.close();
					this->niter = this->epoch;
					break;
				}
			}
			if ((local_val < main_val) && (std::abs(local_val - main_val) > this->epsilon))
			{
				main_val = local_val;
				solution = local_individ;

			}
			else if (this->mutate_cell > 0)
			{
				--this->mutate_cell;
				this->set_mutator(this->mutate_cell, this->random_mutate);

			}

			else break;



		}
		if (solution != nullptr) { this->optimal_individ = solution; }
		//this->log.append("solution val " + std::to_string(this->optimal_individ->get_val()));
		out << this->log;
	}
	catch (...) { this->optimal_individ = nullptr; this->log.append("interupted by an error "); out << this->log; }

};
const size_t GeneralizedPopulation::niter_() const { return this->niter; };

const std::string GeneralizedPopulation::__log() const { return this->log; };
