IMPORTANT
=========
Need to initialize the TAP_GA_QL submodule, to do so use the following command:
```sh
git submodule init && git submodule update
```

Can get other networks from
===========================
 * [Networks](https://github.com/maslab-ufrgs/network-files)

Dependencies
============
 * [Cplex](https://www-01.ibm.com/software/commerce/optimization/cplex-optimizer/)
 * [DocPlex](https://pypi.python.org/pypi/docplex)
 * [Python 2.7](https://www.python.org/downloads/)
 * [Pyevolve](https://sourceforge.net/projects/pyevolve/)
 * [Python Mathematical Expression Evaluator](https://pypi.python.org/pypi/py_expression_eval)
 * [matplotlib](http://matplotlib.org/)
 * [NumPy](http://www.numpy.org/)

Usage
=====

```sh
python so_solver.py [OPTIONS]
```
Or:
```sh
./so_solver.py [OPTIONS]
```

Options
=======

```
optional arguments:
  -h, --help            show this help message and exit
  -f FILE               The network file.
  -lp LP                Generate lp file format of the problem
```
