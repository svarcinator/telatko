from qbf.formula_preparation import edge_dictionary, update_run_info, try_evaluate0, empty_aut, get_formula, filter_out_representants
from qbf.parser import process_variables
from telatko2.classes import *
from z3 import *


def not_incr_loop(aut,tmp_mode,
                  scc_state_info, scc_edg, currently_reduced, original, formula_attr):
    K = aut.get_acceptance().used_sets().count()
    C = len(aut.get_acceptance().to_dnf().top_disjuncts())
    orig_scc_edg = scc_edg
    orig_scc_state_info = scc_state_info
    if currently_reduced == FormulaAtribute.K:
        K -= 1
    else:
        C -= 1

    while C > 0 and K > 0:
        

        if aut.get_acceptance().used_sets().count(
        ) < 1 or aut.prop_state_acc() == spot.trival.yes_value:
            return aut

        edge_dict, scc_equiv_edges, representants = edge_dictionary(
            aut, tmp_mode, scc_edg, formula_attr.scc_optimization)

        
        if tmp_mode == 1:
            scc_edg, scc_state_info = filter_out_representants(aut, set(representants), orig_scc_edg, orig_scc_state_info)
        
        
           
        formula = get_formula(
            aut,
            scc_state_info,
            C,
            K,
            tmp_mode,
            edge_dict,
            scc_edg,
            formula_attr.scc_optimization)

        scc_edg = orig_scc_edg
        scc_state_info = orig_scc_state_info
        

        solver = Solver()
        solver.add(formula)
        solver.set("timeout", 1000 * formula_attr.timeout)
        solver.push()
        res = solver.check()

        if res == sat:
            s = solver.model()
            process_variables(aut, s, scc_equiv_edges, tmp_mode)
            
            """
            if not spot.are_equivalent(original, aut):
                print("NOT EQUIVALENT! C=", C, " K=", K)
                return aut
            """
            
                
        else:
            if currently_reduced == FormulaAtribute.K:
                aut.set_name(
                    aut.get_name() +
                    update_run_info(
                        K,
                        res,
                        tmp_mode))
            if aut.get_acceptance().used_sets().count() <= 1:
                return try_evaluate0(aut, original)
            return aut

        if aut.get_acceptance().used_sets().count() < 1:
            return empty_aut(aut, original)

        if currently_reduced == FormulaAtribute.K:
            K = K - 1
        else:
            C = C - 1
    return try_evaluate0(aut, original)
