
from telatko2.classes import *
from qbf.formula import *
import copy

def get_mark_edg( aut, edges, edges_translator):
    """
        Returns: dictionary {acc_mark : [real_edge_numbers]}
    """
    dict = {}
    counter = 1
    for e in edges:
        edges_translator[aut.edge_number(e)] = counter
        for m in e.acc.sets():
            if m in dict:
                dict[m].append(aut.edge_number(e))
            else:
                dict[m] = [aut.edge_number(e)]
        counter += 1
    return  dict

def one_fin2(clause, acc_set, edges_translator):
    """
        Create formula in shape of :
        n_ck -> (&_1<=t<=T (!f_tk | !e_t)
        Args:
            clause: num of clause
            acc_set: num of acc set


        Returns:

        """
    c = str(clause)
    k = str(acc_set)
    impl = SATformula('->')
    impl.add_subf(SATformula('n_' + c + '_' + k))

    conjunction = SATformula('&')
    for t in edges_translator:
        disj = SATformula('|')
        disj.add_subf(SATformula('!e_' + str(edges_translator[t])))
        disj.add_subf(SATformula('!f_' + str(t) + '_' + k))

        conjunction.add_subf(disj)
    impl.add_subf(conjunction)
    return impl

def one_inf2(clause, acc_set, edges_translator):
    """

    :param clause: num of clause c
    :param acc_set: num off acc set k
    :param edges_translator: {num_of_edge_in_aut : num_of_edge_in_SATformula}

    :return:
    """


    c = str(clause)
    k = str(acc_set)
    impl = SATformula('->')
    impl.add_subf(SATformula('p_' + c + '_' + k))

    disjunction = SATformula('|')
    for t in edges_translator:
        conj = SATformula('&')
        conj.add_subf(SATformula('e_' + str(edges_translator[t])))
        conj.add_subf(SATformula('f_' + str(t) + '_' + k))

        disjunction.add_subf(conj)
    impl.add_subf(disjunction)
    return impl


def new_formula2(edges_translator, C, K):
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
            conj.add_subf(one_inf2(c, k, edges_translator))
            conj.add_subf(one_fin2(c, k, edges_translator))

            sets_conj.add_subf(conj)
        clauses_disj.add_subf(sets_conj)
    return clauses_disj

def least_one_edge2(T_max):
    f = SATformula("|")
    for i in range(1, T_max + 1):
        f.add_subf("e_" + str(i))
    return f

def get_key(my_dict, val):
    for key, value in my_dict.items():
        if val == value:
            return key

def disjunct_formula2(edges, edge_translator):
    disjunct = SATformula("|")
    for e in edges:
        disjunct.add_subf(SATformula("e_" + (str(edge_translator[e]))))
    return disjunct

def in_n_out2(scc_info, edge_translator):

    conjunct = SATformula("&")
    for src_dst in scc_info.values():
        src = src_dst[0]
        dst = src_dst[1]
        eq = SATformula("<->")
        #print(edge_translator)
        eq.add_subf(disjunct_formula2(src, edge_translator))
        eq.add_subf(disjunct_formula2(dst, edge_translator))
        conjunct.add_subf(eq)

    return conjunct

def count_edges(edges):
    counter = 0
    for e in edges:
        counter += 1
    return counter

def laso_part(scc_info, edge_translator, L, inner_edges, aut, max_T):
    laso = SATformula("&")
    in_out = in_n_out2(scc_info, edge_translator)
    least_one = least_one_edge2(count_edges(inner_edges))
    laso.add_subf(least_one)
    laso.add_subf(in_out)
    if L == 3:
        #laso.add_subf(in_out)
        neg = negate_part2(aut, inner_edges, edge_translator)
        laso.add_subf(neg)
        return laso

    return laso

def quantify_e(T):
    formula = ""
    for i in range(1, T + 1):
        formula += "# e_" + str(i)
    return formula




def old_formula2(acc, edge_dict, edge_translator, scc_sets, aut, scc):
    """

        Args:
            acc: Original acceptance condition in DNF
            edge_dict: Dictionary with number of acceptance set : numbers of edges that the acceptance set contains

        Returns: Formula in DNF

        """
    #print("acc: ", acc)
    #print("scc sets:", scc_sets)
    tmp_acc = copy.deepcopy(acc)


    tmp_acc.clean_up2(list(scc_sets.sets()))


    #print("cleaned acc: ", tmp_acc)
    dnf_formula = SATformula('|')
    for dis in tmp_acc.formula:
        conjunct_f = SATformula('&')
        for con in dis:
            new_shape = None

            if con.type == MarkType.Inf:
                new_shape = SATformula('|')

                for edge in edge_dict[con.num]:
                    new_shape.add_subf(
                        SATformula(
                            "e_" +
                            str(edge_translator[edge])))
            else:
                #print("con num:", con.num)
                #print(edge_dict)
                new_shape = SATformula('&')
                for edge in edge_dict[con.num]:
                    new_shape.add_subf(
                        SATformula(
                            "!e_" + str(edge_translator[edge])))
            # bude tu problem pokud nekde bude pouze samotnej log operator
            conjunct_f.add_subf(new_shape)

        dnf_formula.add_subf(conjunct_f)
    #print("dnf formula:  ",dnf_formula)

    return dnf_formula

def least_one(T):
    f = SATformula("|")
    for i in range(1, T+1):
        f.add_subf("e_" + str(i))
    return f

def w_quant2(aut, max_states):
    """
    Creates universal variables w_
    Args:
        aut:

    Returns:

    """
    univ_formula = ""
    for i in range(max_states):
        univ_formula += "?w_" + str(i)
    return univ_formula


def connection2(aut, inner_edges, edge_translator):
    con = SATformula("&")
    for e in inner_edges:
        src = e.src
        dst = e.dst
        if src != dst:

            impl = SATformula("->")
            impl.add_subf(SATformula("e_" + str(edge_translator[aut.edge_number(e)])))
            eq = SATformula("<->")
            eq.add_subf(SATformula("w_" + str(src)))
            eq.add_subf(SATformula("w_" + str(dst)))
            impl.add_subf(eq)
            con.add_subf(impl)
    if con.is_empty():
        return None
    return con


def positive2(aut, inner_edges, edge_translator):
    dis = SATformula("|")
    for e in inner_edges:
        con = SATformula("&")
        con.add_subf(SATformula("e_" + str(edge_translator[aut.edge_number(e)])))
        con.add_subf(SATformula("w_" + str(e.src)))
        dis.add_subf(con)
    if dis.is_empty():
        return None
    return dis


def negative2(aut, inner_edges, edge_translator):
    dis = SATformula("|")
    for e in inner_edges:
        con = SATformula("&")
        con.add_subf(SATformula("e_" + str(edge_translator[aut.edge_number(e)])))
        con.add_subf(SATformula("!w_" + str(e.src)))
        dis.add_subf(con)
    if dis.is_empty():
        return None
    return dis


def negate_part2(aut, inner_edges, edge_translator):
    """
    Part of formula that ensures that cycles are connected.
    We say that cycles are disconnected and than we negate it.
    Args:
        aut:
        inner_edges:

    Returns:

    """
    con = SATformula("&")
    connect = connection2(aut, inner_edges, edge_translator)
    pos = positive2(aut, inner_edges, edge_translator)
    neg = negative2(aut, inner_edges, edge_translator)
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

def laso22(aut, inner_edges, scc_info, edge_translator):
    """
    QBF CYCLES ve statistikach
    Formula that makes sure that the edges are cycles.

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
        impl.add_subf(SATformula("e_" + str(edge_translator[aut.edge_number(e)])))
        c = SATformula("&")
        c.add_subf(SATformula("w_" + src))
        c.add_subf(SATformula("w_" + dst))
        impl.add_subf(c)
        con1.add_subf(impl)

        # part two
        impl2 = SATformula("->")
        impl2.add_subf(SATformula("e_" + str(edge_translator[aut.edge_number(e)])))
        c1 = SATformula("&")
        c1.add_subf(SATformula("!w_" + src))
        c1.add_subf(SATformula("!w_" + dst))
        impl2.add_subf(c1)
        con2.add_subf(impl2)

        # part three
        # dis 1
        c2 = SATformula("&")
        c2.add_subf(SATformula("e_" + str(edge_translator[aut.edge_number(e)])))
        c2.add_subf(SATformula("w_" + src))
        c2.add_subf(SATformula("!w_" + dst))
        dis1.add_subf(c2)

        # dis 2
        c3 = SATformula("&")
        c3.add_subf(SATformula("e_" + str(edge_translator[aut.edge_number(e)])))
        c3.add_subf(SATformula("!w_" + src))
        c3.add_subf(SATformula("w_" + dst))
        dis2.add_subf(c3)

    con3.add_subf(dis1)
    con3.add_subf(dis2)

    main_dis.add_subf(con1)
    main_dis.add_subf(con2)
    main_dis.add_subf(con3)
    laso = SATformula("&")

    #one_scc = one_scc_f(scc_edg)
    laso.add_subf(main_dis)
    laso.add_subf(in_n_out2(scc_info, edge_translator))
    return laso
