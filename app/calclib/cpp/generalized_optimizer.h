#pragma once
#include "main.h"
using float_ = std::unique_ptr<float[]>;
using int_ = std::unique_ptr<signed int[]>;
using shfloat_ = std::shared_ptr<float[]>;
//using vector_ = std::unique_ptr<std::vector<size_t>>;

class GeneralizedIndivid :Individ
{
	size_t ncell = 1;
	size_t nrow = 1;
	float penalty_degree = 1;
	boolean_ cells = nullptr;
	float_ rests = nullptr;
	float_ values = nullptr;
	shfloat_ xarray = nullptr;
	shfloat_ yarray = nullptr;
	shfloat_ bounds = nullptr;
	int_ indices = nullptr;
	size_t inheritance_slice = 0;
	std::vector<size_t> shuffled;
	void __inherit(const GeneralizedIndivid*, const GeneralizedIndivid*);
	void inherit__(const GeneralizedIndivid*, const GeneralizedIndivid*);
	const bool isvalid(size_t, size_t,size_t) const;
	void copy_row(size_t, const GeneralizedIndivid*);
	void print_row(size_t) const;
	void __mutate(size_t,size_t);
	bool if_move(const size_t,const signed int) const;
	void move(const size_t, const signed int) const;
	

public:
	using Individ::Individ;
	GeneralizedIndivid(size_t, size_t, std::random_device&,float);
	GeneralizedIndivid();
	~GeneralizedIndivid();	
	bool at(size_t,size_t) const;
	virtual bool at(size_t) const override;
	virtual bool valid() const;
	const float get_rest(size_t) const;
	const float get_val(size_t) const;
	const signed int get_index(size_t) const;
	const size_t index(size_t, size_t) const;
	const size_t x_axis(size_t) const;
	const size_t y_axis(size_t) const;
	const size_t get_inheritance_slice() const;
	void fit(const shfloat_, size_t, const shfloat_, size_t, const shfloat_,size_t);
	const float value();
	virtual  const size_t randint() override;	
	void inherit(const GeneralizedIndivid*, const GeneralizedIndivid*,const size_t);
	virtual  void mutate(size_t) override;
	virtual const float get_rest() const override;
	virtual const float get_val() const override;
	virtual const float metric() const;
};

//template <typename T>
class GeneralizedPopulation
{
protected:
	//T individ;
	using individ_ptr = std::shared_ptr<GeneralizedIndivid>;
	using individ_ptru = std::unique_ptr<GeneralizedIndivid>;
	using dictionary_ = std::unordered_map<size_t, individ_ptr>;	
	using dictionary_iterator = typename dictionary_::iterator;
	
	std::random_device* random_device = nullptr;
	Mutator* mutator_ = nullptr;

	using vector_ = std::vector<size_t>;
	using uniform_ = std::uniform_real_distribution<float>;
	uniform_ random_;
	std::mt19937 random_generator_;
	dictionary_ population_;

	shfloat_ x = nullptr;
	shfloat_ y = nullptr;
	shfloat_ bound = nullptr;

	float epsilon = 1e-3f;
	float tolerance = 0.7f;
	float threshold = 0.7f;
	float inh_threshold = 0.1f;
	float penalty_degree = 1;
	const float inf = std::numeric_limits<float>::infinity();
	float minval = this->inf;
	float maxval = -this->inf;
	bool random_mutate = false;
	size_t npopul = 100;
	size_t maxiter = 100000;
	size_t length = 1;
	size_t nrow = 1;
	size_t ncell = 1;
	size_t mutate_cell = 1;
	size_t cast_number;
	size_t epoch = 1000;
	size_t niter = 0;
	size_t individ_index = 0;
	std::string log;
	std::string path;
	std::ofstream* out;
	virtual void fit();
	void set_limits();
	void add_individ(size_t, individ_ptr, dictionary_*);
	individ_ptr cross(individ_ptr, individ_ptr);
	void selection(vector_*);
	const size_t cast(const vector_&, individ_ptr) const;

	void inherit(dictionary_*, vector_*, size_t&, size_t&, float&, float&, size_t);
	const float frandom();
	void set_mutator(size_t, bool);
	void print_population(dictionary_*);
	void update_population(dictionary_*, size_t, float, float);
	virtual void get_new_population(dictionary_*, size_t&, float&, float&, size_t);






public:
	individ_ptr optimal_individ = nullptr;
	GeneralizedPopulation(size_t, shfloat_,size_t, shfloat_,size_t, shfloat_,  float, float, float, float, size_t, size_t, bool,float);
	~GeneralizedPopulation();
	const size_t niter_() const;
	virtual void optimize(const size_t);
	const std::string __log() const;

};