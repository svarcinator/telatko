import random
from threading import current_thread
from qbf.parser import *
from qbf.incremental import inc_loop
from qbf.not_incremental import not_incr_loop
from qbf.formula_preparation import try_evaluate0



def scc_info(aut):
    """

    Args:
        aut:

    Returns: scc_state_info[{state_number : [edges out of the state], [edges in the state]}]
              scc_edg [[numbers of inner edges of one SCC]]

    """
    scc_state_inf = []

    # [[edges in one scc]]
    scc_edges = []

    si = spot.scc_info(aut)

    for i in range(si.scc_count()):
        states = si.states_of(i)
        if si.is_trivial(i):
            continue
        
        if si.check_scc_emptiness(i):
            # if rejecting ignore edges (for now)
            states = si.states_of(i)
            continue
        
        state_dict = {}
        for s in states:
            state_dict[s] = [[], []]
        edges = si.inner_edges_of(i)
        
        scc_edges.append(list(edges))
    
        for e in edges:
            
            state_dict[e.src][0].append(aut.edge_number(e))
            state_dict[e.dst][1].append(aut.edge_number(e))

        scc_state_inf.append(state_dict)
    
    return scc_state_inf, scc_edges



def count_sets(sets):
    counter = 0
    for s in sets:
        counter += 1
    return counter




def resolve_formula_atributes(minimized_atribute, C, K):
    if minimized_atribute == 'clauses':

        return FormulaAtribute.C
    else:

        return FormulaAtribute.K



def play(aut, formula_attr):
    aut.set_name("")

    spot.cleanup_acceptance_here(aut)

    if aut.get_acceptance().used_sets().count(
    ) < 1 or aut.prop_state_acc() == spot.trival.yes_value:
        return aut

    original = spot.automaton(aut.to_str())

    


    # scc_edg [[nums of edges of one scc]]
    # scc state info [{state num : [[num of edge of which is the state source
    # of][num of edge of which is the state destination of]]}]
    scc_state_info, scc_edg = scc_info(aut)

    if formula_attr.incremental:
        for i in range(formula_attr.tmp_level, formula_attr.level + 1):
            if aut.get_acceptance().used_sets().count() <= 1:
                aut = try_evaluate0(aut, original)
                break
            aut = inc_loop(
                aut,
                i,
                scc_state_info,
                scc_edg,
                FormulaAtribute.K,
                original,
                formula_attr)
        # if reduce C, reduce C
        if formula_attr.min_clauses:
            aut = inc_loop(
                aut,
                formula_attr.level,
                scc_state_info,
                scc_edg,
                FormulaAtribute.C,
                original,
                formula_attr)
        return aut

    # not incremental solving

    for i in range(formula_attr.tmp_level, formula_attr.level + 1):
        if aut.get_acceptance().used_sets().count() <= 1:
            aut = try_evaluate0(aut, original)
            break
        aut = not_incr_loop(
            aut,
            i,
            scc_state_info,
            scc_edg,
            FormulaAtribute.K,
            original,
            formula_attr)
    # if reduce C, reduce C
    if formula_attr.min_clauses:
        aut = inc_loop(
            aut,
            formula_attr.level,
            scc_state_info,
            scc_edg,
            FormulaAtribute.C,
            original,
            formula_attr)
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
        # print_aut(a1, "err_aut.hoa", "a")
    f.write('\n')
    f.close()


if __name__ == "__main__":
    main(sys.argv[1:])
