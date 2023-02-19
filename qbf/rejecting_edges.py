import spot
from telatko2.classes import MarkType


def clear_aut_edges(aut):
    for e in aut.edges():
        e.acc = spot.mark_t()


def list_of_rejecting_edges(aut):

    rejecting_edges = []
    si = spot.scc_info(aut)

    for i in range(si.scc_count()):

        if si.is_trivial(i):
            continue

        if si.check_scc_emptiness(i):
            for e in si.inner_edges_of(i):
                rejecting_edges.append(e)

    return rejecting_edges


def rejecting_sccs_edges(aut, acc):
    """
    Takes all edges from original automaton and makes them rejecting for the new acceptance condition.
    (As side effect has to clean all edges of the automaton.)
    """

    rejecting_edges = list_of_rejecting_edges(aut)

    # returns cpp pair <bool, spot.mark_t>, if bool is False, there is no rejecting combination
    # there should be rejecting combination since we are dealing with
    # rejecting SCCs
    rejecting_marks = spot.acc_cond(spot.acc_code(acc)).unsat_mark()

    # fails if there is no unsat combination of marks
    assert (rejecting_marks[0])
    # removes all acceptance marks from edges
    clear_aut_edges(aut)

    for e in rejecting_edges:
        e.acc = rejecting_marks[1]
