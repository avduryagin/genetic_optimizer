from setuptools import setup, Extension
import pybind11
import os
import sys
path=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,path)
sources_=[os.path.join(path,f) for f in ['bind.cpp','main.cpp','pymodule.cpp','generalized_optimizer.cpp']]
cpp_args = ['-std=c++14','-fvisibility=hidden']

sfc_module = Extension(
    'genetic_lib',
    sources=sources_,
    include_dirs=[pybind11.get_include(),os.path.join(pybind11.get_include(),"include")],
    #library_dirs=[os.getcwd()],
    language='c++',
    extra_compile_args=cpp_args,
    )

setup(
    name='genetic_lib',
    version='2.0',
    author='Duryagin',
    author_email='duryagin.mail@gmail.com',
    description='genetic optimizer for python',
    ext_modules=[sfc_module],
)