# System Optimum Solver
Python implementation, using the Cplex Api, to calculate the System Optimum value of a given network.

Network's cost functions must be linear.

 There is the need to initialize the submodules, to do so use the following command:
```sh
git submodule init && git submodule update
```

Can get networks from
===========================
 * [Networks](https://github.com/maslab-ufrgs/network-files)

Dependencies
============
 * [Cplex](https://www-01.ibm.com/software/commerce/optimization/cplex-optimizer/)
 * [DocPlex](https://pypi.python.org/pypi/docplex)
 * [Python 3](https://www.python.org/downloads/)
 * [Python Mathematical Expression Evaluator](https://pypi.python.org/pypi/py_expression_eval)

Usage
=====

```sh
python so_solver.py [OPTIONS]
```
Or:
```sh
./so_solver.py [OPTIONS]
```
To get the System Optimal:
```sh
so = SOSolver(nodes, edges, od_matrix)
so.solve()
system_optimal = so.get_system_optimum()
```

The System Optimum
==================
![alt text](https://github.com/maslab-ufrgs/system_optimal_solver/blob/master/system_optimum.png)


Options
=======

```
  -h, --help            show this help message and exit
  -f FILE               The network file.
  -lp LP                Generate lp file format of the problem
```

REFERENCES:
=======

1. Stefanello,Fernando and Bazzan, Ana L. C., 2016. Traffic Assignment Problem - Extending Braess Paradox.
2. http://wiki.inf.ufrgs.br/network_files_specification.
