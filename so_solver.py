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

import cplex
from docplex.mp.model import *

import os
from time import localtime
import string
import argparse

# Local modules
from modules.classes import *


class SOSolver():

    def __init__(self, nodes, edges, od_list, name):
        self.nodes = nodes
        self.edges = edges
        self.od_list = od_list
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
            for od in self.od_list:
                # if node is an origin
                if n.name == od[0]:
                    flow -= od[2]
                # if node is a destiny
                elif n.name == od[1]:
                    flow += od[2]
            # Flow Arriving - Flow Leaving == 0 if node is neither an origin or a destiny
            #                              == demand if node is destiny
            #                              == -demand if node is origin
            self.model.add_constraint((sum(self.vars[y.name] for y in pickEdgesListAll(n, self.edges) if y.end == n.name) +
                                      (sum(-self.vars[x.name] for x in pickEdgesList(n, self.edges)))) == flow, n.name)

    # Function must be a linear function (f) f*m+n
    def __generate_objective_function__(self):

        cost = 0
        for e in self.edges:
            m, n = e.function.replace('(', '').replace(')','').split('+')

            # m is the parameter which multiplies the variable, n is the constant
            if m.find('f') == -1:
                m, n = n, m

            m = float(m.replace('f', '').replace('*', ''))
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

    v, e, od = read_infos(args.file, flow=0)

    so = SOSolver(v, e, od, args.file)
    so.solve(generate_lp=args.lp, verbose=True)
