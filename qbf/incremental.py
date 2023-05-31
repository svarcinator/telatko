from qbf.formula_preparation import edge_dictionary, update_run_info, try_evaluate0, get_formula, solver_init, filter_out_representants, z3_result
from qbf.parser import process_variables
from telatko2.classes import *
from z3 import *


def restrict_f_vars(K, inner_edges_nums):
    formula = []
    for e in inner_edges_nums:
        # these two are not equivalent?
        # var1 = Bool("f_{0}_{1} ".format(str(e), str(K)))
        var = Bool("f_" + str(e) + "_" + str(K))

        formula.append(Not(var))
    return And(formula)


def restrict_pn_vars(C, K):
    formula = []
    for i in range(1, C + 1):

        p = Bool("p_" + str(i) + "_" + str(K))
        n = Bool("n_" + str(i) + "_" + str(K))
        formula.append(Not(p))
        formula.append(Not(n))
    return And(formula)


def restrict_C_vars(C, K):
    formula = []
    for i in range(1, K + 1):

        p = Bool("p_" + str(C) + "_" + str(i))
        n = Bool("n_" + str(C) + "_" + str(i))
        formula.append(Not(p))
        formula.append(Not(n))
    return And(formula)


def update_inc_solver(solver, currently_reduced, C, K, inner_edges_nums):
    if currently_reduced == FormulaAtribute.K:
        solver.push()
        solver.add(restrict_f_vars(K, inner_edges_nums))
        solver.add(restrict_pn_vars(C, K))

        return solver
    else:
        solver.push()
        solver.add(restrict_C_vars(C, K))
        return solver
    assert (False)


def model_assert(model, K):
    for t in model.decls():
        if str(t)[0] == 'f' and str(t)[-1] == str(K):
            assert (is_false(model[t]))


def inc_loop(
        aut,
        tmp_mode,
        scc_state_info,
        scc_edg,
        currently_reduced,
        original,
        formula_attr):

    K = aut.get_acceptance().used_sets().count()
    C = len(aut.get_acceptance().to_dnf().top_disjuncts())
    orig_scc_edg = scc_edg
    orig_scc_state_info = scc_state_info
    if currently_reduced == FormulaAtribute.K:
        K -= 1
    else:
        C -= 1

    # edge_dict: {acc_set_num : [edge_nums]}
    # scc_equiv_edges: [ {"combination (tuple) of marks  : ["edges that contain this combination of marks"]" }]
    # representants: ["first edge that I see for each combination of marks"]
    edge_dict, scc_equiv_edges, representants = edge_dictionary(
        aut, tmp_mode, scc_edg, formula_attr.scc_optimization)

    if tmp_mode == 1:
        scc_edg, scc_state_info = filter_out_representants(
            aut, set(representants), scc_edg, scc_state_info)
    else:
        # during gradual increasing of level we dont want the filtered versions
        # of scc info
        scc_edg = orig_scc_edg
        scc_state_info = orig_scc_state_info

    formula = get_formula(
        aut,
        scc_state_info,
        C,
        K,
        tmp_mode,
        edge_dict,
        scc_edg,
        formula_attr)

    solver = solver_init(formula, formula_attr.timeout)

    inner_edges_nums = []
    for scc_edg_list in scc_edg:
        inner_edges_nums += list(map(lambda e: aut.edge_number(e),
                                 scc_edg_list))

    model = None
    if currently_reduced == FormulaAtribute.K:
        K += 1
    else:
        C += 1

    while C > 0 and K > 0:

        if aut.get_acceptance().used_sets().count(
        ) < 1 or aut.prop_state_acc() == spot.trival.yes_value:
            return aut

        solver.check()
        res = solver.check()

        result, _, _ = z3_result(res)

        if result == Solver_result.sat:
            model = solver.model()
            if (K <= 1 or aut.get_acceptance().used_sets().count()
                    <= 1) and currently_reduced == FormulaAtribute.K:
                process_variables(
                    aut,
                    model,
                    scc_equiv_edges,
                    tmp_mode,
                    formula_attr.solver)
                return try_evaluate0(aut, original)
            elif C <= 1 and currently_reduced == FormulaAtribute.C:
                process_variables(
                    aut,
                    model,
                    scc_equiv_edges,
                    tmp_mode,
                    formula_attr.solver)
                return aut

            if tmp_mode == 1:
                solver = update_inc_solver(
                    solver, currently_reduced, formula_attr.C, K, representants)
            else:
                solver = update_inc_solver(
                    solver, currently_reduced, formula_attr.C, K, scc_edg)

            if currently_reduced == FormulaAtribute.K:
                K = K - 1
            else:
                C -= 1
        else:

            if model is not None:
                process_variables(
                    aut,
                    model,
                    scc_equiv_edges,
                    tmp_mode,
                    formula_attr.solver)
            if currently_reduced == FormulaAtribute.K:
                aut.set_name(
                    aut.get_name() +
                    update_run_info(
                        aut.get_acceptance().used_sets().count() -
                        1,
                        result,
                        tmp_mode))

            if aut.get_acceptance().used_sets().count(
            ) <= 1 and currently_reduced == FormulaAtribute.K:
                return try_evaluate0(aut, original)
            return aut

    return try_evaluate0(aut, original)
