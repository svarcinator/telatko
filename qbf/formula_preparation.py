from qbf.z3_formula import *
from qbf.parser import clear_aut_edges
import spot
from qbf.limboole_formula import *
from telatko2.classes import Solver_result, safe_file
from qbf.solver_manipulation.solver_functions import z3_result, query
import subprocess



def update_run_info(K, res, tmp_mode):
    if res == Solver_result.timeout:
        str_res = "T"
    if res == Solver_result.unsat:
        str_res = "U"
    assert (str_res != "")
    return "L{0}_{1}_{2} ".format(str(tmp_mode), str(K), str_res)


def empty_aut(aut, original):
    clear_aut_edges(aut)
    aut.set_acceptance(0, spot.acc_code.t())
    if not spot.are_equivalent(original, aut):
        aut.set_acceptance(0, spot.acc_code.f())
    aut.set_name(aut.get_name() + "F_0_S")
    return aut


def add_or_append(dict, key, value):
    if key in dict:
        dict[key].append(value)
    else:
        dict[key] = [value]


def filter_out_representants(aut, representants_set, scc_edg, scc_state_info):
    new_scc_edg = []
    for i in range(len(scc_edg)):
        new_scc_edg.append(
            list(
                filter(
                    lambda e: aut.edge_number(e) in representants_set,
                    scc_edg[i])))

    new_scc_state_info = []

    for scc in scc_state_info:
        for k, v in scc.items():
            out_state = list(set(v[0]) & representants_set)
            in_state = list(set(v[1]) & representants_set)
            new_scc_state_info.append({k: [out_state, in_state]})

    return new_scc_edg, new_scc_state_info


def print_eq_edges(aut, eq_edges):
    for d in eq_edges:
        for key, val in d.items():
            print(key, " : ", list(map(lambda e: aut.edge_number(e), val)))


def dict_union(d1, d2):
    """
    Args:
        d1 :: (acc. sets) : [edges]
        d2 :: (acc. sets) : [edges]

    """
    for key, val in d1.items():
        if key in d2.keys():
            d2[key] = d2.get(key, []) + d1.get(key, [])
        else:
            d2[key] = d1.get(key, [])
    return d2


def edge_dictionary(aut, mode, sccs_edges, scc_optimalization):
    """

    Args:
        aut: spot::twa - automaton from input
        sccs_edges [[edges of one SCC]]
        scc_optimalization: Bool - Is the SCC optimalization turned on.

    Returns:
        edge_dict: {acceptance set number : [numbers of edges in this set]}
        scc_equiv_edges: [ {"combination (tuple) of marks  : ["edges that contain this combination of marks"]" }]
        representants: ["first edge that I see for each combination of marks"]

    """

    edge_dict = {}
    scc_equiv_edges = []
    representants = []

    for one_scc_edges in sccs_edges:
        marks_edges = {}

        for e in one_scc_edges:

            # edge_dict
            if mode != 1:
                for m in e.acc.sets():
                    add_or_append(edge_dict, m, aut.edge_number(e))

            if tuple(e.acc.sets()) in marks_edges:
                marks_edges[tuple(e.acc.sets())].append(e)
                # one num representant is enough to create formula
            else:

                marks_edges[tuple(e.acc.sets())] = [e]

                representants.append(aut.edge_number(e))

                if mode == 1:
                    for m in e.acc.sets():
                        add_or_append(edge_dict, m, aut.edge_number(e))
        scc_equiv_edges.append(marks_edges)

        """
        if scc_optimalization or scc_equiv_edges == []:
            scc_equiv_edges.append(marks_edges)
        else:
            scc_equiv_edges[0] = dict_union(scc_equiv_edges[0], marks_edges)
        """

    return edge_dict, scc_equiv_edges, representants


def solver_init(formula, timeout):
    solver = Solver()
    # solver.push()
    solver.add(formula)
    solver.set("timeout", 1000 * timeout)
    solver.push()
    return solver


def scc_unoptimized_formula(
        aut,
        edge_dict,
        scc_edg,
        scc_state_info,
        C,
        K,
        mode, solver):
    """

    :param aut:
    :param acc:
    :param edge_dict:
    :param scc_edg: [[edge of one scc]]
    :param state_dict:
    :param C: ::int - clauses caunt
    :param K: :: int - acceptance sets count
    :return:
    """

    scc_edges_nums = []
    for scc_edg_list in scc_edg:
        scc_edges_nums.append(
            list(map(lambda e: aut.edge_number(e), scc_edg_list)))
    f_creator = None
    if solver == "z3":

        f_creator = Z3_f_ctor(
            edge_dict,
            scc_edg,
            scc_edges_nums,
            scc_state_info,
            C,
            K,
            mode)
    else:
        #print(f"Limboole formula")

        f_creator = Boole_f_ctor(
            edge_dict,
            scc_edg,
            scc_edges_nums,
            scc_state_info,
            C,
            K,
            mode)

    formula = f_creator.get_qbf_formula(aut)
    return formula


def remove_edges(edge_dict, edges):
    new_dict = {}

    for key in edge_dict:
        new_dict[key] = list(set(edge_dict[key]) & set(edges))

    return new_dict


def scc_optimized_formula(aut, scc_state_info, C,
                          K, mode, edge_dict, scc_edg):

    formula = []

    # create list of list with edge numbers for each scc
    scc_edges_nums = []
    for scc_edg_list in scc_edg:
        scc_edges_nums.append(
            list(map(lambda e: aut.edge_number(e), scc_edg_list)))

    for i in range(len(scc_edg)):

        scc_edge_dict = remove_edges(edge_dict, scc_edges_nums[i])
        if scc_edg[i] == []:

            continue

        f_creator = Z3_f_ctor(
            scc_edge_dict,
            [scc_edg[i]],
            [scc_edges_nums[i]],
            [scc_state_info[i]],
            C,
            K,
            mode)

        z3_formula = f_creator.get_qbf_formula(aut)
        formula.append(z3_formula)

    return And(formula)



def run_with_limited_time(aut1, aut2, time):

    safe_file("a1", aut1.to_str(), "w")
    safe_file("a2", aut2.to_str(), "w")

    try:
        cp = subprocess.run(["python3",
                             "./are_eq.py",
                             "-F1", "./a1", "-F2", "a2"],
                            universal_newlines=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            timeout=time)
    except subprocess.TimeoutExpired:
        print("expired")
        return False
    print(f"Response: {cp.stdout}")

    if cp.stdout == "EQUIVALENT\n":
        print("here")

        return True
    else:
        return False




def try_evaluate0(aut, orig):
    """
    Try evaluate with K = 0(len of acceptance formula == 0)
    :param aut: spot::automaton
    :return: potentionally zero acceptance spot::automaton
    """

    last_eq_aut = spot.automaton(aut.to_str())

    last_eq_aut.set_name(last_eq_aut.get_name() + "F_0_U")
    clear_aut_edges(aut)
    aut.set_acceptance(0, spot.acc_code.t())

    are_eq = run_with_limited_time(orig, aut, 20)

    if are_eq:
        aut.set_name(aut.get_name() + "F_0_S")
        return aut

    aut.set_acceptance(0, spot.acc_code.f())

    are_eq = run_with_limited_time(orig, aut, 2)

    if are_eq:
        aut.set_name(aut.get_name() + "F_0_S")
        return aut
    return last_eq_aut


def get_formula(aut, scc_state_info, C, K, tmp_mode, edge_dict, scc_edg,
                formula_attr):
    if (formula_attr.scc_optimization):

        formula = scc_optimized_formula(
            aut,
            scc_state_info,
            C,
            K,
            tmp_mode,
            edge_dict,
            scc_edg)
    else:

        formula = scc_unoptimized_formula(
            aut,
            edge_dict,
            scc_edg,
            scc_state_info,
            C,
            K,
            tmp_mode, formula_attr.solver)
    return formula
