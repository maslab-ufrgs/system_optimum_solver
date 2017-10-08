# System Optimal Solver
Python implementation, using the Cplex Api, to calculate the System Optimal value of a given network.

Can get networks from
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
  -h, --help            show this help message and exit
  -f FILE               The network file.
  -lp LP                Generate lp file format of the problem
```
