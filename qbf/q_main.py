import random
# from classes import *
from qbf.parser import *
from qbf.formula import *
from qbf.optimization import *
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
    #print(scc_equiv_edges)
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
            #print("trivial before", i)
            continue
        #print("i: ", i)
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
    if qbf_solver == "limboole":
        f_creator = Limboole_f_ctor(edge_dict, scc_edg, scc_state_info
                      ,inner_edges_nums,C, K, inner_edges
                      , mode, qbf_solver)
        f_creator.get_qbf_formula(aut)

        return None
    else:


        f_creator = Z3_f_ctor(edge_dict, scc_edg, scc_state_info
                      ,inner_edges_nums,C, K, inner_edges
                      , mode, qbf_solver)
        if mode == 1:
            z3_formula = f_creator.get_level1(aut, representants)
        else:
            z3_formula = f_creator.get_qbf_formula(aut)

        return z3_formula

    # quantified edges #e_1 ... #e_n
    quant_edges = quant_all(inner_edges_nums)
    # quantified variables ?w_1 ?w_2 ... ?w_n

    # quant_edges += w_quant(aut)
    if mode > 2:
        quant_edges += w_quant(aut)

    # edges that are true create continuous cycle of edges aka laso

    if mode == 3:
        laso = laso2(aut, inner_edges, scc_edg)
        in_out = in_n_out(scc_state_info)
        laso.add_subf(in_out)
    else:
        laso = laso_f(
            aut,
            inner_edges_nums,
            scc_state_info,
            scc_edg,
            inner_edges,
            mode)

    # reqiurements on old acceptance formula
    old = old_formula(aut.get_acceptance(), edge_dict)

    # assignment of variables to create new acceptance formula
    new = new_formula(inner_edges_nums, C, K)
    # old and new need to be equivalent
    eq = SATformula('<->')
    eq.add_subf(old)
    eq.add_subf(new)

    impl = SATformula("->")
    impl.add_subf(laso)
    impl.add_subf(eq)

    # root of QBFformula
    con = SATformula("&")
    con.add_subf(impl)

    # not (Inf1 & Fin1)
    inf_not_fin = inf_is_not_fin_clause(C, K)

    # (Fin1 | Inf1) - we need control over formula
    inf_or_fin = inf_or_fin_f(C, K)
    con.add_subf(inf_not_fin)
    con.add_subf(inf_or_fin)
    # prints our formula into text file
    SAT_output("sat_file", quant_edges, con)


def try_evaluate0(aut, orig):
    """
    Try evaluate with K = 0(len of acceptance formula == 0)
    :param aut: spot::automaton
    :return: potentionally zero acceptance spot::automaton
    """
    last_eq_aut = spot.automaton(aut.to_str())
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


def scc_optimized_formula(aut, acc, scc_state_info, C, K, L):
    formula = SATformula('&')
    #print("scc state info:" , scc_state_info)
    weak = spot.scc_info(aut).weak_sccs()

    si = spot.scc_info(aut)
    max_T = 0
    max_states = 0
    counter = 0
    scc_counter = 0


    for scc in (si):

        if si.is_trivial(scc_counter):
            #print("trivial", si.states_of(scc_counter))
            scc_counter += 1
            continue

        scc_inner_edges = si.inner_edges_of(scc_counter)
        edges_translator = {}
        mark_edg_dict = get_mark_edg(aut, scc_inner_edges, edges_translator)
        max_T = max(max_T, len(edges_translator))

        eq = SATformula('<->')
        #old = old_formula_scc(aut.get_acceptance(), mark_edg_dict, edges_translator, si.acc_sets_of(scc))

        # print(si.used_acc_of(scc_counter))
        if si.is_rejecting_scc(scc_counter):
            # print("rejecting")
            # old je False
            old = SATformula("&")
            old.add_subf("t")
            old.add_subf("!t")
            eq = new_formula2(edges_translator, C, K)
            eq.negate()
            eq.imper()

        elif weak[scc_counter] and si.is_accepting_scc(scc_counter):

            #print("weak accepting", si.states_of(scc_counter))
            old = SATformula("|")
            old.add_subf("t")
            old.add_subf("!t")
            eq = new_formula2(edges_translator, C, K)
        else:
            old = old_formula2(
                acc,
                mark_edg_dict,
                edges_translator,
                si.acc_sets_of(scc_counter),
                aut,
                scc)
            new = new_formula2(edges_translator, C, K)
            eq.add_subf(old)
            eq.add_subf(new)

        impl = SATformula('->')
        laso = laso_part(
            scc_state_info[counter],
            edges_translator,
            L,
            scc_inner_edges,
            aut)
        if L == 3:
            laso = laso_scc_optimized(
                aut,
                scc_inner_edges,
                scc_state_info[counter],
                edges_translator)
        impl.add_subf(laso)
        impl.add_subf(eq)
        formula.add_subf(impl)
        counter += 1
        scc_counter += 1
    formula.add_subf(inf_or_fin_f(C, K))
    formula.add_subf(inf_is_not_fin_clause(C, K))
    # formula.add_subf(least_one(max_T))

    q = quantify_e(max_T)
    if L > 2:
        q += w_quant(aut)
    SAT_output("sat_file", q, formula)


def resolve_formula_atributes(minimized_atribute, C, K):
    if minimized_atribute == 'clauses':
        #print("reducing clauses")

        return FormulaAtribute.C
    else:

        return FormulaAtribute.K


def play(aut, C, K, mode, timeout, timeouted,
         optimized_scc, minimized_atribute, qbf_solver):

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
    tmp_mode = 1

    currently_reduced = resolve_formula_atributes(minimized_atribute, C, K)
    if currently_reduced == FormulaAtribute.K:
        K -= 1
    else:
        C -= 1

    while C > 0 and K > 0:
        #print("C: ", C, ", K: ", K)

        if aut.get_acceptance().used_sets().count(
        ) < 1 or aut.prop_state_acc() == spot.trival.yes_value:

            return aut
        """
        if K == 0 and currently_reduced == FormulaAtribute.K:
            return try_evaluate0(aut, original)
        """


        # dictionary {acc_set_num : [edge_nums]}
        edge_dict, scc_equiv_edges, representants = edge_dictionary(aut, mode)

        # QBF formula is written into ./sat_file
        formula = None
        if (optimized_scc):
            acc = ACC_DNF(aut.get_acceptance().to_dnf())
            # print("scc")
            scc_optimized_formula(aut, acc, scc_state_info, C, K, tmp_mode)
        else:
            # print("not scc")

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
            #print("z3 formula: ", formula)
            solver = Solver()
            solver.add(formula)
            solver.set("timeout",1000* timeout)
            solver.push()

            #print("solver check: ", solver.check())

            if solver.check() == sat:
                print("--satisfiable--")
                s = solver.model()
                #print(s)

                process_variables(aut, s, qbf_solver, scc_equiv_edges, mode)

                #parse_model(solver.model())
            else:
                # code repetition, necessary to rewrite
                print("unsatisfiable")
                if (tmp_mode < mode):
                    tmp_mode += 1
                    print("new level of simplification:", tmp_mode)
                    continue
                else:

                    if minimized_atribute == 'all' and currently_reduced == FormulaAtribute.K:
                        currently_reduced = FormulaAtribute.C
                        K = K + 1
                        C = C - 1
                        continue
                    else:
                        return aut

        else:
            assert(qbf_solver == "limboole")
            # LIMBOOLE SOLVER
            try:
                cp = subprocess.run(["./qbf/limboole1.2/limboole",
                                     "./sat_file"],
                                    universal_newlines=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    timeout=int(timeout))

            except subprocess.TimeoutExpired:
                print("expired")
                timeouted[0] += 1
                return aut

            out = cp.stdout.splitlines()
            f = open("sat_evaluation", "w")
            f.write(cp.stdout)
            f.close()

            if len(out) == 1:
                print("unsatisfiable")
                if (tmp_mode < mode):

                    tmp_mode += 1
                    print("new level of simplification:", tmp_mode)
                    continue
                else:
                    if minimized_atribute == 'all' and currently_reduced == FormulaAtribute.K:
                        currently_reduced = FormulaAtribute.C
                        K = K + 1
                        C = C - 1
                        continue
                    else:
                        return aut

            if len(out) == 0:
                print("sat error")
                return aut
            variables = out[1:]
            print("satisfiable")

            process_variables(aut, variables, qbf_solver, scc_equiv_edges, mode)

        if aut.get_acceptance().used_sets().count() == 0:
            print("used sets = 0, setting acc to t")
            aut.set_acceptance(0, spot.acc_code.t())
            if not spot.are_equivalent(original, aut):
                print("setting acc to f")
                aut.set_acceptance(0, spot.acc_code.f())

        if currently_reduced == FormulaAtribute.K:
            K = K - 1
        else:
            C = C - 1
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
