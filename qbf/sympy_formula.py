from sympy import *
from qbf.classes import *

# NEW FORMULA

def one_inf_sym(clause, acc_set, inner_edges):
    c = str(clause)
    k = str(acc_set)
    p_char = "p_" + c + "_" + k
    p = symbols(p_char)
    disjunction = False

    for t in inner_edges:
        e_char, f_char = "e_" + str(t), "f_" + str(t) + "_" + k
        e, f = symbols(e_char + "," + f_char)
        conjunction = e & f
        disjunction = disjunction | conjunction
    impl = p >> disjunction
    #print(impl)
    return impl


def one_fin_sym(clause, acc_set, inner_edges):
    c = str(clause)
    k = str(acc_set)
    n_char = "n_" + c + "_" + k
    n = symbols(n_char)

    conjunction = True

    for t in inner_edges:
        e_char, f_char = "!e_" + str(t), "!f_" + str(t) + "_" + k
        e, f = symbols(e_char + "," + f_char)
        disjunction = e | f
        conjunction = conjunction & disjunction
    impl = n >> conjunction
    #print(impl)
    return impl


def new_formula_sym(inner_edges, C, K):

    clauses_disj = False
    for c in range(1, C + 1):
        sets_conj = True
        for k in range(1, K + 1):
            p_n_conj = one_inf_sym(c, k , inner_edges) & one_fin_sym(c, k, inner_edges)
            sets_conj = sets_conj & p_n_conj
        clauses_disj = clauses_disj | sets_conj
    #print(clauses_disj)
    return clauses_disj

# LASO PART OF Formula

def least_one_edge_sym(edges):
    """
    Disjunction of edges variables
    e_1 | 1_2 |... | e_T
    """

    dis = False
    for i in edges:
        e_char = "e_" + str(i)
        e = symbols(e_char)
        dis = dis | e
    return dis

def in_n_out_sym(scc_state_info):
    """
    Ensures that no cycle has a dead end.
    "If edge goes to cycle it also goes from cycle"
    Args:
        state_state_info [{state num : [[num of edge of which state is a source][num of edge of which state is a destination]]}]

    Returns:

    """
    conjunct = True # baze
    for dict in scc_state_info:
        for src_dst in dict.values():
            eq = Equivalent(least_one_edge_sym(src_dst[0]), least_one_edge_sym(src_dst[1]))
            conjunct = conjunct & eq
    return conjunct

def only_one_scc_sym(scc_edg):
    """
    Edges that are true are from one SCC, every other edge is false
    Args:
        scc_edg: [[numbers of edges in one SCC]]
    """
    negated_scc_edges = [Not(least_one_edge_sym(scc)) for scc in scc_edg]
    #print(negated_scc_edges)
    dis = False
    for i in range(len(negated_scc_edges)):
        con = Not(negated_scc_edges[i])
        for j in range(len(negated_scc_edges)):
            if (i != j):
                con = con & negated_scc_edges[j]
        dis = dis | con

    #print(dis)
    return dis

def laso_f_sym(aut, inner_edges_nums, scc_state_info, scc_edg, inner_edges, mode):
    """
    Args:
        aut:
        inner_edges_nums: [numbers of edges]
        scc_state_info: [{state_num : [[edges state.dst]][edges state.src]}]
        scc_edg:
        inner_edges:
    """
    # edg1 | edg2 | ...
    least_one = least_one_edge_sym(inner_edges_nums)

    # (e_1 | e_2) <-> (e_3 | e_4)
    in_out = in_n_out_sym(scc_state_info)

    # only one scc edges
    one_scc = only_one_scc_sym(scc_edg)

    laso = least_one & in_out & one_scc

    return laso
# OLD FORMULA

def old_formula_sym(acc, edge_dict):
    """

        Args:
            acc: Original acceptance condition in DNF
            edge_dict: Dictionary with number of acceptance set : numbers of edges that the acceptance set contains

        Returns: Formula in DNF

    """
    dnf_formula = False
    for dis in acc.formula:
        conjunct_f = True
        for con in dis:
            new_shape = None
            if con.type == MarkType.Inf:
                new_shape = False
                for edge in edge_dict[con.num]:
                    e_char = "e_" + str(edge)
                    e = symbols(e_char)
                    new_shape = new_shape | e
            else:
                new_shape = True
                for edge in edge_dict[con.num]:
                    e_char = "!e_" + str(edge)
                    e = symbols(e_char)
                    new_shape = new_shape & e
            conjunct_f = conjunct_f & new_shape
        dnf_formula = dnf_formula | conjunct_f
    #print(dnf_formula)
    return dnf_formula

def inf_or_fin_sym(C, K):
    con = True
    for c in (1, C+1):
        for k in (1, K + 1):
            print("a")
    return con
