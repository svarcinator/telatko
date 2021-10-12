#!/usr/bin/python3


import spot
import enum
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
        class for DNF form of acceptance formula
        tzn. format self.formula = [[ACCMark]], kde ACCMark je trida reprezentujici jednu akc. mnozinu T1,
        takze konstruktor bude ACCMark(type, num) napr Inf(3)
    """

    def __init__(self, acc):
        self.formula = parse_acc(acc)
        self.sat = None  # satisfied?

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

    def __getitem__(self, index):
        return self.formula[index]

    def __len__(self):
        return len(self.formula)

    def acc_len(self):
        l = 0
        for dis in self.formula:
            for con in dis:
                l += 1
        return l

    def set_sat(self, val):
        self.sat = val

    def count_unique_m(self):
        inf = []
        fin = []
        for dis in self.formula:
            for con in dis:
                if con.type == MarkType.Inf and con.num not in inf:
                    inf.append(con.num)
                if con.type == MarkType.Fin and con.num not in fin:
                    fin.append(con.num)
        return len(inf), len(fin)

    def count_total_unique_m(self):
        um = []
        for dis in self.formula:
            for con in dis:
                if con not in um:
                    um.append(con)
        return len(um)

    def max(self):
        m = self.formula[0][0].num
        for dis in self.formula:
            for con in dis:
                if con.num > m:
                    m = con.num
        return m

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

    def clean_up(self, aut, scc):
        clean_f = []
        marks = scc_current_marks(aut, scc)
        for dis in self.formula:
            clean_dis = []
            for con in dis:
                if con.num in marks:
                    clean_dis.append(con)
            if clean_dis:
                clean_f.append(clean_dis)
        self.formula = clean_f
        self.resolve_redundancy()

    def clean_up2(self, scc_sets):
        clean_f = []
        for dis in self.formula:
            clean_dis = []
            add_disj = True
            for con in dis:
                if con.num in scc_sets:
                    clean_dis.append(con)
                else:
                    if con.type == MarkType.Inf:
                        # inf mark not present in scc
                        # whole conjunct is false
                        add_disj = False
            if clean_dis and add_disj:
                clean_f.append(clean_dis)
        self.formula = clean_f
        #self.resolve_redundancy()

    def get_mtype(self, m):
        for dis in self.formula:
            for con in dis:
                if m == con.num:
                    return con.type

    def find_m_dis(self, m):
        occurrences = []
        i = 0
        for dis in self.formula:
            for con in dis:
                if con.num == m:
                    occurrences.append(i)
            i += 1
        return occurrences

    def rem_from_dis(self, index, m):
        new_dis = []
        for con in self.formula[index]:
            if con.num != m:
                new_dis.append(con)
        self.formula[index] = new_dis

    def rem_dis(self, index):
        new_f = []
        i = 0
        for dis in self.formula:
            if i != index:
                new_f.append(dis)
            i += 1
        self.formula = new_f

    def int_list(self):
        alist = []
        for expr in self.formula:
            for one in expr:
                alist.append(one.num)
        return list(dict.fromkeys(alist))


class PACC_CNF:
    """
        class for CNF form of acceptance formula
    """

    def __init__(self, acc):
        self.formula = parse_orig_acc(acc)
        self.sat = None  # satisfied?

    def __str__(self):
        f = []
        for dis in self.formula:
            f.append('(')
            for con in dis:
                f.append(str(con))
                if con is not dis[-1]:
                    f.append(" | ")
            f.append(')')
            if dis is not self.formula[-1]:
                f.append(" & ")
        return ''.join(f)

    def __len__(self):
        return len(self.formula)

    def __getitem__(self, index):
        return self.formula[index]

    def int_format(self):
        f = []
        for dis in self.formula:
            d = []
            for con in dis:
                d.append(con.num)
            f.append(d)
        return f

    def int_list(self):
        alist = []
        for expr in self.formula:
            for one in expr:
                alist.append(one.num)
        return list(dict.fromkeys(alist))

    def max(self):
        m = self.formula[0][0].num
        for expr in self.formula:
            for one in expr:
                if one.num > m:
                    m = one.num
        return m

    def rem_from_expr(self, index, m):
        new_expr = []
        for one in self.formula[index]:
            if one.num != m:
                new_expr.append(one)
        self.formula[index] = new_expr

    def rem_expr(self, index):
        new_f = []
        i = 0
        for dis in self.formula:
            if i != index:
                new_f.append(dis)
            i += 1
        self.formula = new_f

    def resolve_redundancy(self):
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

    def clean_up(self, aut, scc):
        clean_f = []
        marks = scc_current_marks(aut, scc)
        for dis in self.formula:
            clean_dis = []
            for con in dis:
                if con.num in marks:
                    clean_dis.append(con)
            if clean_dis:
                clean_f.append(clean_dis)
        self.formula = clean_f
        self.resolve_redundancy()





def parse_orig_acc(acc):
    """
    parse original acc
    """
    if acc == "":
        return []
    formula = []
    for sub in str(acc).split('&'):
        expr = []
        for one in sub.split('|'):
            mtype = None
            if one.find("Fin") != -1:
                mtype = MarkType.Fin
            else:
                mtype = MarkType.Inf
            num = []
            for c in one:
                if c.isdigit():
                    num.append(c)
            expr.append(ACCMark(mtype, int(''.join(num))))
        formula.append(expr)
    return formula


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
            new_dis.append(ACCMark(mtype, int(''.join(num))))
        formula.append(new_dis)
    return formula


def scc_current_marks(aut, scc):

    # c++ marks_of(scc)
    """Return a list of marks currently present on edges in given scc.

    Arguments:
        aut {spot::twa} -- input automaton
        scc {spot::scc_info_node} -- SCC

    Returns:
        [int] -- list of marks on edges of given scc
    """
    marks = []
    for s in scc.states():
        for e in aut.out(s):
            for m in e.acc.sets():
                if m not in marks:
                    marks.append(int(m))
    return marks
