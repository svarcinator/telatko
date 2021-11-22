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



def scc_compl_sets(aut,scc, scc_index):
    """Returns a list of tuples. Each tuple contains numbers of acceptance sets m1, m2,
    such that the set of transitions that hold m1 is complementary with the set of transitions
    that hold m2.

    Returns:
        [(int, int))] -- array of tuples of complementary marks in given scc
    """
    compl = []
    marks = scc.acc_marks().sets()
    for m1 in marks:
        for m2 in marks:
            if m1 is not m2:
                are_compl = True
                for s in scc.states():
                    for e in aut.out(s):
                        if e.dst in scc.states() and (
                            (m1 in e.acc.sets() and m2 in e.acc.sets()) or (
                                m1 not in e.acc.sets() and m2 not in e.acc.sets())):
                            are_compl = False
                if are_compl and (
                        m1, m2) not in compl and (
                        m2, m1) not in compl:
                    compl.append((m1, m2))
    return compl


def scc_subsets(aut, scc, scc_index):
    """[summary]

    Arguments:
        aut {spot::twa} -- input automaton
        scc {spot::scc_info_node} -- SCC

    Returns:
        [(int, int)] -- list of tuples that denote complementary sets ? u sure, mi to prijde jako
    """
    marks = scc.acc_marks().sets()
    subsets = []
    for m1 in marks:
        for m2 in marks:
            if m1 is not m2:
                is_sub = True
                for s in scc.states():
                    for e in aut.out(s):
                        if e.dst in scc.states() and m2 in e.acc.sets() and m1 not in e.acc.sets():
                            is_sub = False
                            break
                        if not is_sub:
                            break
                if is_sub:
                    subsets.append((m1, m2))
    return subsets

def removed_relation_set(relation_set, m):
    return set(filter(lambda x: (x[0] == m or x[1] == m), relation_set))

def cnf_inf_dis(aut, acc, scc, subsets):
    """

    Inf(X) ⫅ Inf (Y) -> Inf(X)

    Arguments:
        aut {spot::twa} -- input automaton
        acc {PACC} -- acceptance condition formula
        scc {spot::scc_info_node} -- SCC
        subsets {[(int, int)]} -- list if tuples that denote which set includes which
    """
    removed_relations = set()
    for sub in subsets:
        if sub in removed_relations:
            continue;
        if acc.get_mtype(
                sub[0]) == MarkType.Inf and acc.get_mtype(
                sub[1]) == MarkType.Inf:
            sub_i = acc.find_m_dis(sub[1])
            super_i = acc.find_m_dis(sub[0])

            if (all(i in super_i for i in sub_i)):

                for index in reversed(sub_i):

                    acc.rem_from_expr(index, sub[1])

                scc_clean_up_edges(aut, acc, scc)
                #cnf_inf_dis(aut, acc, scc, scc_subsets(aut, scc, acc.scc_index))
                #return
                removed_relations = set.union(removed_relations,  removed_relation_set(subsets, sub[1]))
    subsets = [elem for elem in subsets if elem not in removed_relations]

def dnf_inf_con(aut, acc, scc, subsets):
    """If there are acceptance sets X, Y, such that X is a subset of Y, and X, Y always appear
    in the same disjuncts, then remove X.

    Inf(X) ⫅ Inf (Y) -> Inf(X)

    Arguments:
        aut {spot::twa} -- input automaton
        acc {PACC} -- acceptance condition formula
        scc {spot::scc_info_node} -- SCC
        subsets {[(int, int)]} -- list if tuples that denote which set includes which
    """
    removed_relations = set()
    for sub in subsets:
        if sub in removed_relations:
            continue;
        if acc.get_mtype(
                sub[0]) == MarkType.Inf and acc.get_mtype(
                sub[1]) == MarkType.Inf:
            sub_i = acc.find_m_dis(sub[1])
            super_i = acc.find_m_dis(sub[0])
            if (all(i in sub_i for i in super_i)):
                for index in reversed(super_i):
                    acc.rem_from_expr(index, sub[0])
                scc_clean_up_edges(aut, acc, scc)
                #dnf_inf_con(aut, acc, scc, scc_subsets(aut, scc, acc.scc_index))
                #return
                removed_relations = set.union(removed_relations,  removed_relation_set(subsets, sub[0]))
    subsets = [elem for elem in subsets if elem not in removed_relations]


def fin_same_dis(aut, acc, scc):
    """
    Fin(X), Fin (Y) in same disjunct -> Fin(Z) = Fin(X) ∪ Fin(Y)
    """
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
                    if (fin1 not in dis and fin2 in dis) or (
                            fin2 not in dis and fin1 in dis):
                        merge = False
                if merge:
                    add_dupl_marks(aut, scc, fin2.num, fin1.num)
                    acc.clean_up(aut, scc)
                    return

def inf_same_con(aut, acc, scc):
    """
    Inf(X), Inf(Y) in same conjunct -> Inf(Z) = Inf(X) ∪ Inf(Y)
    """

    infs = []
    for con in acc.formula:
        for dis in con:
            if dis.type == MarkType.Inf:
                infs.append(dis)

    for inf1 in infs:
        for inf2 in infs:
            if inf1 != inf2:
                merge = True
                for con in acc.formula:
                    if (inf1 not in con and inf2 in con) or (
                            inf2 not in con and inf1 in con):
                        merge = False
                if merge:

                    add_dupl_marks(aut, scc, inf2.num, inf1.num)
                    acc.clean_up(aut, scc)
                    return


def cnf_fin_subsets(aut, acc, scc, subsets):
    """
    Fin(X) ⫅ Fin (Y) -> Fin(X)
    """
    removed_relations = set()
    for sub in subsets:
        if sub in removed_relations:
            continue;
        if acc.get_mtype(
                sub[0]) == MarkType.Fin and acc.get_mtype(
                sub[1]) == MarkType.Fin:
            sub_i = acc.find_m_dis(sub[1])
            super_i = acc.find_m_dis(sub[0])
            if (all(i in sub_i for i in super_i)):
                for index in super_i:
                    acc.rem_from_expr(index, sub[0])
                scc_clean_up_edges(aut, acc, scc)
                acc.clean_up(aut, scc)
                #cnf_fin_subsets(aut, acc, scc, scc_subsets(aut, scc, acc.scc_index))
                #return
                removed_relations = set.union(removed_relations,  removed_relation_set(subsets, sub[0]))
            else:
                for i in reversed(super_i):
                    if i in sub_i:
                        acc.rem_from_expr(i, sub[0])
                        acc.clean_up(aut, scc)
    subsets = [elem for elem in subsets if elem not in removed_relations]


def dnf_fin_subsets(aut, acc, scc, subsets):
    """
    Fin(X) ⫅ Fin (Y) -> Fin(Y)
    """
    removed_relations = set()
    for sub in subsets:
        if sub in removed_relations:
            continue;
        if acc.get_mtype(
                sub[0]) == MarkType.Fin and acc.get_mtype(
                sub[1]) == MarkType.Fin:
            sub_i = acc.find_m_dis(sub[1])
            super_i = acc.find_m_dis(sub[0])
            if (all(i in super_i for i in sub_i)):
                for index in sub_i:
                    acc.rem_from_expr(index, sub[1])
                scc_clean_up_edges(aut, acc, scc)
                acc.clean_up(aut, scc)
                #dnf_fin_subsets(aut, acc, scc, scc_subsets(aut, scc, acc.scc_index))
                #return
                removed_relations = set.union(removed_relations,  removed_relation_set(subsets, sub[1]))

            else:
                for i in reversed(sub_i):
                    if i in super_i:
                        acc.rem_from_expr(i, sub[1])
                        acc.clean_up(aut, scc)
    subsets = [elem for elem in subsets if elem not in removed_relations]



def cnf_co_dis(aut, acc, scc, compl_sets):
    """
    Complementary sets Inf(i) and Fin(j), remove Inf(i)
    """
    for co in compl_sets:
        if acc.get_mtype(co[0]) != acc.get_mtype(co[1]):
            inf, fin = co[0], co[1]
            if (acc.get_mtype(co[0]) == MarkType.Fin):
                inf, fin = co[1], co[0]
            inf_i = acc.find_m_dis(inf) # [index of disjunct with acc set m]
            fin_i = acc.find_m_dis(fin) # [index of disjunct with acc set m]
            if all(i in fin_i for i in inf_i):
                # nachazi se ve stejnych disjunktech (expressions)
                for index in reversed(fin_i):
                    # inf i se odstrani ze vsech expressions
                    acc.rem_from_expr(index, fin)

                scc_clean_up_edges(aut, acc, scc)
                cnf_co_dis(aut, acc, scc, scc_compl_sets(aut, scc, acc.scc_index))
                return
            else:
                for i in fin_i:
                    if i in inf_i:
                        acc.rem_from_expr(i, fin)
                acc.clean_up(aut, scc)

def dnf_co_con(aut, acc, scc, compl_sets):
    """
    Complementary sets Inf(i) and Fin(j), remove Inf(i)
    """
    for co in compl_sets:
        if acc.get_mtype(co[0]) != acc.get_mtype(co[1]):
            inf, fin = co[0], co[1]
            if (acc.get_mtype(co[0]) == MarkType.Fin):
                inf, fin = co[1], co[0]
            inf_i = acc.find_m_dis(inf) # [index of disjunct with acc set m]
            fin_i = acc.find_m_dis(fin) # [index of disjunct with acc set m]
            if all(i in fin_i for i in inf_i):
                # nachazi se ve stejnych disjunktech (expressions)
                for index in reversed(inf_i):
                    # inf i se odstrani ze vsech expressions
                    acc.rem_from_expr(index, inf)

                scc_clean_up_edges(aut, acc, scc)
                dnf_co_con(aut, acc, scc, scc_compl_sets(aut, scc, acc.scc_index))
                return
            else:
                for i in inf_i:
                    if i in fin_i:
                        acc.rem_from_expr(i, inf)
                acc.clean_up(aut, scc)


# check if inf marks are placed on all edges that do not have fin mark
def check_implies_marks(aut, scc, fin, inf):
    for s in scc.states():
        for e in aut.out(s):
            if e.dst in scc.states() and inf not in e.acc.sets() and fin not in e.acc.sets():
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

                        acc.rem_from_expr(i, inf.num)
                        scc_clean_up_edges(aut, acc, scc)
                        simpl_fin_implies_inf(aut, acc, scc)
                        return




def simpl_substitute(aut, acc, scc, scc_index):
    acc.initial_cleanup(aut, scc)

    """
    current = scc_current_marks(aut, scc_index)  # list of marks dane scc
    everywhere = scc_everywhere(aut, scc_index)  # set of marks thaht include
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
                # odstrani vzdy pravdivy konj z disj
                acc.rem_from_expr(i, con.num)
            elif con.num not in current and con.type == MarkType.Fin:
                # odstrani vzdy pravdivy konj z disj
                acc.rem_from_expr(i, con.num)

    for index in reversed(rem_d):
        acc.rem_expr(index)
    acc.clean_up(aut, scc)
    acc.resolve_redundancy()
    """


def simpl_true_subsets(aut, acc, subsets, scc):
    """
    Fin(X) ⊆ Inf(Y) -> whole expression (conjunct) is True
    """
    removed_relations = set()
    for sub in subsets:
        if sub in removed_relations:
            continue;
        if acc.get_mtype(
                sub[0]) == MarkType.Inf and acc.get_mtype(
                sub[1]) == MarkType.Fin:
            sub_i = acc.find_m_dis(sub[1])
            super_i = acc.find_m_dis(sub[0])
            for i in sub_i:
                if i in super_i:
                    acc.rem_expr(i)
                    scc_clean_up_edges(aut, acc, scc)
                    #simpl_true_subsets(aut, acc, scc_subsets(aut, scc, acc.scc_index), scc)
                    #return
                    removed_relations = set.union(removed_relations,  removed_relation_set(subsets, sub[1]))
    subsets = [elem for elem in subsets if elem not in removed_relations]


def simpl_false_subsets(aut, acc, subsets, scc):
    """
    Inf(X) ⊆ Fin(Y) -> whole expression (disjunct) is False
    """
    removed_relations = set()
    for sub in subsets:
        if sub in removed_relations:
            continue;
        if acc.get_mtype(
                sub[0]) == MarkType.Fin and acc.get_mtype(
                sub[1]) == MarkType.Inf:
            sub_i = acc.find_m_dis(sub[1])
            super_i = acc.find_m_dis(sub[0])
            for i in sub_i:
                if i in super_i:
                    acc.rem_expr(i)
                    scc_clean_up_edges(aut, acc, scc)
                    #simpl_false_subsets(aut, acc, scc_subsets(aut, scc, acc.scc_index), scc)
                    #return
                    removed_relations = set.union(removed_relations,  removed_relation_set(subsets, sub[1]))
    subsets = [elem for elem in subsets if elem not in removed_relations]



def simpl_false_fin(aut, acc, scc):
    """
    D = (.. & Fin(X) & ..), X is not on any edge of scc -> whole D is true
    Dealt with in `simplify.simpl_substitute`
    """
    rem_dis = []
    for i in range(len(acc)):
        current_fins = []
        for con in acc[i]:
            if con.type == MarkType.Fin:
                current_fins.append(con.num)
        current_dis = True
        for s in scc.states():
            for e in aut.out(s):
                if e.dst in scc.states() and all(m not in e.acc.sets()
                                                 for m in current_fins):
                    current_dis = False
        if current_dis:
            rem_dis.append(i)
    for index in reversed(rem_dis):
        acc.rem_expr(index)


### SIMPLIFY ###

def simplify(aut, acc, scc, scc_index, acc_type):
    #print("------simplify-----------------")
    orig = spot.automaton(aut.to_str())
    acc_l = acc.count_total_unique_m()
    while True:

        #do while simplification fix point is not reached

        # remove always false disjuncts
        simpl_substitute(aut, acc, scc, scc_index)


        if acc_type == AccType.dnf:
            fin_same_dis(aut, acc, scc)
            # simplify complementary marks
            dnf_co_con(aut, acc, scc, scc_compl_sets(aut, scc, scc_index))


            subsets = scc_subsets(aut, scc, scc_index)
            simpl_false_subsets(aut, acc, subsets, scc)

            dnf_inf_con(aut, acc, scc, subsets)

            dnf_fin_subsets(aut, acc, scc, subsets)


            # simplify disjuncts where (Fin = True) => (Inf = True)
            # this is complement, init?
            # simpl_fin_implies_inf(aut, acc, scc)

        else:

            inf_same_con(aut, acc, scc)
            # simplify complementary marks
            cnf_co_dis(aut, acc, scc, scc_compl_sets(aut, scc, scc_index))

            subsets = scc_subsets(aut, scc, scc_index)
            simpl_true_subsets(aut, acc, subsets, scc)

            cnf_inf_dis(aut, acc, scc, subsets)
            cnf_fin_subsets(aut, acc, scc, subsets)


        #simpl_false_fin(aut, acc, scc)
        simpl_substitute(aut, acc, scc, scc_index)


        scc_clean_up_edges(aut, acc, scc)
        acc.clean_up(aut, scc)
        #print(acc)

        unique_m = acc.count_total_unique_m()
        if acc_l == unique_m:
            break
        else:
            acc_l = unique_m



def add_dupl_marks(aut, scc, origin_m, new_m):
    for s in scc.states():
        for e in aut.out(s):
            if e.dst in scc.states() and origin_m in e.acc.sets():
                if new_m not in e.acc.sets():
                    e.acc.set(new_m)
