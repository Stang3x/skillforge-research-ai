import os
os.environ['LOCAL_TEST'] = '1'
import importlib
importlib.import_module('evaluation.benchmark_suite')
