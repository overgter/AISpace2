"""
Utilities for converting to and from a Python CSP (aipython.cspProblem.CSP)
and a Graph<ICSPGraphNode, IGraphEdge> in JavaScript.
"""

from string import Template

from aipython.cspProblem import (AND, CSP, FALSE, IMPLIES, NOT, OR, TRUE, XOR,
                                 Constraint, Equals, GreaterThan, IsFalse,
                                 IsTrue, LessThan, meet_at)

import re


def csp_to_json(csp, widget_model=None):
    """Converts a Python CSP instance to a dictionary representable as JSON.
    Args:
        csp (aipython.cspProblem.CSP): The CSP instance to convert to a dictionary.
        widget_model: Instance of widget model passed by ipywidgets during conversion. Never used; you can ignore it.
    Returns:
        (dict or None):
            A CSP that is representable in JSON. None if no CSP was provided.
            This means the dictionary has no references to object instances.
            This JSON should be immediately usable in creating a new CSP Graph in JavaScript.
            See the TypeScript definition of IGraphJSON for details of its shape.
    """
    if not csp:
        return None

    csp_json = {'nodes': [], 'edges': []}

    # Maps variables to their IDs
    node_map = {var: str(hash(var)) for var in csp.domains}

    # Maps (variable, constraint) to their corresponding arc IDs
    edge_map = {}

    for i, (var, value) in enumerate(csp.domains.items()):
        csp_json['nodes'].append({
            'id': node_map[var],
            'name': var,
            'type': 'csp:variable',
            'idx': i,
            'domain': list(value)
        })
        if var in csp.positions:
            csp_json['nodes'][-1]['x'] = csp.positions[var][0]
            csp_json['nodes'][-1]['y'] = csp.positions[var][1]

    for (i, constraint) in enumerate(csp.constraints):
        constraint_id = str(hash(constraint))
        constraint_name = constraint.__repr__()
        csp_json['nodes'].append({
            'id': constraint_id,
            'name': constraint_name,
            'type': 'csp:constraint',
            'idx': i,
            'combinations_for_true': csp.get_combinations_for_true(constraint)
        })
        if constraint_name in csp.positions:
            csp_json['nodes'][-1]['x'] = csp.positions[constraint_name][0]
            csp_json['nodes'][-1]['y'] = csp.positions[constraint_name][1]

        # Create a link from the constraint to each variable in its scope
        for var in constraint.scope:
            link_id = str(hash((var, constraint)))
            link = {
                'id': link_id,
                'source': node_map[var],
                'target': constraint_id
            }

            csp_json['edges'].append(link)

    return csp_json


def generate_csp_graph_mappings(csp):
    """Generate a ID mapping from a CSP for communicating with the frontend.
    Why is this useful? You want to tell the frontend to highlight a node or edge, for example.
    You aren't able to pass an instance directly to the frontend, because that node/edge instance is a Python object.
    Therefore, in order to tell the frontend which node/edge to highlight, you pass its ID instead.
    Args:
        csp (aipython.cspProblem.CSP): The CSP instance to generate mappings for.
    Returns:
        (dict, dict):
            The first dictionary is a node map, where the keys are node names (strings),
            and values are the IDs (also strings) of the nodes in the resulting JSON.
            For example, `node_map['A'] -> 'a6c!dv33'` and `node_map[A_lt_B_constraint] -> '205cvlkj'.
            You can ignore this dictionary - it is provided for convenience.
            The second dictionary is a edge map.
            The keys are a tuple of (node name, Constraint instance).
            The values are the IDs (string) of the edge connecting them in the resulting JSON.
            For example, `edge_map[('A', A_lt_B_constraint)] -> 'wer3jbvcs2'`.
            You can ignore this dictionary - it is provided for convenience.
    """
    if not csp:
        return ({}, {})

    node_map = {var: str(hash(var)) for var in csp.domains}
    edge_map = {}

    for (_, constraint) in enumerate(csp.constraints):
        constraint_id = str(hash(constraint))
        node_map[constraint] = constraint_id

        for var in constraint.scope:
            link_id = str(hash((var, constraint)))
            edge_map[(var, constraint)] = link_id

    return (node_map, edge_map)


def find_used_condition_func(constraintType):
    conditions_used = []
    conditions = ["Equals", "LessThan", "GreaterThan",
                  "TRUE", "FALSE", "IsTrue", "IsFalse",
                  "AND", "OR", "XOR", "IMPLIES"]

    if constraintType in conditions:
        conditions_used.append(constraintType)

    if re.match(r'Equals\(.*\)', constraintType):
        conditions_used.append("Equals")
    if re.match(r'LessThan\(.*\)', constraintType):
        conditions_used.append("LessThan")
    if re.match(r'GreaterThan\(.*\)', constraintType):
        conditions_used.append("GreaterThan")

    if (constraintType[4:len(constraintType)-1] in conditions) and (constraintType[0:4] == "NOT("):
        conditions_used.append("NOT")

    return conditions_used


def json_to_csp(graph_json, widget_model=None):
    """Converts a CSP represented by a JSON dictionary into a Python CSP instance.
    Note that because a CSP doesn't use the concept of IDs, unlike the JSON graph representation,
    IDs will be lost and will be different if you convert the result of this function back to JSON.
    Args:
        graph_json (dict): A dictionary representing JSON to be converted into a CSP instance.
        widget_model: Instance of widget model passed by ipywidgets during conversion. Never used; you can ignore it.
    Returns:
        (aipython.cspProblem.CSP or None):
             An instance of CSP that was converted from the provided JSON. None if no JSON was provided.
    """
    if not graph_json:
        return None

    true = True
    false = False

    domains = {
        node['name']: set(node['domain'])
        for node in graph_json['nodes'] if node['type'] == 'csp:variable'
    }

    constraints = []

    for node in graph_json['nodes']:
        scope = []
        if node['type'] == 'csp:constraint':
            condition_name = node['condition_name']
            condition_fn = LessThan
            callable = "condition_fn = " + condition_name
            exec(callable)
            # Find the links with the target as this constraint
            for link in graph_json['edges']:
                if link['target'] == node['id']:
                    source_node = next(n for n in graph_json['nodes']
                                       if n['id'] == link['source'])
                    scope.append(source_node['name'])
                elif link['source'] == node['id']:
                    source_node = next(n for n in graph_json['nodes']
                                       if n['id'] == link['target'])
                    scope.append(source_node['name'])

            if scope:
                c = Constraint(tuple(scope), condition_fn)
                c.condition_name = condition_name
                constraints.append(c)

    positions = {node['name']: (int(node['x']), int(node['y']))
                 for node in graph_json['nodes']}

    return CSP(domains, constraints, positions)


def csp_to_python_code(csp, need_positions=False):
    """Converts a CSP into Python code that, when executed, creates the CSP.
    Example:
        ::
            >>> csp_to_python_code(csp)
            'from aipython.cspProblem import CSP, Constraint
            csp = CSP({"A": [1, 2, 3], "B": [1, 2, 3]}, Constraint(("A", "B"), lt))'
    Args:
        csp (aipython.cspProblem.CSP): The CSP instance to convert to Python code.
    Returns:
        (string):
            A string containing Python code. Executing this string will cause a CSP to be created.
    """
    conditions_used = []

    domains = csp.domains
    constraint_strings = []
    for constraint in csp.constraints:
        scope = constraint.scope
        name = constraint.condition_name
        conditions_used = conditions_used + find_used_condition_func(name)
        constraint_strings.append("Constraint({}, {})".format(scope, name))
    positions = csp.positions if need_positions else {}
    conditions_used = list(dict.fromkeys(conditions_used))

    template = """from aipython.cspProblem import CSP, Constraint, $conditions_used\n
csp = CSP(
    domains=$domains,
    constraints=[$constraints],
    positions=$positions)"""

    return Template(template).substitute(
        conditions_used=', '.join(conditions_used),
        domains=domains,
        constraints=', '.join(constraint_strings),
        positions=positions)