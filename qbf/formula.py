from qbf.classes import *

### NEW FORMULA ###


def one_inf(clause, acc_set, inner_edges):
    """

    :param clause: num of clause c
    :param acc_set: num off acc set k
    :param edges_count: number of edges in automaton
    :return:
    """
    c = str(clause)
    k = str(acc_set)
    impl = SATformula('->')
    impl.add_subf(SATformula('p_' + c + '_' + k))

    disjunction = SATformula('|')
    for t in inner_edges:
        conj = SATformula('&')
        conj.add_subf(SATformula('e_' + str(t)))
        conj.add_subf(SATformula('f_' + str(t) + '_' + k))

        disjunction.add_subf(conj)
    impl.add_subf(disjunction)
    return impl


def one_fin(clause, acc_set, inner_edges):
    """
        Create formula in shape of :
        n_ck -> (&_1<=t<=T (!f_tk | !e_t)
        Args:
            clause: num of clause
            acc_set: num of acc set
            T: count of all edges
            sequence_num: num of sequence

        Returns:

        """
    c = str(clause)
    k = str(acc_set)
    impl = SATformula('->')
    impl.add_subf(SATformula('n_' + c + '_' + k))

    conjunction = SATformula('&')
    for t in inner_edges:
        disj = SATformula('|')
        disj.add_subf(SATformula('!e_' + str(t)))
        disj.add_subf(SATformula('!f_' + str(t) + '_' + k))

        conjunction.add_subf(disj)
    impl.add_subf(conjunction)
    return impl


def new_formula(inner_edges, C, K):
    """
    Creates requirements for variables for new, short acceptance formula of automaton
    :param inner_edges: all inner edges of SCCs of automaton
    :param C:
    :param K:
    :return:

    """
    clauses_disj = SATformula('|')
    for c in range(1, C + 1):
        sets_conj = SATformula('&')
        for k in range(1, K + 1):
            conj = SATformula('&')
            conj.add_subf(one_inf(c, k, inner_edges))
            conj.add_subf(one_fin(c, k, inner_edges))

            sets_conj.add_subf(conj)
        clauses_disj.add_subf(sets_conj)
    return clauses_disj


### LASO PART OF FORMULA ###

def least_one_edge(inner_edges):
    """

    :param edge_count: Int
    :return: e_1 | e_2| ... e_T
    """
    dis = SATformula("|")
    for i in inner_edges:
        dis.add_subf("e_" + str(i))
    return dis


def disjunct_formula(edges):
    disjunct = SATformula("|")
    for e in edges:
        disjunct.add_subf(SATformula("e_" + (str(e))))
    return disjunct


def in_n_out(scc_state_info):
    """
    Ensures that no cycle has a dead end.
    "If edge goes to cycle it also goes from cycle"
    Args:
        state_state_info [{state num : [[num of edge of which state is a source][num of edge of which state is a destination]]}]

    Returns:

    """

    conjunct = SATformula("&")
    for dict in scc_state_info:
        for src_dst in dict.values():
            src = src_dst[0]
            dst = src_dst[1]
            eq = SATformula("<->")
            eq.add_subf(disjunct_formula(src))
            eq.add_subf(disjunct_formula(dst))
            conjunct.add_subf(eq)
    return conjunct


def disjunct_formula_list(scc_edg):
    """
    Creates list of negated formulas of all edges in SCC
    Args:
        scc_edg:

    Returns:

    """
    alist = []
    for i in scc_edg:
        dis = disjunct_formula(i)
        dis.negate()
        dis.imper()
        alist.append(dis)
    return alist


def one_scc_f(scc_edg):
    """
    Edges that are true are from one SCC, every other edge is false
    Args:
        scc_edg:

    Returns:

    """
    # list of negated formulas disjuncts
    formula_list = disjunct_formula_list(scc_edg)
    dis = SATformula("|")
    for i in range(len(formula_list)):
        con = SATformula("&")
        formula1 = formula_list[i]
        # formula of the scc that is true (double negation)
        formula1.negate()

        for formula in formula_list:
            f = copy.deepcopy(formula)
            con.add_subf(f)
        formula1.negate()
        dis.add_subf(con)
    return dis


# # # QUANTIFIED PART OF FORMULA # # #

def quant_all(edges):
    formula = ""
    for e in edges:
        formula += " # e_" + str(e)
    return formula

"""
def quant_exist(scc_state_info):
    print("tohle se podle me nevyuziva, ne?")
    formula = ""
    for dict in scc_state_info:
        n = 2 ** (ceil(log2(len(dict))))

        for q1 in dict:
            for q2 in dict:
                i = n
                while i >= 1:
                    var_r = "_".join(["r", str(q1), str(q2), str(i)])
                    formula += "?" + var_r + " "
                    i //= 2

    return formula
"""


# # # OLD FORMULA # # #

def old_formula(acc, edge_dict):
    """

        Args:
            acc: Original acceptance condition in DNF
            edge_dict: Dictionary with number of acceptance set : numbers of edges that the acceptance set contains

        Returns: Formula in DNF

        """

    dnf_formula = SATformula('|')
    for dis in acc.formula:
        conjunct_f = SATformula('&')
        for con in dis:
            new_shape = None
            if con.type == MarkType.Inf:
                new_shape = SATformula('|')
                for edge in edge_dict[con.num]:
                    new_shape.add_subf(
                        SATformula(
                            "e_" +
                            str(edge)))
            else:
                new_shape = SATformula('&')
                for edge in edge_dict[con.num]:
                    new_shape.add_subf(
                        SATformula(
                            "!e_" + str(edge)))
            conjunct_f.add_subf(new_shape)
        dnf_formula.add_subf(conjunct_f)

    return dnf_formula


# connection of formula: quantified part . lasso -> (old <-> new)

def laso_f(aut, inner_edges_nums, scc_state_info, scc_edg, inner_edges, mode):
    """
    QBF CONNECTED/SCC
    Formula sais that at least one edge is true and it is infinite
    Args:
        aut:
        inner_edges_nums: [numbers of edges]
        scc_state_info: [{state_num : [[edges state.dst]][edges state.src]}]
        scc_edg:
        inner_edges:

    Returns:

    """
    # QBF SCC

    # edg1 | edg2 | ...
    #least_one = least_one_edge(inner_edges_nums)
    # e1 -> s1 -> e2
    in_out = in_n_out(scc_state_info)
    # edges that are true are in one SCC and none of edges from other SCCs is
    # true
    one_scc = one_scc_f(scc_edg)
    laso = SATformula("&")
    #laso.add_subf(least_one)
    laso.add_subf(in_out)
    laso.add_subf(one_scc)

    # this part makes sure, that the edges are connected tzn QBF CONNECTED
    if mode == 3:
        neg = negate_part(aut, inner_edges)
        laso.add_subf(neg)
    return laso


def equiv_f(old, new):
    eq = SATformula("<->")
    eq.add_subf(old)
    eq.add_subf(new)
    return eq


### final parts of formula ###


def inf_is_not_fin_clause(
        clauses_count,
        acc_sets_count, ):
    """
    Formula in shape of:
    &_1<=c<=C (&_1<=k<=K (!p_ck | !n_ck))
    Args:
        clauses_count:
        acc_sets_count:
        edges_count:
        sequence_num:

    Returns:

    """

    clauses_conj = SATformula('&')
    for c in range(1, clauses_count + 1):
        sets_conj = SATformula('&')
        for k in range(1, acc_sets_count + 1):
            disj = SATformula('|')
            disj.add_subf(SATformula('!p_' + str(c) + '_' + str(k)))
            disj.add_subf(SATformula('!n_' + str(c) + '_' + str(k)))
            sets_conj.add_subf(disj)

        clauses_conj.add_subf(sets_conj)
    return clauses_conj


def inf_or_fin_f(
        clauses_count,
        acc_sets_count, ):
    """
    Formula in shape of:
    &_1<=c<=C (&_1<=k<=K (p_ck | n_ck))
    Args:
        clauses_count:
        acc_sets_count:
        edges_count:
        sequence_num:

    Returns:

    """

    clauses_dis = SATformula('|')
    for c in range(1, clauses_count + 1):
        sets_dis = SATformula('|')
        for k in range(1, acc_sets_count + 1):
            disj = SATformula('|')
            disj.add_subf(SATformula('p_' + str(c) + '_' + str(k)))
            disj.add_subf(SATformula('n_' + str(c) + '_' + str(k)))
            sets_dis.add_subf(disj)

        clauses_dis.add_subf(sets_dis)
    return clauses_dis


def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))

# negation formula auxiliary


def connection(aut, inner_edges):
    con = SATformula("&")
    for e in inner_edges:
        src = e.src
        dst = e.dst
        if src != dst:

            impl = SATformula("->")
            impl.add_subf(SATformula("e_" + str(aut.edge_number(e))))
            eq = SATformula("<->")
            eq.add_subf(SATformula("w_" + str(src)))
            eq.add_subf(SATformula("w_" + str(dst)))
            impl.add_subf(eq)
            con.add_subf(impl)
    if con.is_empty():
        return None
    return con


def positive(aut, inner_edges):
    dis = SATformula("|")
    for e in inner_edges:
        con = SATformula("&")
        con.add_subf(SATformula("e_" + str(aut.edge_number(e))))
        con.add_subf(SATformula("w_" + str(e.src)))
        dis.add_subf(con)
    if dis.is_empty():
        return None
    return dis


def negative(aut, inner_edges):
    dis = SATformula("|")
    for e in inner_edges:
        con = SATformula("&")
        con.add_subf(SATformula("e_" + str(aut.edge_number(e))))
        con.add_subf(SATformula("!w_" + str(e.src)))
        dis.add_subf(con)
    if dis.is_empty():
        return None
    return dis


def negate_part(aut, inner_edges):
    """
    Part of formula that ensures that cycles are connected.
    We say that cycles are disconnected and than we negate it.
    Args:
        aut:
        inner_edges:

    Returns:

    """
    con = SATformula("&")
    connect = connection(aut, inner_edges)
    pos = positive(aut, inner_edges)
    neg = negative(aut, inner_edges)
    if connect:
        con.add_subf(connect)
    if pos:
        con.add_subf(pos)
    if neg:
        con.add_subf(neg)
    con.negate()
    con.imper()
    if not con.is_empty():
        return con
    return None
