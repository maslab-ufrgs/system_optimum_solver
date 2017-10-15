"""
Changelog:
    v1.0 - Changelog created. <04/10/2017>
    v1.1 - Function string bug corrected
    v1.2 - Git Repository created

Maintainer: Lucas Nunes Alegre (lucasnale@gmail.com)
Created (changelog): 04/10/2017

This module contains the System Optimal Solver, which calculates the SO of a network.

Warning: Use spaces instead of tabs, or configure your editor to transform tab to 4 spaces.
"""

import argparse
import os
import re
from docplex.mp.model import *
from py_expression_eval import *

# Local modules
from MSA.successive_averages import *


class SOSolver():

    def __init__(self, nodes, edges, od_matrix, name='model'):
        self.nodes = nodes
        self.edges = edges
        self.od_matrix = od_matrix
        self.name = os.path.basename(name).split('.')[0]
        self.model = Model(name=self.name)
        self.vars = {}
        self.system_optimal = -1

    def __generate_constraints__(self):

        # Each edge is a variable of the objective function
        self.vars = {e.name: self.model.continuous_var(name=e.name) for e in self.edges}

        for n in self.nodes:

            flow = 0
            # od is (origin, destiny, demand)
            for od in self.od_matrix.keys():

                # if node is an origin
                if n.name == od.split('|')[0]:
                    flow -= self.od_matrix[od]

                # if node is a destiny
                elif n.name == od.split('|')[1]:
                    flow += self.od_matrix[od]

            leaving = []
            arriving = []
            for edge in self.edges:
                if edge.start == n.name:
                    leaving.append(edge)
                elif edge.end == n.name:
                    arriving.append(edge)

            # Flow Arriving - Flow Leaving == 0 if node is neither an origin or a destiny
            #                              == demand if node is destiny
            #                              == -demand if node is origin
            self.model.add_constraint((sum(self.vars[y.name] for y in arriving) +
                                      (sum(-self.vars[x.name] for x in leaving))) == flow, n.name)

    # Function must be a linear function (f) f*m+n
    def __generate_objective_function__(self):

        cost = 0
        for e in self.edges:

            f = e.function[2]
            for var in e.function[1]:
                f = f.substitute(var, e.params[var])
            f = f.toString()

            m, n = f.replace('(', '').replace(')', '').split('+')

            # m is the parameter which multiplies the variable, n is the constant
            if m.find(e.var) == -1:
                m, n = n, m

            m = float(m.replace(e.var, '').replace('*', ''))
            n = float(n)

            # m*f^2 + n*f
            cost += m*(self.vars[e.name] ** 2) + self.vars[e.name]*n

        self.model.minimize(cost)

    def solve(self, verbose=False, generate_lp=False):

        self.__generate_constraints__()
        self.__generate_objective_function__()
        solution = self.model.solve()

        if solution:
            self.system_optimal = solution.get_objective_value()
            if verbose:
                print(solution.display())

            if generate_lp:
                lpfile = open(self.name+'.lp', 'w')
                lpfile.write(self.model.export_as_lp_string())
                lpfile.close()

        else:
            print('Error calculating System Optimal!')

    def get_system_optimal(self):

        return self.system_optimal


if __name__ == '__main__':

    prs = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                  description="""
                                      System Optimal Solver using the Cplex API""")
    prs.add_argument("-f", dest="file", required=True, help="The network file.\n")

    prs.add_argument("-lp", action="store_true",
                     default=False, help="Generate LP file of the problem.\n")

    args = prs.parse_args()

    v, e, od = generateGraph(args.file, flow=0.0)

    so = SOSolver(v, e, od, name=args.file)
    so.solve(generate_lp=args.lp, verbose=True)

