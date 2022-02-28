import random
# from classes import *
from qbf.parser import *
#from qbf.optimization import *
from qbf.z3_formula import *

def add_or_append(dict, key, value):
    if key in dict:
        dict[key].append(value)
    else:
        dict[key] = [value]

def edge_dictionary(aut, mode):
    """

    Args:
        aut: spot::twa - automaton from input

    Returns: Dictionary {acceptance set number : [numbers of edges in this set]}

    """
    #list_of_all_edges = aut.edges()
    edge_dict = {}
    scc_equiv_edges = []
    representants = []
    #set_nums = aut.get_acceptance().used_sets()

    si = spot.scc_info(aut)
    for scc in range(si.scc_count()):
        marks_edges = {}
        edges = si.inner_edges_of(scc)
        for e in edges:
            # edge_dict
            if mode != 1:
                for m in e.acc.sets():
                    add_or_append(edge_dict, m, aut.edge_number(e))
            if tuple( e.acc.sets()) in marks_edges:
                marks_edges[tuple( e.acc.sets())].append(e)
                # one num representant is enough to create formula
            else:
                marks_edges[tuple( e.acc.sets())] = [e]
                representants.append(aut.edge_number(e))

                if mode == 1:
                    for m in e.acc.sets():
                        add_or_append(edge_dict, m, aut.edge_number(e))

        scc_equiv_edges.append(marks_edges)
    return edge_dict, scc_equiv_edges, representants




def get_edges(aut):
    """

    Args:
        aut: spot::twa - automaton

    Returns: [numbers of inner edges of all sccs], [spot::twa_graph::edge_storage_t - inner edges of all sccs]

    """
    edge_nums = []
    edges_list = []
    si = spot.scc_info(aut)
    for scc in range(si.scc_count()):
        edges = si.inner_edges_of(scc)
        for e in edges:
            edge_nums.append(aut.edge_number(e))
            edges_list.append(e)
    return edge_nums, edges_list


def scc_info(aut):
    """

    Args:
        aut:

    Returns: scc_state_info[{state_number : [edges out of the state], [edges in the state]}]
              scc_edg [[numbers of edges of one SCC]]

    """
    scc_state_inf = []

    scc_edg = []
    si = spot.scc_info(aut)
    counter = 0
    for i in range(si.scc_count()):
        states = si.states_of(i)
        if si.is_trivial(i):
            continue
        state_dict = {}
        for s in states:
            state_dict[s] = [[], []]
        edges = si.inner_edges_of(i)
        scc_edg.append([])
        for e in edges:
            scc_edg[counter].append(aut.edge_number(e))
            state_dict[e.src][0].append(aut.edge_number(e))
            state_dict[e.dst][1].append(aut.edge_number(e))
        counter += 1
        scc_state_inf.append(state_dict)
    return scc_state_inf, scc_edg






def create_formula(
        aut,
        edge_dict,
        scc_edg,
        scc_state_info,
        inner_edges_nums,
        C,
        K,
        inner_edges,
        mode, qbf_solver, representants):
    """

    :param aut:
    :param acc:
    :param edge_dict:
    :param scc_edg:
    :param state_dict:
    :param inner_edges: [edge_num :: int] all inner edges of SCCs
    :param C: ::int - clauses caunt
    :param K: :: int - acceptance sets count
    :return:
    """


    if mode == 1:
        f_creator = Z3_f_ctor(edge_dict, scc_edg, None
                      ,inner_edges_nums,C, K, inner_edges
                      , mode)

        z3_formula = f_creator.get_level1(aut, representants)
    else:
        f_creator = Z3_f_ctor(edge_dict, scc_edg, scc_state_info
                      ,inner_edges_nums,C, K, inner_edges
                      , mode)
        z3_formula = f_creator.get_qbf_formula(aut)

    return z3_formula

def try_evaluate0(aut, orig, qbf_run_info):
    """
    Try evaluate with K = 0(len of acceptance formula == 0)
    :param aut: spot::automaton
    :return: potentionally zero acceptance spot::automaton
    """
    last_eq_aut = spot.automaton(aut.to_str())
    aut.set_name(qbf_run_info + "F_0_S")
    last_eq_aut.set_name(qbf_run_info + "F_0_U")
    clear_aut_edges(aut)
    aut.set_acceptance(0, spot.acc_code.t())
    if spot.are_equivalent(orig, aut):

        return aut

    aut.set_acceptance(0, spot.acc_code.f())
    if spot.are_equivalent(orig, aut):
        return aut
    return last_eq_aut


def count_sets(sets):
    counter = 0
    for s in sets:
        counter += 1
    return counter

def remove_edges(edge_dict, edges):
    new_dict = {}

    for key in edge_dict:
        new_dict[key] = list(set(edge_dict[key]) & set(edges))

    return new_dict


def scc_optimized_formula(aut, acc, scc_state_info, C, K, mode, edge_dict, scc_edg, representants):
    formula = []
    weak = spot.scc_info(aut).weak_sccs()

    si = spot.scc_info(aut)
    relevant_scc_counter = 0
    scc_counter = 0


    for scc in (si):

        if si.is_trivial(scc_counter):
            scc_counter += 1
            continue

        scc_inner_edges = si.inner_edges_of(scc_counter)
        scc_inner_edges_nums = list(map(lambda e: aut.edge_number(e), scc_inner_edges))

        scc_edge_dict = remove_edges(edge_dict, scc_inner_edges_nums)


        if mode == 1:
            scc_representants = list(set(representants) & set(scc_inner_edges_nums))
            f_creator = Z3_f_ctor(scc_edge_dict, [scc_inner_edges_nums], None
                          ,scc_inner_edges_nums,C, K, scc_inner_edges
                          , mode)

            if si.is_rejecting_scc(scc_counter):

                z3_f = f_creator.rejecting_scc(scc_representants)
                formula.append(z3_f)

            elif weak[scc_counter] and si.is_accepting_scc(scc_counter):

                z3_f = f_creator.accepting_scc(scc_representants)
                formula.append(z3_f)

            else:

                formula.append(f_creator.get_level1(aut, scc_representants))
            #z3_f = f_creator.get_level1(aut, scc_representants)

            #assert(False)
        else:

            f_creator = Z3_f_ctor(scc_edge_dict,  [scc_inner_edges_nums], [scc_state_info[relevant_scc_counter]]
                          ,scc_inner_edges_nums,C, K, scc_inner_edges
                          , mode)
            if si.is_rejecting_scc(scc_counter):

                z3_f = f_creator.rejecting_scc_l23(aut)
                formula.append(z3_f)
            else:
                formula.append(f_creator.get_qbf_formula(aut))

        relevant_scc_counter += 1
        scc_counter += 1

    return And(formula)




def resolve_formula_atributes(minimized_atribute, C, K):
    if minimized_atribute == 'clauses':

        return FormulaAtribute.C
    else:

        return FormulaAtribute.K

def update_run_info(K, res, tmp_mode):
    if res == z3.unknown:
        str_res = "T"
    if res == unsat:
        str_res = "U"
    assert(str_res != "")
    return "L_{0}_{1}_{2} ".format(str(tmp_mode), str(K), str_res)


def play(aut, C, K, mode, timeout, timeouted,
         optimized_scc, minimized_atribute, qbf_solver, tmp_mode):

    spot.cleanup_acceptance_here(aut)

    if aut.get_acceptance().used_sets().count(
    ) < 1 or aut.prop_state_acc() == spot.trival.yes_value:

        return aut
    original = spot.automaton(aut.to_str())

    # [int] - all nums of inner edges of SCCs
    inner_edges_nums, inner_edges = get_edges(aut)

    # scc_edg [[nums of edges of one scc]]
    # scc state info [{state num : [[num of edge of which is the state source
    # of][num of edge of which is the state destination of]]}]
    scc_state_info, scc_edg = scc_info(aut)

    # K = K - 1  # we dont want to try what we already know
    qbf_run_info = ""


    currently_reduced = resolve_formula_atributes(minimized_atribute, C, K)
    if currently_reduced == FormulaAtribute.K:
        K -= 1
    else:
        C -= 1

    while C > 0 and K > 0:

        if aut.get_acceptance().used_sets().count(
        ) < 1 or aut.prop_state_acc() == spot.trival.yes_value:

            return aut

        # dictionary {acc_set_num : [edge_nums]}
        edge_dict, scc_equiv_edges, representants = edge_dictionary(aut, tmp_mode)

        # QBF formula is written into ./sat_file
        formula = None
        if (optimized_scc):
            # tohle pujde dopryc ?
            acc = ACC_DNF(aut.get_acceptance().to_dnf())
            formula = scc_optimized_formula(aut, acc, scc_state_info, C, K, tmp_mode, edge_dict, scc_edg, representants)
        else:

            formula = create_formula(
                aut,
                edge_dict,
                scc_edg,
                scc_state_info,
                inner_edges_nums,
                C,
                K,
                inner_edges,
                tmp_mode, qbf_solver, representants)

        if formula != None:
            # QBF SOLVER
            assert(qbf_solver == "z3")
            solver = Solver()
            solver.add(formula)
            solver.set("timeout",1000* timeout)
            solver.push()
            res = solver.check()

            if  res == sat:
                s = solver.model()

                process_variables(aut, s, qbf_solver, scc_equiv_edges, tmp_mode)

            else:
                qbf_run_info += update_run_info(K, res, tmp_mode)

                if (tmp_mode < mode):
                    tmp_mode += 1
                    continue
                else:

                    if minimized_atribute == 'all' and currently_reduced == FormulaAtribute.K:
                        currently_reduced = FormulaAtribute.C
                        K = K + 1
                        C = C - 1
                        continue
                    else:
                        aut.set_name(qbf_run_info)
                        return aut


        if aut.get_acceptance().used_sets().count() < 1:
            clear_aut_edges(aut)
            aut.set_acceptance(0, spot.acc_code.t())
            if not spot.are_equivalent(original, aut):
                aut.set_acceptance(0, spot.acc_code.f())
            aut.set_name(qbf_run_info)
            return aut

        if currently_reduced == FormulaAtribute.K:
            K = K - 1
        else:
            C = C - 1

    return try_evaluate0(aut, original, qbf_run_info)


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
