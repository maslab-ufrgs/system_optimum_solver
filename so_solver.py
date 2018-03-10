"""
Changelog:
    v1.0 - Changelog created. <04/10/2017>
    v1.1 - Function string bug corrected
    v1.2 - Git Repository created
    v2.0 - Included more constraints, which were causing some networks to give a wrong answer <10/03/2018>

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
	self.model.float_precision = 6
        self.phi_vars = {}
	self.x_vars = {}
	self.l_vars = {}
        self.system_optimal = -1
        self.sum_flows = sum(od_matrix.values())

    def _generate_vars(self):
	for e in self.edges:
            self.phi_vars[e.name] = self.model.continuous_var(name='phi_'+e.name)
            self.l_vars[e.name] = self.model.continuous_var(name='l_'+e.name)
            for k in self.od_matrix.keys():
                self.x_vars[e.name+k] = self.model.continuous_var(name='x_'+k+'_'+e.name)

    def _generate_flow_conservation_constraint(self):

        # Each edge is a variable of the objective function
        for k in self.od_matrix.keys():
            for n in self.nodes:

                leaving = []
                arriving = []
                for edge in self.edges:
                    if edge.start == n.name:
                        leaving.append(edge)
                    elif edge.end == n.name:
                        arriving.append(edge)
            
                # if node is an origin
                if n.name == k.split('|')[0]: 
                    demand = -self.od_matrix[k]
                elif n.name == k.split('|')[1]:
                    demand = self.od_matrix[k]
                else:
                    demand = 0
            # Flow Arriving - Flow Leaving == 0 if node is neither an origin or a destiny
            #                              == demand if node is destiny
            #                              == -demand if node is origin
                self.model.add_constraint((sum(self.x_vars[y.name+k] for y in arriving) -
                                          (sum(self.x_vars[x.name+k] for x in leaving))) == demand, n.name+k)

    def _generate_total_flow_constraint(self):
        for e in self.edges:
            somatorio = sum(self.x_vars[e.name+k] for k in self.od_matrix.keys())
            self.model.add_constraint(self.l_vars[e.name] == somatorio)

    def _generate_domain_constraint(self):
        for e in self.edges:
            self.model.add_constraint(self.l_vars[e.name] >= 0)	
            self.model.add_constraint(self.phi_vars[e.name] >= 0)
	    for k in self.od_matrix.keys():
                self.model.add_constraint(self.x_vars[e.name+k] >= 0)

    # Function must be a linear function (f) f*m+n or f/m+n
    # TODO: bug with scientific notation parametesr in py expression eval
    def _generate_cost_constraint(self):

        cost = 0
        for e in self.edges:

            f = e.function[2]
            for var in e.function[1]:
                f = f.substitute(var, float(e.params[var]))
            f = f.toString()

            m, n = f.replace('(', '').replace(')', '').split('+')

            # m is the parameter which multiplies the variable, n is the constant
            if m.find(e.var) == -1:
                m, n = n, m

            # f/m
            if m.find('*') == -1:
                m = float(m.replace(e.var, '').replace('/', ''))
                m = 1/m
            #f*m
            else:
                m = float(m.replace(e.var, '').replace('*', ''))

            n = float(n)

            # m*f^2 + n*f
            cost = m*(self.l_vars[e.name] ** 2) + self.l_vars[e.name]*n

            self.model.add_constraint(cost <= self.phi_vars[e.name])

    def _generate_objective_function(self):
	self.model.minimize(sum(self.phi_vars.values()))

    def solve(self, verbose=False, generate_lp=False):

        self._generate_vars()
        self._generate_objective_function()
        self._generate_cost_constraint()
        self._generate_total_flow_constraint()
        self._generate_flow_conservation_constraint()
        self._generate_domain_constraint()

        solution = self.model.solve()

        if solution:

            self.system_optimal = solution.get_objective_value()/self.sum_flows

            if verbose:
                print(solution.display())
                print('System Optimal = ' + str(self.system_optimal))

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

