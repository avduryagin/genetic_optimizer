#define _USE_MATH_DEFINES
#include "bind.h"

PYBIND11_MODULE(genetic_lib, m)
{
	py::class_<optimizer>(m, "Optimizer")
		.def_readonly("value", &optimizer::val)
		.def_readonly("rest", &optimizer::rest)
		.def_readonly("niter", &optimizer::niter)
		.def(py::init())
		//.def("fit", &optimizer::fit)
		.def("optimize", &optimizer::optimize);

	py::class_<multijobs_optimizer>(m, "MultiJobsOptimizer")
		.def_readonly("value", &multijobs_optimizer::val)
		.def_readonly("rest", &multijobs_optimizer::rest)
		.def_readonly("niter", &multijobs_optimizer::niter)
		.def(py::init())
		//.def("fit", &optimizer::fit)
		.def("optimize", &multijobs_optimizer::optimize);

	py::class_<generalized_optimizer>(m, "GeneralizedOptimizer")
		.def_readonly("value", &generalized_optimizer::val)
		.def_readonly("rest", &generalized_optimizer::rest)
		.def_readonly("niter", &generalized_optimizer::niter)
		.def_readonly("metric", &generalized_optimizer::metric_)
		.def(py::init())
		//.def("fit", &optimizer::fit)
		.def("optimize", &generalized_optimizer::optimize);

} 