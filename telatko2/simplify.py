from telatko2.classes import *


### SIMPLIFY AUXILIARY ###


def scc_clean_up_edges(aut, acc, scc):
    """Removes useless marks from the edges of the given SCC. Useless marks denote transitions of sets that do not appear in the Acc.

    Arguments:
        aut {spot::twa} -- input automaton
        acc {PACC} -- acceptance condition formula
        scc {spot::scc_info_node} -- SCC
    """
    current_m = []
    for dis in acc.formula:
        for con in dis:
            if con.num not in current_m:
                current_m.append(con.num)

    for s in scc.states():
        for e in aut.out(s):
            for m in e.acc.sets():
                if int(m) not in current_m:
                    e.acc.clear(m)


def scc_everywhere(aut, scc):
    """Return a list of acceptance sets that include all transitions in the SCC.

    Arguments:
        aut {spot::twa} -- input automaton
        scc {spot::scc_info_node} -- SCC

    Returns:
        [int] -- list of marks (acceptance sets) that include all transtitions of SCC
    """
    m_all_edges = set(scc_current_marks(aut, scc))
    for s in scc.states():
        for e in aut.out(s):
            if e.dst in scc.states():
                for m in list(m_all_edges):
                    if not m in e.acc.sets():
                        m_all_edges.remove(m)
    return list(m_all_edges)


def scc_compl_sets(aut, scc):
    """Returns a list of tuples. Each tuple contains numbers of acceptance sets m1, m2,
    such that the set of transitions that hold m1 is complementary with the set of transitions
    that hold m2.

    Returns:
        [(int, int))] -- array of tuples of complementary marks in given scc
    """
    compl = []
    marks = scc_current_marks(aut, scc)
    for m1 in marks:
        for m2 in marks:
            if m1 is not m2:
                are_compl = True
                for s in scc.states():
                    for e in aut.out(s):
                        if e.dst in scc.states() and ((m1 in e.acc.sets() and m2 in e.acc.sets()) or (
                                m1 not in e.acc.sets() and m2 not in e.acc.sets())):
                            are_compl = False
                if are_compl and (m1, m2) not in compl and (m2, m1) not in compl:
                    compl.append((m1, m2))
    return compl


def scc_subsets(aut, scc):
    """[summary]

    Arguments:
        aut {spot::twa} -- input automaton
        scc {spot::scc_info_node} -- SCC

    Returns:
        [(int, int)] -- list of tuples that denote complementary sets ? u sure, mi to prijde jako
    """
    marks = scc_current_marks(aut, scc)
    subsets = []
    for m1 in marks:
        for m2 in marks:
            if m1 is not m2:
                is_sub = True
                for s in scc.states():
                    for e in aut.out(s):
                        if e.dst in scc.states() and m2 in e.acc.sets() and not m1 in e.acc.sets():
                            is_sub = False
                if is_sub:
                    subsets.append((m1, m2))
    # print(subsets)
    return subsets


def simpl_inf_con(aut, acc, scc, subsets):
    """If there are acceptance sets X, Y, such that X is a subset of Y, and X, Y always appear
    in the same disjuncts, then remove X.

    Arguments:
        aut {spot::twa} -- input automaton
        acc {PACC} -- acceptance condition formula
        scc {spot::scc_info_node} -- SCC
        subsets {[(int, int)]} -- list if tuples that denote which set includes which
    """
    for sub in subsets:
        if acc.get_mtype(sub[0]) == MarkType.Inf and acc.get_mtype(sub[1]) == MarkType.Inf:
            sub_i = acc.find_m_dis(sub[1])
            super_i = acc.find_m_dis(sub[0])
            if (all(i in sub_i for i in super_i)):
                for index in reversed(super_i):
                    acc.rem_from_dis(index, sub[0])
                scc_clean_up_edges(aut, acc, scc)
                simpl_inf_con(aut, acc, scc, scc_subsets(aut, scc))
                return


def simpl_fin_same_dis(aut, acc, scc):
    fins = []
    for dis in acc.formula:
        for con in dis:
            if con.type == MarkType.Fin:
                fins.append(con)

    for fin1 in fins:
        for fin2 in fins:
            if fin1 is not fin2:
                merge = True
                for dis in acc.formula:
                    if (fin1 not in dis and fin2 in dis) or (fin2 not in dis and fin1 in dis):
                        merge = False
                if merge:
                    add_dupl_marks(aut, scc, fin2.num, fin1.num)
                    acc.clean_up(aut, scc)
                    return


def simpl_fin_con_subsets(aut, acc, scc, subsets):
    for sub in subsets:
        if acc.get_mtype(sub[0]) == MarkType.Fin and acc.get_mtype(sub[1]) == MarkType.Fin:
            sub_i = acc.find_m_dis(sub[1])
            super_i = acc.find_m_dis(sub[0])
            if (all(i in super_i for i in sub_i)):
                for index in sub_i:
                    acc.rem_from_dis(index, sub[1])
                scc_clean_up_edges(aut, acc, scc)
                acc.clean_up(aut, scc)
                simpl_fin_con_subsets(aut, acc, scc, scc_subsets(aut, scc))
                return
            else:
                for i in reversed(sub_i):
                    if i in super_i:
                        acc.rem_from_dis(i, sub[1])
                        acc.clean_up(aut, scc)


def simpl_co_con(aut, acc, scc, compl_sets):
    for co in compl_sets:
        if acc.get_mtype(co[0]) != acc.get_mtype(co[1]):
            inf, fin = co[0], co[1]
            if (acc.get_mtype(co[0]) == MarkType.Fin):
                inf, fin = co[1], co[0]
            inf_i = acc.find_m_dis(inf)
            fin_i = acc.find_m_dis(fin)
            if all(i in fin_i for i in inf_i):
                for index in reversed(inf_i):
                    acc.rem_from_dis(index, inf)

                scc_clean_up_edges(aut, acc, scc)
                simpl_co_con(aut, acc, scc, scc_compl_sets(aut, scc))
                return
            else:
                for i in inf_i:
                    if i in fin_i:
                        acc.rem_from_dis(i, inf)
                acc.clean_up(aut, scc)


# check if inf marks are placed on all edges that do not have fin mark
def check_implies_marks(aut, scc, fin, inf):
    for s in scc.states():
        for e in aut.out(s):
            if e.dst in scc.states() and not inf in e.acc.sets() and not fin in e.acc.sets():
                return False
    return True


# (Fin AND Inf), situations where: 'if Fin true then Inf true'; Inf can be removed
def simpl_fin_implies_inf(aut, acc, scc):
    for i in range(0, len(acc)):
        infs = []
        for con in acc[i]:
            if con.type == MarkType.Inf:
                infs.append(con)
        if not infs:
            return
        for con in acc[i]:
            if con.type == MarkType.Fin:
                for inf in infs:
                    if check_implies_marks(aut, scc, con.num, inf.num):
                        acc.rem_from_dis(i, inf.num)
                        scc_clean_up_edges(aut, acc, scc)
                        simpl_fin_implies_inf(aut, acc, scc)
                        return


def simpl_substitute(aut, acc, scc):
    current = scc_current_marks(aut, scc)  # list of marks dane scc
    everywhere = scc_everywhere(aut, scc)  # set of marks thaht include
    # all transitons of SCC
    # print("acc v simpl sub", scc.states(), acc, current, everywhere)
    rem_d = []  # disjunkty k odstraneni
    for i in range(len(acc)):
        for con in acc[i]:
            if (con.num in everywhere and con.type == MarkType.Fin) or \
                    (con.num not in current and con.type == MarkType.Inf):
                if i not in rem_d:
                    rem_d.append(i)
            elif con.num in everywhere and con.type == MarkType.Inf:
                acc.rem_from_dis(i, con.num)  # odstrani vzdy pravdivy konj z disj
            elif con.num not in current and con.type == MarkType.Fin:
                acc.rem_from_dis(i, con.num)  # odstrani vzdy pravdivy konj z disj
    # print("disj k odstr:" ,rem_d, acc)

    for index in reversed(rem_d):
        acc.rem_dis(index)
    acc.clean_up(aut, scc)


def simpl_false_subsets(aut, acc, subsets, scc):
    for sub in subsets:
        if acc.get_mtype(sub[0]) == MarkType.Fin and acc.get_mtype(sub[1]) == MarkType.Inf:
            sub_i = acc.find_m_dis(sub[1])
            super_i = acc.find_m_dis(sub[0])
            for i in sub_i:
                if i in super_i:
                    acc.rem_dis(i)
                    scc_clean_up_edges(aut, acc, scc)
                    simpl_false_subsets(aut, acc, scc_subsets(aut, scc), scc)
                    return


def simpl_false_fin(aut, acc, scc):
    rem_dis = []
    for i in range(len(acc)):
        current_fins = []
        for con in acc[i]:
            if con.type == MarkType.Fin:
                current_fins.append(con.num)
        current_dis = True
        for s in scc.states():
            for e in aut.out(s):
                if e.dst in scc.states() and all(m not in e.acc.sets() for m in current_fins):
                    current_dis = False
        if current_dis:
            rem_dis.append(i)
    for index in reversed(rem_dis):
        acc.rem_dis(index)


### SIMPLIFY ###

def simplify(aut, acc, scc):
    acc_l = acc.count_total_unique_m()  # pocet unikatnich konjunktu v cele akc. podm
    # remove always false disjuncts
    # a taky odstarni vzdy pravdivy konj z nekterych disjunktu
    # print(1, scc.states(), str(acc), acc_l)
    simpl_substitute(aut, acc, scc)
    # print(2,scc.states(),str(acc), acc_l)
    simpl_false_subsets(aut, acc, scc_subsets(aut, scc), scc)
    # print(3, scc.states(),str(acc), acc_l)
    simpl_false_fin(aut, acc, scc)
    # print(4, scc.states(),str(acc), acc_l)

    # simplify inclusion mark sets
    simpl_inf_con(aut, acc, scc, scc_subsets(aut, scc))
    # print(5,scc.states(), str(acc), acc_l)
    simpl_fin_con_subsets(aut, acc, scc, scc_subsets(aut, scc))
    # print(6, scc.states(),str(acc), acc_l)
    simpl_fin_same_dis(aut, acc, scc)
    # print(7,scc.states(), str(acc), acc_l)
    # simplify complementary marks
    simpl_co_con(aut, acc, scc, scc_compl_sets(aut, scc))
    # print(8, scc.states(),str(acc), acc_l)
    # simplify disjuncts where (Fin = True) => (Inf = True)
    simpl_fin_implies_inf(aut, acc, scc)
    # print(9, scc.states(),str(acc), acc_l)
    scc_clean_up_edges(aut, acc, scc)
    acc.clean_up(aut, scc)
    if acc_l > acc.count_total_unique_m():
        simplify(aut, acc, scc)


def add_dupl_marks(aut, scc, origin_m, new_m):
    for s in scc.states():
        for e in aut.out(s):
            if e.dst in scc.states() and origin_m in e.acc.sets():
                if not new_m in e.acc.sets():
                    e.acc.set(new_m)