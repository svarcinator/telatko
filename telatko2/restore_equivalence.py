
from telatko2.classes import *
from telatko2.simplify import *
from telatko2.merge import get_set_nums


def make_true(aut, scc, merged_acc):
    scc_clean_up_edges(aut, PACC(""), scc)

    min_inf = len(merged_acc[0])
    cheap_dis = merged_acc[0]
    for dis in merged_acc.formula:
        if all(con.type == MarkType.Fin for con in dis):
            return
        count = 0
        for con in dis:
            if con.type == MarkType.Inf:
                count += 1
        if count < min_inf:
            min_inf = count
            cheap_dis = dis

    add_m = []
    for con in cheap_dis:
        if con.type == MarkType.Inf:
            add_m.append(con.num)

    if not add_m:
        return
    for s in scc.states():
        for e in aut.out(s):
            if e.dst in scc.states():
                for m in add_m:
                    e.acc.set(m)


def make_false(aut, scc, merged_acc):
    scc_clean_up_edges(aut, PACC(""), scc)
    add_m = []
    for dis in merged_acc.formula:
        if all(con.type == MarkType.Fin for con in dis):
            add_m.append(dis[0].num)

    if not add_m:
        return
    for s in scc.states():
        for e in aut.out(s):
            if e.dst in scc.states():
                for m in add_m:
                    e.acc.set(m)


def make_one_true(aut, scc, one):
    """
    Make ACCMark true in particular expression - Inf on every transition
    :param aut:
    :param scc:
    :param one: ACCMark
    :return:
    """
    if one.type == MarkType.Inf:
        for s in scc.states():
            for e in aut.out(s):
                if e.dst in scc.states():
                    e.acc.set(one.num)


def make_one_false(aut, scc, one):
    """
    Make ACCMark true in particular expression - Fin on every transition
    :param aut:
    :param scc:
    :param one: ACCMark
    :return:
    """
    if one.type == MarkType.Fin:
        for s in scc.states():
            for e in aut.out(s):
                if e.dst in scc.states():
                    e.acc.set(one.num)


def make_expr_true(aut, scc, expr):
    """
    Make con/dis true
    jeste pujde vylepsit tak, ze pokud delame v DNF, tak staci jen jeden nebo zadnej
    :param aut:
    :param scc:
    :param expr:
    :return:
    """
    for one in expr:
        make_one_true(aut, scc, one)


def make_expr_false(aut, scc, expr):
    """

    :param aut:
    :param scc:
    :param expr:
    :return:
    """
    for one in expr:
        make_one_false(aut, scc, one)


def restore_cnf(aut, scc, merged_f, unused, dep_log):
    """
    Restores equivalence in CNF mode
    :param aut:
    :param scc:
    :param merged_f: acc formula
    :param unused: ACCMarks that aren't used in this SCC
    :return:
    """
    for i in range(len(merged_f.formula)):
        expr = merged_f.formula[i]
        expr_nums = get_set_nums(expr)    # nums in particular expression
        if all(num in unused for num in expr_nums):
            if any(one.type == MarkType.Fin for one in expr):
                # con is always true, because there is Fin disjunct, which
                # isn't in scc
                continue
            make_expr_true(aut, scc, expr)
        elif i in dep_log.keys() and dep_log[i] in expr_nums:
            for one in expr:
                if one.num in unused:
                    make_one_true(aut, scc, one)

        elif any(num in unused for num in expr_nums):
            for one in expr:

                if one.num in unused:
                    make_one_false(aut, scc, one)


def restore_dnf(aut, scc, merged_f, unused, dep_log):
    """
    Restores equivalence in DNF mode
    :param aut:
    :param scc:
    :param merged_f: acc formula
    :param unused: ACCMarks that aren't used in this SCC
    :return:
    """
    for i in range(len(merged_f.formula)):
        dis = merged_f.formula[i]
        dis_nums = get_set_nums(dis)    # nums in particular expression
        if all(num in unused for num in dis_nums):
            if any(one.type == MarkType.Inf for one in dis):
                # con is always true, because there is Fin disjunct, which
                # isn't in scc
                continue
            make_expr_false(aut, scc, dis)
        elif i in dep_log.keys() and dep_log[i] in dis_nums:

            for one in dis:
                if one.num in unused:
                    # print("nummmm:",one.num)
                    make_one_false(aut, scc, one)
        elif any(num in unused for num in dis_nums):
            #print(scc.states(), merged_f, unused)

            for con in dis:
                # print(con.num)
                if con.num in unused:
                    # print("con",con.num)
                    make_one_true(aut, scc, con)


def restore_maybe_accepting(aut, scc, merged_f, unused, dep_log):
    if aut.get_acceptance().is_cnf():
        restore_cnf(aut, scc, merged_f, unused, dep_log)
    else:
        restore_dnf(aut, scc, merged_f, unused, dep_log)


def restore_always_accepting(aut, scc, merged_f):
    """
    Restores equivalence with new acceptance formula in scc which was originally always accepting
    :param aut:
    :param scc:
    :param merged_f: new acc formula
    :return:
    """
    if aut.get_acceptance().is_cnf():
        for expr in merged_f.formula:
            make_expr_true(aut, scc, expr)
    else:
        # tady se pak bude dat vybirat nejakej vhodnej disjunkt
        make_expr_true(aut, scc, merged_f[0])


def restore_never_accepting(aut, scc, merged_f):
    """
        Restores equivalence with new acceptance formula in scc which was originally never accepting
        :param aut:
        :param scc:
        :param merged_f: new acc formula
        :return:
        """
    if aut.get_acceptance().is_cnf():
        make_expr_false(aut, scc, merged_f.formula[0])
    else:           # dnf
        for expr in merged_f:
            make_expr_false(aut, scc, expr)


def new_make_equiv(aut, accs, sccs, merge_logs, merged_f, depend_logs):
    """
    Makes automata equivalent with the new acceptance formula
    :param aut:
    :param accs:
    :param sccs:
    :param merge_logs: {ACCMark.num, ACCMark.num}  which num of original acc was mapped on new num in merged_f
    :param merged_f: new acceptance formula
    :param depend_logs: new acceptance formula
    :return:
    """
    all_set_nums = merged_f.int_list()  # all acc sets in new_acc
    for i in range(len(accs)):
        scc = sccs[i]
        acc = accs[i]
        m_log = merge_logs[i]
        dep_log = depend_logs[i]
        if acc.sat is True:
            restore_always_accepting(aut, scc, merged_f)
        elif acc.sat is False:
            restore_never_accepting(aut, scc, merged_f)
        else:
            used = []
            unused = []
            for num in all_set_nums:
                if num in m_log.values():
                    used.append(num)
                else:
                    unused.append(num)
            restore_maybe_accepting(aut, scc, merged_f, unused, dep_log)
