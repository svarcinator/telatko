
import random


from telatko2.merge import *
from telatko2.restore_equivalence import *
import copy


def eval_set(aut, mark, scc, m_all_e):
    if mark.num in m_all_e:
        return mark.type == MarkType.Inf
    if mark.num not in scc_current_marks(aut, scc):  # list of marks dane scc
        return mark.type == MarkType.Fin
    return None


def try_eval(aut, acc, scc):
    m_all_edges = set(scc_everywhere(aut, scc))  # set of marks that include
    # all transitions of SCC

    eval_f = False
    for dis in acc.formula:
        eval_dis = True
        for con in dis:
            val = eval_set(aut, con, scc, m_all_edges)
            if eval_dis is False or val is False:
                eval_dis = False
            elif (eval_dis is None or eval_dis is True) and val is None:
                eval_dis = None
        if eval_dis is True:
            acc.sat = True
            acc.formula = []
            return
        elif (eval_f is None or eval_f is False) and eval_dis is None:
            eval_f = None
    acc.set_sat(eval_f)
    if acc.sat is not None:
        acc.formula = []


def try_eval2(aut, acc, scc, weak):
    if weak:
        if scc.is_rejecting():  # all cycles in scc are rejecting
            # nechapu, pokud weak znamena, ze ma pouze akc. transitions
            acc.set_sat(False)
        else:
            acc.set_sat(True)
        acc.formula = []
        return
    else:
        try_eval(aut, acc, scc)


def print_aut(aut, output, m):
    if output is not None:
        f = open(output, m)
        f.write(aut.to_str() + '\n')
        f.close()
    else:
        print(aut.to_str())

def get_accs(aut):
    """
    Simplifies acceptance condition in DNF for every SCC
    Args:
        aut:

    Returns:[simplified acceptance conditions for scc],[scc]

    """
    accs = []
    sccs = []
    counter = 0
    weak = spot.scc_info(aut).weak_sccs()  # bool if scc is weak
    for scc in spot.scc_info(aut):
        sccs.append(scc)
        acc = PACC(
            aut.get_acceptance().to_dnf())
        try_eval2(aut, acc, scc, weak[counter])
        counter += 1
        if acc.sat is None:
            simplify(aut, acc, scc)
        accs.append(acc)

    return accs, sccs


def check_emptyness(sccs, accs):
    """
    Filters empty accs
    If all of them is empty, returns None, None
    :param sccs:
    :param accs:
    :return: None, None or nempty_sccs, nempty_accs
    """
    nempty_accs = []
    nempty_sccs = []

    for i in range(len(accs)):
        if accs[i].formula:
            nempty_accs.append(accs[i])
            nempty_sccs.append(sccs[i])

    if not nempty_accs:
        return None, None
    return nempty_sccs, nempty_accs


def no_new_acceptance(aut, sccs, accs):
    """
    Solves the situation when new acceptance is []
    :param aut:
    :param sccs:
    :param accs:
    :return:
    """

    if all(acc.sat is True for acc in accs):
        for scc in sccs:
            scc_clean_up_edges(aut, PACC(""), scc)
        aut.set_acceptance(0, spot.acc_code.t())

    elif all(acc.sat is False for acc in accs):
        for scc in sccs:
            scc_clean_up_edges(aut, PACC(""), scc)
        aut.set_acceptance(0, spot.acc_code.f())

    else:
        new_acc = PACC("Inf(0)")
        for i in range(len(accs)):
            if accs[i].sat is True:
                make_true(aut, sccs[i], new_acc)
            else:
                make_false(aut, sccs[i], new_acc)
        aut.set_acceptance(1, spot.acc_code(str(new_acc)))


def get_dependencies(merged_f):
    """

    Args:
        merged_f: base acc condition

    Returns: [int] - list of duplicated acc set numbers in merged_f

    """
    matrix = merged_f.int_format()
    matrix = np.array(matrix)
    u, c = np.unique(matrix, return_counts=True)
    dup = u[c > 1]
    return dup




def process_automaton(aut):
    orig = spot.automaton(aut.to_str())
    spot.cleanup_acceptance_here(aut)
    if aut.get_acceptance().used_sets().count(
    ) < 1 or aut.prop_state_acc() == spot.trival.yes_value:
        return aut

    # simplifies acceptance condition for each scc
    accs, sccs = get_accs(aut) # simplification occurs in here

    # puts acceptance to shorter form(cnf or dnf)
    short_accs = get_short_accs(aut, accs)

    # Filters emty assceptance formulas from short_accs
    nempty_sccs, nempty_short_accs = check_emptyness(sccs, short_accs)

    if not nempty_short_accs:
        # sets acceptance and restores equivalence
        no_new_acceptance(aut, sccs, short_accs)
        return aut
    # sorts accs and sccs - primary key is length(cardinality), secondary key is length of longest disjunct
    acc_quicksort(
        nempty_short_accs,
        nempty_sccs,
        0,
        len(nempty_short_accs) -
        1)
    # stores original acc formula
    orig_acc = PACC_CNF(aut.get_acceptance())

    # highest number of acceptance set in formula
    m = orig_acc.max()

    # disjunct with highest cardinality
    # final acceptance formula for whole automaton to be
    merged_f = copy.deepcopy(nempty_short_accs[0])

    # shift numbers of acceptance sets in future final formula to prevent conflict
    shift_first_acc(merged_f, m)

    # list of numbers of acc sets with more than one occurance
    dependence = get_dependencies(merged_f)

    #[{ACCMark.num : ACCMark.num}]
    list_of_logs = []
    # numbers of dependent acc sets that are not mapped
    # [{index of expr : ACCMark.num}]
    list_of_unmapped_dependencies = []

    for i in range(len(short_accs)):
        if short_accs[i].sat is not None or not short_accs[i].formula:
            # to maintain correspondency of sccs and accs in logs
            list_of_logs.append({})
            list_of_unmapped_dependencies.append({})
            continue

        # linear sum assignment decides what maps on what
        # log{acc_index : merged_f index}
        pairing_log = mergeable(merged_f, short_accs[i])

        # does the heavy lifting - merges it
        list_of_logs.append(
            new_merge(
                aut,
                merged_f,
                short_accs[i],
                pairing_log,
                sccs[i], nempty_sccs[0], dependence, list_of_unmapped_dependencies))

    # make aut equivalent with acceptance formula
    new_make_equiv(aut, short_accs, sccs, list_of_logs, merged_f, list_of_unmapped_dependencies)
    aut.set_acceptance(merged_f.max() + 1, spot.acc_code(str(merged_f)))
    spot.cleanup_acceptance_here(aut)
    if not spot.are_equivalent(aut, orig):
        print("nejsou ekvivalentni - fce playground")
        # precaution
        return orig
    else:
        return aut



def test_aut(a1, a2):
    f = open("summary.txt", "a")
    if spot.are_equivalent(a1, a2):
        if a1.get_acceptance().used_sets().max_set(
        ) < a2.get_acceptance().used_sets().max_set():
            f.write("ok, simplified")
        else:
            f.write("ok, NOT simplified, (" +
                    str(a1.get_acceptance().used_sets()) +
                    ", " +
                    str(a2.get_acceptance().used_sets()) +
                    ')')
    else:
        f.write("nok")
        print_aut(a1, "err_aut.hoa", "a")
    f.write('\n')
    f.close()

