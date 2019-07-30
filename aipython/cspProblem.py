# cspProblem.py - Representations of a Constraint Satisfaction Problem
# AIFCA Python3 code Version 0.7.1 Documentation at http://aipython.org

# Artificial Intelligence: Foundations of Computational Agents
# http://artint.info
# Copyright David L Poole and Alan K Mackworth 2017.
# This work is licensed under a Creative Commons
# Attribution-NonCommercial-ShareAlike 4.0 International License.
# See: http://creativecommons.org/licenses/by-nc-sa/4.0/deed.en

from aipython.utilities import Displayable, dict_union


class Constraint(object):
    """A Constraint consists of
    * name: the unique name of this constraint
    * scope: a tuple of variables
    * condition: a function that can applied to a tuple of values
    for the variables
    """

    def __init__(self, scope, condition):
        self.scope = scope
        self.condition = condition
        if self.condition.__name__ == "<lambda>":
            self.condition.__name__ = "Custom"
        self.repr = self.condition.__name__ + str(self.scope)

    def __repr__(self):
        return self.repr

    def holds(self, assignment):
        """returns the value of Constraint con evaluated in assignment.

        precondition: all variables are assigned in assignment
        """
        return self.condition(*tuple(assignment[v] for v in self.scope))


class CSP(Displayable):
    """A CSP consists of
    * domains, a dictionary that maps each variable to its domain
    * constraints, a list of constraints
    * positions, a dictionary that maps name of each node into its (x,y)-position.
    """

    def __init__(self, domains, constraints, positions={}):
        self.variables = set(domains)
        self.domains = domains
        self.constraints = sorted(constraints, key=lambda con: con.__repr__())
        self.var_to_const = {var: set() for var in self.variables}
        for con in constraints:
            for var in con.scope:
                self.var_to_const[var].add(con)
        self.positions = positions

        # Numbering the conditions with the same names:
        conditions = list(map(lambda con: con.__repr__(), constraints))
        for i in range(len(constraints)):
            occurence = conditions.count(constraints[i].__repr__())
            if occurence == 1:  # only appear once
                continue
            for j in range(occurence):
                # start numbering
                constraints[i + j].repr += str(j)
            i += occurence

    def __str__(self):
        """string representation of CSP"""
        return str(self.domains)

    def __repr__(self):
        """more detailed string representation of CSP"""
        return "CSP(" + str(self.domains) + ", " + str([str(c) for c in self.constraints]) + ")"

    def consistent(self, assignment):
        """assignment is a variable:value dictionary
        returns True if all of the constraints that can be evaluated
                        evaluate to True given assignment.
        """
        return all(con.holds(assignment)
                   for con in self.constraints
                   if all(v in assignment for v in con.scope))

# Constraint Functions:

# Negate the input function


def NOT(fn):
    def toReturn(*args, **kwargs):
        return not fn(*args, **kwargs)
    toReturn.__name__ = "NOT(" + fn.__name__ + ")"
    return toReturn

# Basic constraints:


def TRUE(*args, **kwargs):
    return True


def FALSE(*args, **kwargs):
    return False

# Uniary constraints


def StringEquals(str1, str2=None):
    if str2 is None:
        def toReturn(x):
            return x == str1
        toReturn.__name__ = "StringEquals(" + str1 + ")"
        return toReturn
    return str == str2  # binary constraint


def LessThan(num1, num2=None):
    if num2 is None:
        def toReturn(x):
            return x < str1
        toReturn.__name__ = "LessThan(" + str(num1) + ")"
        return toReturn
    return num1 < num2  # binary constraint


def Equals(num1, num2=None):
    if num2 is None:
        def toReturn(x):
            return x == num1
        toReturn.__name__ = "Equals(" + str(num1) + ")"
        return toReturn
    return num1 == num2  # binary constraint


def GreaterThan(num1, num2=None):
    if num2 is None:
        def toReturn(x):
            return x > num1
        toReturn.__name__ = "GreaterThan(" + str(num1) + ")"
        return toReturn
    return num1 > num2  # binary constraint


def IsTrue(bool):
    return bool


def IsFalse(bool):
    return not bool

# Binary constraints


def AND(bool1, bool2):
    return bool1 and bool2


def OR(bool1, bool2):
    return bool1 or bool2


def IMPLIES(bool1, bool2):
    return (not bool1) or bool2


def XOR(bool1, bool2):
    return (bool1 and (not bool2)) or ((not bool1) and bool2)


csp_empty = CSP({}, [])

csp_simple1 = CSP({'A': {1, 2, 3}, 'B': {1, 2, 3}, 'C': {1, 2, 3}},
                  [Constraint(('A', 'B'), LessThan),
                   Constraint(('B', 'C'), LessThan)])

csp_simple2 = CSP({'A': {1, 2, 3, 4}, 'B': {1, 2, 3, 4}, 'C': {1, 2, 3, 4}},
                  [Constraint(('A', 'B'), LessThan),
                   Constraint(('B',), NOT(Equals(2))),
                   Constraint(('B', 'C'), LessThan)])

csp_extended = CSP({'A': {1, 2, 3, 4}, 'B': {1, 2, 3, 4}, 'C': {1, 2, 3, 4},
                    'D': {1, 2, 3, 4}, 'E': {1, 2, 3, 4}},
                   [Constraint(('B',), NOT(Equals(3))),
                    Constraint(('C',), NOT(Equals(2))),
                    Constraint(('A', 'B'), NOT(Equals)),
                    Constraint(('B', 'C'), NOT(Equals)),
                    Constraint(('C', 'D'), LessThan),
                    Constraint(('A', 'D'), Equals),
                    Constraint(('A', 'E'), GreaterThan),
                    Constraint(('B', 'E'), GreaterThan),
                    Constraint(('C', 'E'), GreaterThan),
                    Constraint(('D', 'E'), GreaterThan),
                    Constraint(('B', 'D'), NOT(Equals))])


def meet_at(p1, p2):
    """returns a function that is true when the words meet at the postions p1, p2
    """
    def meets(w1, w2):
        return w1[p1] == w2[p2]
    meets.__name__ = "meet_at(" + str(p1) + ',' + str(p2) + ')'
    return meets


csp_crossword1 = CSP({'one_across': {'ant', 'big', 'bus', 'car', 'has'},
                      'one_down': {'book', 'buys', 'hold', 'lane', 'year'},
                      'two_down': {'ginger', 'search', 'symbol', 'syntax'},
                      'three_across': {'book', 'buys', 'hold', 'land', 'year'},
                      'four_across': {'ant', 'big', 'bus', 'car', 'has'}},
                     [Constraint(('one_across', 'one_down'), meet_at(0, 0)),
                      Constraint(('one_across', 'two_down'), meet_at(2, 0)),
                      Constraint(('three_across', 'two_down'), meet_at(2, 2)),
                      Constraint(('three_across', 'one_down'), meet_at(0, 2)),
                      Constraint(('four_across', 'two_down'), meet_at(0, 4))])

words1 = {"add", "age", "aid", "aim", "air", "are", "arm", "art",
          "bad", "bat", "bee", "boa", "dim", "ear", "eel", "eft", "lee", "oaf"}

words2 = {"add", "ado", "age", "ago", "aid", "ail", "aim", "air",
          "and", "any", "ape", "apt", "arc", "are", "ark", "arm", "art", "ash",
          "ask", "auk", "awe", "awl", "aye", "bad", "bag", "ban", "bat", "bee",
          "boa", "dim", "ear", "eel", "eft", "far", "fat", "fit", "lee", "oaf",
          "rat", "tar", "tie"}

csp_crossword2 = CSP({'1_down': words1, '2_down': words1, '3_down': words1,
                      '1_across': words1, '4_across': words1, '5_across': words1},
                     [Constraint(('1_down', '1_across'), meet_at(0, 0)),  # 1_down[0]=1_across[0]
                      Constraint(('1_down', '4_across'), meet_at(1, 0)),  # 1_down[1]=4_across[0]
                      Constraint(('1_down', '5_across'), meet_at(2, 0)),
                      Constraint(('2_down', '1_across'), meet_at(0, 1)),
                      Constraint(('2_down', '4_across'), meet_at(1, 1)),
                      Constraint(('2_down', '5_across'), meet_at(2, 1)),
                      Constraint(('3_down', '1_across'), meet_at(0, 2)),
                      Constraint(('3_down', '4_across'), meet_at(1, 2)),
                      Constraint(('3_down', '5_across'), meet_at(2, 2))
                      ])


def is_word(*letters, words=words1):
    """is true if the letters concatenated form a word in words"""
    return "".join(letters) in words


letters = {"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
           "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y",
           "z"}
csp_crossword2d = CSP({"p00": letters, "p01": letters, "p02": letters,
                       "p10": letters, "p11": letters, "p12": letters,
                       "p20": letters, "p21": letters, "p22": letters},
                      [Constraint(("p00", "p01", "p02"), is_word),
                       Constraint(("p10", "p11", "p12"), is_word),
                       Constraint(("p20", "p21", "p22"), is_word),
                       Constraint(("p00", "p10", "p20"), is_word),
                       Constraint(("p01", "p11", "p21"), is_word),
                       Constraint(("p02", "p12", "p22"), is_word)])

# def test(CSP_solver, csp=csp_simple2, solutions=[{'A': 1, 'B': 3, 'C': 4}, {'A': 2, 'B': 3, 'C': 4}]):
#     """CSP_solver is a solver that finds a solution to a CSP.
#     CSP_solver takes a csp and returns a solution.
#     csp has to be a CSP, where solutions is the list of all solutions.
#     This tests whether the solution returned by CSP_solver is a solution.
#     """
#     print("Testing csp with", CSP_solver.__doc__)
#     sol0 = CSP_solver(csp)
#     print("Solution found:", sol0)
#     assert sol0 in solutions, "Solution not found for " + str(csp)
#     print("Passed unit test")
