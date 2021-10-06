#!/usr/bin/python3

import enum
import spot
import sys
import argparse
from scipy.optimize import linear_sum_assignment
import numpy as np
import copy
import os
import subprocess
import itertools
from math import ceil, log2


class Variable:
    """
    Class that contains information retrieved from SAT-result.
     Variable in this class formulates shape of new acceptance condition.
    """

    def __init__(self, var):
        self.type = var[0]
        self.clause = int(var[1])
        self.set = int(var[2].split('=')[0])


class SATformula:
    """
    Represents boolean formula, retrieved from the input automata, that will be given to SAT-solver.

    """

    def __init__(self, bool):
        self.formula = bool
        self.subformula = []
        self.negation = False
        self.imperativ = False

    def __len__(self):
        if not self.subformula:
            return 1
        else:
            return sum(map(len, self.subformula))

    def __str__(self):

        if not self.subformula:

            return ''.join(" " + self.formula + " ")

        elif len(self.subformula) == 1:
            if self.negation and self.imperativ:
                # print("tuna")
                return ''.join('!(' + str(self.subformula[0]) + ')')
            return ''.join('(' + str(self.subformula[0]) + ')')

        else:
            if self.negation and self.imperativ:
                return '!(' + str(self.subformula[0]) + self.formula + ''.join(str(
                    elem) + self.formula for elem in self.subformula[1:-1]) + str(self.subformula[-1]) + ')'
            return '(' + str(self.subformula[0]) + self.formula + ''.join(str(
                elem) + self.formula for elem in self.subformula[1:-1]) + str(self.subformula[-1]) + ')'
    def just_operator(self):
        if is_empty() and ["&", "|", "->", "<->"] in bool and lne(bool) <=3:
            return true
        return false
    def is_empty(self):
        return self.subformula == []

    def add_subf(self, new_subform):
        self.subformula.append(new_subform)

    def negate(self):
        self.negation = not self.negation

    def imper(self):
        self.imperativ = True

    def remove_last_kiddo(self):
        self.subformula.pop()

    def subformula_list(self):
        return self.subformula


class MarkType(enum.Enum):
    """Represents whether acceptance set T appears in the formula as Fin(T) or Inf(T).

    Arguments:
        enum {int}
    """
    Inf = 1
    Fin = 2


class ACCMark:
    """Represents an acceptance set.
    """

    def __init__(self, mtype, num):
        """ACCMark constructor.

        Arguments:
            mtype {MarkType} -- denotes whether a set appears in Inf or Fin term in the formula
            num {int} -- number of the acceptance set
        """
        self.type = mtype
        self.num = num

    def __str__(self):
        """Return the information about ACCMark as string.

        Returns:
            string -- ACCMarks information as string
        """
        return ''.join(
            ["Inf" if self.type == MarkType.Inf else "Fin", '(', str(self.num), ')'])

    def __eq__(self, other):
        """Compare two ACCMarks, return true if they are the same, false otherwise.

        Arguments:
            other {ACCMark} -- the other ACCMark

        Returns:
            bool -- true if marks are the same, false otherwise
        """
        if (self.type == other.type) and (self.num == other.num):
            return True
        else:
            return False


class PACC:
    """
        Class for DNF form of acceptance formula
         format self.formula = [[ACCMark]]
    """

    def __init__(self, acc):
        self.formula = parse_acc(acc)

    def __str__(self):
        f = []
        for dis in self.formula:
            f.append('(')
            for con in dis:
                f.append(str(con))
                if con is not dis[-1]:
                    f.append(" & ")
            f.append(')')
            if dis is not self.formula[-1]:
                f.append(" | ")
        return ''.join(f)

    def __len__(self):
        return len(self.formula)

    def int_format(self):
        f = []
        for dis in self.formula:
            d = []
            for con in dis:
                d.append(con.num)
            f.append(d)
        return f

    def resolve_redundancy(self):
        """

        Returns:

        """
        rem_d = []
        int_f = self.int_format()
        for i in range(len(self.formula)):
            for j in range(len(self.formula)):
                if i != j and set(int_f[i]).issubset(set(int_f[j])) and not set(
                        int_f[i]) == set(int_f[j]) and j not in rem_d:
                    rem_d.append(j)

        res_f = []
        for i in range(len(self.formula)):
            if self.formula[i] not in res_f and i not in rem_d:
                res_f.append(self.formula[i])
        self.formula = res_f

    def clean_up(self, present_acc_sets):
        clean_f = []
        marks = present_acc_sets
        for dis in self.formula:
            clean_dis = []
            for con in dis:
                if con.num in marks:
                    clean_dis.append(con)
            if clean_dis:
                clean_f.append(clean_dis)
        self.formula = clean_f
        self.resolve_redundancy()




### PARSE ACC ###

def parse_acc(acc):
    """Parses an acc in DNF and returns the formula represented by list of
    lists of ACCMarks. The inner lists represent disjuncts of the formula. The
    inner lists contain ACCMark (see ACCMark class documentation) objects
    representing atomic conditions (such as Inf(1)).

    Arguments:
        acc {spot::acc_cond::acc_code} -- spot representation of acceptance condition formula

    Returns:
        [[ACCMark]] -- list of lists of ACCMarks
    """
    if acc == "":
        return []
    formula = []
    for dis in str(acc).split('|'):
        new_dis = []
        for con in dis.split('&'):
            mtype = None
            if con.find("Fin") != -1:
                mtype = MarkType.Fin
            else:
                mtype = MarkType.Inf
            num = []
            for c in con:
                if c.isdigit():
                    num.append(c)
            if not num:
                return []
            new_dis.append(ACCMark(mtype, int(''.join(num))))
        formula.append(new_dis)
    return formula
