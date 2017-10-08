from py_expression_eval import Parser
import string


class Node(object):
    """
    Represents a node in the graph.
    """
    def __init__(self, name):
        """
        In:
            name:String = Name of the node.
        """
        self.name = name	# name of the node
        self.dist = 1000000	# distance to this node from start node
        self.prev = None	# previous node to this node
        self.flag = 0		# access flag

    def __repr__(self):
        return repr(self.name)


class Edge(object):
    """
    Represents an edge in the graph.
    In:
        name:String = Name of the edge ("start"-"end").
        start:Node = Start node of the edge.
        end:Node = End node of the edge.
        cost:Float = Cost of the edge.
    """
    def __init__(self, name, start, end, cost):
        self.name = name
        self.start = start
        self.end = end
        self.cost = cost # represents the edge's cost under free flow (or under the specified flow)


class EdgeRC(Edge):
    """
    Represents an edge for the route_choice program.
    Inherits from the Edge class from the KSP code.
    In:
        function:String = The cost function.
    """

    def __init__(self, name, start, end, cost, function):
        Edge.__init__(self, name, start, end, cost)
        self.function = function

    def __repr__(self):
        return repr(self.name)

    def eval_cost(self, var_value):
        """
        Calculates the value of the cost formula at a given value.
        In:
            var_value:Float = Variable value.

        Out:
            value:Float = result of the calculation.
        """
        parser = Parser()
        expression = parser.parse(self.function)
        return expression.evaluate({'f': var_value})

def is_number(arg):
    '''
    This function try to convert whatever is its argument to a float number.

    Input:
        arg:Anything = The object that it tries to convert to a number.
    Output:
        True if it converts successfully to a float.
        False if it can't, by getting a ValueError exception.

    >>> is_number(1)
    True
    >>> is_number(1e1000)
    True
    >>> is_number('5000')
    True
    >>> is_number(3.141598)
    True
    >>> is_number('a')
    False
    >>> is_number('hello')
    False
    >>> is_number(Node('a'))
    Traceback (most recent call last):
    ...
    TypeError: float() argument must be a string or a number
    '''
    try:
        float(arg)
        return True
    except ValueError:
        return False


# returns the list of edges starting in node u
def pickEdgesList(u, E):
	uv = []
	for edge in E:
		if edge.start == u.name:
			uv.append(edge)
	return uv


# returns the list of edges that start or end in node u
def pickEdgesListAll(u, E):
	uv = []
	for edge in E:
		if edge.start == u.name or edge.end == u.name:
			uv.append(edge)
	return uv


def generateGraph(graph_file, flow=0.0):
    """
    Generates the graph from a text file following the specifications(available @
        http://wiki.inf.ufrgs.br/network_files_specification).
    In:
        graph_file:String = Path to the network(graph) file.
        flow:Float = Value to sum the cost of the edges.

    Out:
        V:List = List of vertices or nodes of the graph.
        E:List = List of the edges of the graph.
        OD:List = List of the OD pairs in the network.
    """
    V = [] # vertices
    E = [] # edges
    F = {} # cost functions
    OD = [] # OD pairs

    lineid = 0
    for line in open(graph_file, 'r'):
        lineid += 1
        # ignore \n
        line = line.rstrip()
        # ignore comments
        hash_pos = line.find('#')
        if hash_pos > -1:
            line = line[:hash_pos]

        # split the line
        taglist = line.split()
        if len(taglist) == 0:
            continue

        if taglist[0] == 'function':
            # process the params
            params = taglist[2][1:-1].split(',')
            if len(params) > 1:
                raise Exception('Cost functions with more than one parameter are not yet'\
                                'acceptable! (parameters defined: %s)' % str(params)[1:-1])

            # process the function
            function = Parser().parse(taglist[3])

            # process the constants
            constants = function.variables()
            if params[0] in constants: # the parameter must be ignored
                constants.remove(params[0])

            # store the function
            F[taglist[1]] = [params[0], constants, function]

        elif taglist[0] == 'node':
            V.append(Node(taglist[1]))

        elif taglist[0] == 'dedge' or taglist[0] == 'edge': # dedge is a directed edge
            # process the cost
            function = F[taglist[4]] # get the corresponding function
            # associate constants and values specified in the line (in order of occurrence)
            param_values = dict(zip(function[1], map(float, taglist[5:])))

            param_values[function[0]] = flow # set the function's parameter with the flow value
            cost = function[2].evaluate(param_values) # calculate the cost

            # create the edge(s)
            E.append(Edge(taglist[1], taglist[2], taglist[3], cost))
            if taglist[0] == 'edge':
                E.append(Edge('%s-%s'%(taglist[3], taglist[2]), taglist[3], taglist[2], cost))

        elif taglist[0] == 'od':
            OD.append(taglist[1])

        else:
            raise Exception('Network file does not comply with the specification!'\
                            '(line %d: "%s")' % (lineid, line))

    return V, E, OD


def read_infos(graph_file, flow):
    """
    Read the edges and OD pairs from the file in this program format(with the functions of each).
    In:
        graph_file:String = Path to the network file.
        flow:Integer = Base flow of the network.
    Out:
        vo:Node = List of the nodes of the network.
        new_edges:EdgeRC = List of edges in the correct form for this program.
        od_list:OD = List of OD pairs of the network.
    """
    functions = {}
    new_edges = []
    od_list = []

    #Uses the KSP function to get the infos
    vertices, edges, _ = generateGraph(graph_file, flow=flow)

    #Read again the file to store information in the correct form
    for line in open(graph_file, 'r'):
        taglist = string.split(line)
        if taglist[0] == 'function':
            variables = []
            variables = taglist[2].replace('(', '')
            variables = variables.replace(')', '')
            variables = variables.split(',')
            functions[taglist[1]] = [taglist[3], variables]

        elif taglist[0] == 'dedge' or taglist[0] == 'edge':
            constants = []
            cost_formula = ""
            freeflow_cost = 0
            constant_acc = 0
            if len(taglist) > 5:
                i = 5
                while i <= (len(taglist) - 1):
                    constants.append(taglist[i])
                    i += 1
                parser = Parser()
                ##[4] is function name.[0] is expression
                exp = parser.parse(functions[taglist[4]][0])
                LV = exp.variables()
                buffer_LV = []
                for l in LV:
                    if l not in functions[taglist[4]][1]:
                        constant_acc += 1
                        buffer_LV.append(l)

                #check if the formula has any parameters(variables)
                flag = False
                for v in functions[taglist[4]][1]:
                    if v in LV:
                        flag = True

                buffer_dic = {}
                i = 0
                for index in range(constant_acc):
                    buffer_dic[buffer_LV[index]] = float(constants[index])
                    i = 1

                if not flag:
                    freeflow_cost = exp.evaluate(buffer_dic)
                    cost_formula = str(freeflow_cost)

                elif is_number(functions[taglist[4]][0]):
                    cost_formula = functions[taglist[4]][0]

                else:
                    exp = exp.simplify(buffer_dic)
                    cost_formula = exp.toString()

                for edge in edges:
                    if edge.name == taglist[1] and (edge.start == taglist[2] \
                        or edge.start == taglist[3]) and (edge.end == taglist[2] \
                        or edge.end == taglist[3]):
                        new_edges.append(EdgeRC(edge.name, edge.start, edge.end, edge.cost,
                                                        cost_formula))
                        if taglist[0] == 'edge':
                            new_edges.append(EdgeRC('%s-%s'%(edge.end, edge.start), edge.end,
                                                            edge.start, edge.cost, cost_formula))

            else:
                cost_formula = ""
                freeflow_cost = 0
                parser = Parser()
                if is_number(functions[taglist[4]][0]):
                    cost_formula = functions[taglist[4]][0]

                else:
                    exp = parser.parse(functions[taglist[4]][0])
                    cost_formula = exp.toString()

                for edge in edges:
                    if edge.name == taglist[1] and (edge.start == taglist[2] or edge.start == taglist[3]) \
                    and (edge.end == taglist[2] or edge.end == taglist[3]):
                        new_edges.append(EdgeRC(edge.name, edge.start, edge.end, edge.cost,
                                                        cost_formula))
                        if taglist[0] == 'edge':
                            new_edges.append(EdgeRC(edge.name, edge.end, edge.start, edge.cost,
                                                            cost_formula))

        elif taglist[0] == 'od':
            od_list.append((taglist[2], taglist[3], float(taglist[4])))

    return  vertices, new_edges, od_list