
from telatko2.classes import *
import re

def SAT_output(name, quantified, formula):
    """
    Prints formula into file(for QBF solver) named satfile.
    Args:
        quantified: Universal quantificators of formula
        formula: SATformula - Boolean formula

    Returns:

    """
    f = open(name, "w")
    f.write(str(quantified) + str(formula))
    f.close()


class FormulaCreator:
    """
        Creates formula for QBF solver.
    """

    def __init__(self,  edge_dict, scc_edg, scc_state_info
                  ,inner_edges_nums,C, K, inner_edges
                  , mode, qbf_solver):

        self.edge_dict = edge_dict
        self.scc_edg = scc_edg
        self.scc_state_info = scc_state_info
        self.inner_edges_nums = inner_edges_nums
        self.C = C
        self.K = K
        self.inner_edges = inner_edges
        self.mode = mode # level of simplification
        self.qbf_solver = qbf_solver


# how can I write this more pretty?
class Limboole_f_ctor(FormulaCreator):
    def __init__(self,  edge_dict, scc_edg, scc_state_info
                  ,inner_edges_nums,C, K, inner_edges
                  , mode, qbf_solver):
        super().__init__( edge_dict, scc_edg, scc_state_info
                      ,inner_edges_nums,C, K, inner_edges
                      , mode, qbf_solver)
    def get_qbf_formula(self, aut):
        # quantified edges #e_1 ... #e_n
        quant_edges = quant_all(self.inner_edges_nums)
        # quantified variables ?w_1 ?w_2 ... ?w_n

        # quant_edges += w_quant(aut)
        if self.mode > 2:
            quant_edges += w_quant(aut)

        # edges that are true create continuous cycle of edges aka laso

        if self.mode == 4:
            laso = laso2(aut, self.inner_edges, self.scc_edg)
            in_out = in_n_out(self.scc_state_info)
            laso.add_subf(in_out)
        else:
            laso = laso_f(
                aut,
                self.inner_edges_nums,
                self.scc_state_info,
                self.scc_edg,
                self.inner_edges,
                self.mode)

        # reqiurements on old acceptance formula
        old = old_formula(aut.get_acceptance(), self.edge_dict)

        # assignment of variables to create new acceptance formula
        new = new_formula(self.inner_edges_nums, self.C, self.K)
        # old and new need to be equivalent
        eq = SATformula('<->')
        eq.add_subf(old)
        eq.add_subf(new)

        impl = SATformula("->")
        impl.add_subf(laso)
        impl.add_subf(eq)

        # root of QBFformula
        con = SATformula("&")
        con.add_subf(impl)

        # not (Inf1 & Fin1)
        inf_not_fin = inf_is_not_fin_clause(self.C, self.K)

        # (Fin1 | Inf1) - we need control over formula
        inf_or_fin = inf_or_fin_f(self.C, self.K)
        con.add_subf(inf_not_fin)
        con.add_subf(inf_or_fin)
        SAT_output("sat_file", quant_edges, con)

        # prints our formula into text file
        #SAT_output("sat_file", quant_edges, con)


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





def inf_set_old_formula(edge_dict, set_num):
    new_shape = SATformula('|')
    for edge in edge_dict[set_num]:
        new_shape.add_subf(
            SATformula(
                "e_" +
                str(edge)))
    return new_shape


def fin_set_old_formula(edge_dict, set_num):
    new_shape = SATformula('&')
    for edge in edge_dict[set_num]:
        new_shape.add_subf(
            SATformula(
                "!e_" +
                str(edge)))
    return new_shape


def old_formula(acc, edge_dict):
    """

        Args:
            acc: Original acceptance condition
            edge_dict: Dictionary with number of acceptance set : numbers of edges that the acceptance set contains

        Returns: Formula in DNF

        """

    sets = acc.used_inf_fin_sets()
    inf_sets = list(sets[0].sets())
    fin_sets = list(sets[1].sets())
    formula = str(acc)

    for i in inf_sets:
        reg = r"Inf\(" + str(i) + r"\)"
        formula = re.sub(reg, str(inf_set_old_formula(edge_dict, i)), formula)
    for f in fin_sets:
        reg = r"Fin\(" + str(f) + r"\)"
        formula = re.sub(reg, str(fin_set_old_formula(edge_dict, f)), formula)
    #print(formula)
    return SATformula(formula)


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
    # laso.add_subf(least_one)
    laso.add_subf(in_out)
    laso.add_subf(one_scc)

    # this part makes sure, that the edges are connected tzn QBF CONNECTED
    if mode == 3:
        neg = negate_part(aut, inner_edges, edges_translator)
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
            impl.add_subf(SATformula("e_" +
                                     str(edges_translator[aut.edge_number(e)])))
            eq = SATformula("<->")
            eq.add_subf(SATformula("w_" + str(src)))
            eq.add_subf(SATformula("w_" + str(dst)))
            impl.add_subf(eq)
            con.add_subf(impl)
    if con.is_empty():
        return None
    return con


def positive(aut, inner_edges, edges_translator):
    dis = SATformula("|")
    for e in inner_edges:
        con = SATformula("&")
        con.add_subf(SATformula(
            "e_" + str(edges_translator[aut.edge_number(e)])))
        con.add_subf(SATformula("w_" + str(e.src)))
        dis.add_subf(con)
    if dis.is_empty():
        return None
    return dis


def negative(aut, inner_edges, edges_translator):
    dis = SATformula("|")
    for e in inner_edges:
        con = SATformula("&")
        con.add_subf(SATformula(
            "e_" + str(edges_translator[aut.edge_number(e)])))
        con.add_subf(SATformula("!w_" + str(e.src)))
        dis.add_subf(con)
    if dis.is_empty():
        return None
    return dis


def negate_part(aut, inner_edges, edges_translator):
    """
    Part of formula that ensures that cycles are connected.
    We say that cycles are disconnected and than we negate it.
    Args:
        aut:
        inner_edges:

    Returns:

    """
    con = SATformula("&")
    connect = connection(aut, inner_edges, edges_translator)
    pos = positive(aut, inner_edges, edges_translator)
    neg = negative(aut, inner_edges, edges_translator)
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

def w_quant(aut):
    """
    Creates existential variables w_
    Args:
        aut:

    Returns:

    """
    exist_formula = ""
    num_states = aut.num_states()
    for i in range(num_states):
        exist_formula += "?w_" + str(i)
    return exist_formula


def laso2(aut, inner_edges, scc_edg):
    """
    QBF CYCLES ve statistikach
    Formula that makes sure that the edges are cycles.
    Unluckily the complexity is too high to compute jeden pitomej automat s 12 stavama.
    Args:
        aut:
        inner_edges:
        scc_edg:

    Returns:

    """

    main_dis = SATformula("|")

    con3 = SATformula("&")
    dis1 = SATformula("|")
    dis2 = SATformula("|")
    con1 = SATformula("&")
    con2 = SATformula("&")

    for e in inner_edges:
        src = str(e.src)
        dst = str(e.dst)
        """
        if e.src == e.dst:
            continue
        """

        # part one
        impl = SATformula("->")
        impl.add_subf(SATformula("e_" + str(aut.edge_number(e))))
        c = SATformula("&")
        c.add_subf(SATformula("w_" + src))
        c.add_subf(SATformula("w_" + dst))
        impl.add_subf(c)
        con1.add_subf(impl)

        # part two
        impl2 = SATformula("->")
        impl2.add_subf(SATformula("e_" + str(aut.edge_number(e))))
        c1 = SATformula("&")
        c1.add_subf(SATformula("!w_" + src))
        c1.add_subf(SATformula("!w_" + dst))
        impl2.add_subf(c1)
        con2.add_subf(impl2)

        # part three
        # dis 1
        c2 = SATformula("&")
        c2.add_subf(SATformula("e_" + str(aut.edge_number(e))))
        c2.add_subf(SATformula("w_" + src))
        c2.add_subf(SATformula("!w_" + dst))
        dis1.add_subf(c2)

        # dis 2
        c3 = SATformula("&")
        c3.add_subf(SATformula("e_" + str(aut.edge_number(e))))
        c3.add_subf(SATformula("!w_" + src))
        c3.add_subf(SATformula("w_" + dst))
        dis2.add_subf(c3)

    con3.add_subf(dis1)
    con3.add_subf(dis2)

    main_dis.add_subf(con1)
    main_dis.add_subf(con2)
    main_dis.add_subf(con3)
    laso = SATformula("&")

    one_scc = one_scc_f(scc_edg)
    laso.add_subf(main_dis)
    laso.add_subf(one_scc)
    return laso
