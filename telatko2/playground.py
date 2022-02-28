
import random


from telatko2.merge import *
from telatko2.restore_equivalence import *
import copy
from qbf.parser import clear_aut_edges


def try_eval(aut, acc, scc):
    """

    """
    m_all_edges = set(scc_everywhere(aut, scc))  # set of marks that include
    # all transitions of SCC

    eval_f = False  # proc
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


def weak_eval(aut, acc, scc, weak):
    if weak:
        if scc.is_rejecting():  # all cycles in scc are rejecting
            acc.set_sat(False)
        else:
            acc.set_sat(True)
        acc.formula = []
        return True
    return False


def print_aut(aut, output, m):
    if output is not None:
        f = open(output, m)
        f.write(aut.to_str() + '\n')
        f.close()
    else:
        print(aut.to_str())


def get_acc(aut):
    """
    Returns PACC (dnf) if dnf formula is shorter else PACC_CNF(cnf)
    """
    dnf_acc = ACC_DNF(aut.get_acceptance().to_dnf())
    #return dnf_acc
    cnf_acc = ACC_CNF(aut.get_acceptance().to_cnf())

    #print((cnf_acc),"\n", (dnf_acc))

    if (dnf_acc.acc_len() < cnf_acc.acc_len()) or (dnf_acc.acc_len()
                                                   == cnf_acc.acc_len() and len(dnf_acc) <= len(cnf_acc)):
        #print("DNF")
        return dnf_acc
    else:
        #acc = PACC_CNF(cnf_acc)
        #print("CNF")
        return cnf_acc


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
    orig_acc = get_acc(aut)
    si = spot.scc_info(aut)
    for scc in si:
        sccs.append(scc)
        acc = copy.deepcopy(orig_acc)
        acc.set_scc_index(counter)

        # acc = PACC(aut.get_acceptance().to_dnf()) # proc bych to z toho furt
        # dolovala?
        if (not weak_eval(aut, acc, scc, weak[counter])):
            acc.initial_cleanup(aut, scc)
        else:
            if scc.is_rejecting():  # all cycles in scc are rejecting
                acc.set_sat(False)
            else:
                acc.set_sat(True)
            acc.formula = []

        counter += 1

        if acc.sat is None:
            simplify(aut, acc, scc, counter, acc.acc_type)
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
            scc_clean_up_edges(aut, ACC(""), scc)
        aut.set_acceptance(0, spot.acc_code.t())

    elif all(acc.sat is False for acc in accs):
        for scc in sccs:
            scc_clean_up_edges(aut, ACC(""), scc)
        aut.set_acceptance(0, spot.acc_code.f())

    else:
        new_acc = ACC_DNF("Inf(0)")
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


def try_tt_ff(aut):
    """
    Try evaluate with K = 0(len of acceptance formula == 0)
    :param aut: spot::automaton
    :return: potentionally zero acceptance spot::automaton
    """
    last_eq_aut = spot.automaton(aut.to_str())
    clear_aut_edges(aut)
    aut.set_acceptance(0, spot.acc_code.t())
    if spot.are_equivalent(last_eq_aut, aut):
        return aut, True

    aut.set_acceptance(0, spot.acc_code.f())
    if spot.are_equivalent(last_eq_aut, aut):
        return aut, True
    return last_eq_aut, False


def map_accs(merged_f, short_accs):

    for acc in short_accs:
        # list_of_unmapped_dependencies.append({})
        if acc.sat is not None or not acc.formula:

            continue

        get_mapping(merged_f, acc)

        test_mapping(acc)


def merge_accs(aut, merged_f, short_accs, sccs):
    for acc in short_accs:
        if acc.sat is not None or not acc.formula:
            continue
        duplicate_marks(aut, merged_f, acc, sccs)


def process_automaton(aut):
    orig = spot.automaton(aut.to_str())
    spot.cleanup_acceptance_here(aut)
    if aut.get_acceptance().used_sets().count(
    ) < 1 or aut.prop_state_acc() == spot.trival.yes_value:
        return aut
    aut, is_simple = try_tt_ff(aut)
    if is_simple:
        return aut

    # simplifies acceptance condition for each scc
    short_accs, sccs = get_accs(aut)  # simplification occurs in here

    # Filters emty assceptance formulas from short_accs
    nempty_sccs, nempty_short_accs = check_emptyness(sccs, short_accs)

    if not nempty_short_accs:
        # sets acceptance and restores equivalence
        no_new_acceptance(aut, sccs, short_accs)
        return aut
    # sorts accs and sccs - primary key is length(cardinality), secondary key
    # is length of longest disjunct
    acc_quicksort(
        nempty_short_accs,
        nempty_sccs,
        0,
        len(nempty_short_accs) -
        1)
    # stores original acc formula
    orig_acc = ACC_CNF(aut.get_acceptance())

    # highest number of acceptance set in formula
    m = orig_acc.max()

    # disjunct with highest cardinality
    # final acceptance formula for whole automaton to be
    merged_f = copy.deepcopy(nempty_short_accs[0])
    merged_f.set_merged_f()

    # shift numbers of acceptance sets in future final formula to prevent
    # conflict
    shift_first_acc(merged_f, m)
    merged_f.get_dependencies()

    # rename to merge_logs

    map_accs(merged_f, short_accs)

    unused_clauses_depend = resolve_dependencies(
        aut, merged_f, short_accs, sccs)

    merge_accs(aut, merged_f, short_accs, sccs)


    # make aut equivalent with acceptance formula
    new_make_equiv(
        aut,
        short_accs,
        sccs,
        merged_f,
        unused_clauses_depend)
    aut.set_acceptance(merged_f.max() + 1, spot.acc_code(str(merged_f)))
    spot.cleanup_acceptance_here(aut)
    if not spot.are_equivalent(aut, orig):

        #assert(False)
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
