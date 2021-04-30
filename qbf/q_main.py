import random
# from classes import *
from qbf.parser import *
from qbf.formula import *
from qbf.sequence_formula import *



def edge_dictionary(aut):
    """

    Args:
        aut: spot::twa - automaton from input

    Returns: Dictionary {acceptance set number : [number of edge in this set]}

    """
    list_of_all_edges = aut.edges()
    edge_dict = {}
    set_nums = aut.get_acceptance().used_sets()

    for acc_set in set_nums.sets():
        edge_dict[acc_set] = list(map(aut.edge_number, list(
            filter(lambda edg: edg.acc.has(acc_set), list_of_all_edges))))
    return edge_dict


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


def SAT_output(quantified, formula):
    """
    Prints formula into file(for QBF solver) named satfile.
    Args:
        quantified: Universal quantificators of formula
        formula: SATformula - Boolean formula

    Returns:

    """
    f = open("sat_file", "w")
    f.write(str(quantified) + str(formula))
    f.close()

def w_quant(aut):
    """
    Creates universal variables w_
    Args:
        aut:

    Returns:

    """
    univ_formula = ""
    num_states = aut.num_states()
    for i in range(num_states):
        univ_formula += "?w_" + str(i)
    return univ_formula


def laso2(aut, inner_edges, scc_edg):
    """
    QBF CYCLES ve statistikach
    Formula that makes sure that the edges are cycles.
    Unluckily the complexity is too high to compute jeden pitomej automat s 12 stavama.
    Args:
        aut:
        inner_edges:
        scc_edg:

    Returns:

    """
    main_dis = SATformula("|")

    con3 = SATformula("&")
    dis1 = SATformula("|")
    dis2 = SATformula("|")
    con1 = SATformula("&")
    con2 = SATformula("&")

    for e in inner_edges:
        src = str(e.src)
        dst = str(e.dst)
        """
        if e.src == e.dst:
            continue
        """

        # part one
        impl = SATformula("->")
        impl.add_subf(SATformula("e_"+str(aut.edge_number(e))))
        c = SATformula("&")
        c.add_subf(SATformula("w_" + src))
        c.add_subf(SATformula("w_" + dst))
        impl.add_subf(c)
        con1.add_subf(impl)

        # part two
        impl2 = SATformula("->")
        impl2.add_subf(SATformula("e_" + str(aut.edge_number(e))))
        c1 = SATformula("&")
        c1.add_subf(SATformula("!w_" + src))
        c1.add_subf(SATformula("!w_" + dst))
        impl2.add_subf(c1)
        con2.add_subf(impl2)

        # part three
        ## dis 1
        c2 = SATformula("&")
        c2.add_subf(SATformula("e_" + str(aut.edge_number(e))))
        c2.add_subf(SATformula("w_" + src))
        c2.add_subf(SATformula("!w_" + dst))
        dis1.add_subf(c2)

        ## dis 2
        c3 = SATformula("&")
        c3.add_subf(SATformula("e_" + str(aut.edge_number(e))))
        c3.add_subf(SATformula("!w_" + src))
        c3.add_subf(SATformula("w_" + dst))
        dis2.add_subf(c3)

    con3.add_subf(dis1)
    con3.add_subf(dis2)

    main_dis.add_subf(con1)
    main_dis.add_subf(con2)
    main_dis.add_subf(con3)
    laso = SATformula("&")
    one_scc = one_scc_f(scc_edg)
    laso.add_subf(main_dis)
    laso.add_subf(one_scc)
    return laso



def create_formula(aut, acc, edge_dict, scc_edg, scc_state_info, inner_edges_nums, C, K, inner_edges, mode):
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

    # quantified edges #e_1 ... #e_n
    quant_edges = quant_all(inner_edges_nums)
    # quantified variables #w_1 #w_2 ... #w_n

<<<<<<< HEAD
    #quant_edges += w_quant(aut)
=======
    if mode > 2:
        quant_edges += w_quant(aut)
>>>>>>> 21272206a1a084f916576be1f3ee1e7c61c57328

    # edges that are true create continuous cycle of edges aka laso

    if mode == 4:
        laso = laso2(aut, inner_edges, scc_edg)
    else:
        laso = laso_f(aut, inner_edges_nums, scc_state_info, scc_edg, inner_edges, mode)



    # reqiurements on old acceptance formula
    old = old_formula(acc, edge_dict)

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
    SAT_output(quant_edges, con)

def resolve_flags(precision_flag, ck_flag, mode, C, K):
    if ck_flag:
        if precision_flag or mode == '1':
            return None, None, None, None, True
        else:
            precision_flag = 1
    else:
        if precision_flag or mode == '1':
            ck_flag = 1
            precision_flag = 0
            K += 1
        else:
            precision_flag = 1
    return precision_flag, ck_flag, C, K, False


def try_evaluate0(aut):
    """
    Try evaluate with K = 0(len of acceptance formula == 0)
    :param aut: spot::automaton
    :return: potentionally zero acceptance spot::automaton
    """
    last_eq_aut = spot.automaton(aut.to_str())
    clear_aut_edges(aut)
    aut.set_acceptance(0, spot.acc_code.t())
    if spot.are_equivalent(last_eq_aut, aut):
        return aut

    aut.set_acceptance(0, spot.acc_code.f())
    if spot.are_equivalent(last_eq_aut, aut):
        return aut
    return last_eq_aut

def play(aut, C, K, mode, timeout):
    print("mode",mode)
    spot.cleanup_acceptance_here(aut)

    if aut.get_acceptance().used_sets().count(
    ) < 1 or aut.prop_state_acc() == spot.trival.yes_value:
        return aut
    original = spot.automaton(aut.to_str())

    # [int] - all nums of inner edges of SCCs
    inner_edges_nums, inner_edges = get_edges(aut)


    # scc_edg [[nums of edges of one scc]]
    # scc state info [{state num : [[num of edge of which is the state source of][num of edge of which is the state destination of]]}]
    scc_state_info, scc_edg = scc_info(aut)

    K = K - 1  # we dont want to try what we already know



    while C > 0 and K > 0:
        print(K)

        if aut.get_acceptance().used_sets().count(
        ) < 1 or aut.prop_state_acc() == spot.trival.yes_value:
            return aut

        # dictionary {edge_num : [num of acceptance set]}
        edge_dict = edge_dictionary(aut)

        acc = PACC(aut.get_acceptance().to_dnf())
        if acc.formula ==  []:
            a = try_evaluate0(aut)
            return a

        # QBF formula is written into ./sat_file

        create_formula(aut, acc, edge_dict, scc_edg, scc_state_info, inner_edges_nums, C, K, inner_edges, mode)

        try:
            cp = subprocess.run(["./qbf/limboole1.2/limboole", "./sat_file"], universal_newlines=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=int(timeout))

        except subprocess.TimeoutExpired:
            print("expired")
            return aut


        out = cp.stdout.splitlines()
        f = open("sat_evaluation", "w")
        f.write(cp.stdout)
        f.close()



        if len(out) == 1:
            print("unsatisfiable")
            return aut


        if len(out) == 0:
            print("sat error")
            return aut
        variables = out[1:]

        process_variables(aut, variables)

        K = K - 1

    # print(aut.to_str())
    a = try_evaluate0(aut)
    return a


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-F",
        "--autfile",
        help="File containing automata in HOA format.")
    parser.add_argument("-O", "--outfile", help="File to print output to.")
    args = parser.parse_args()
    if not args.autfile:
        print("No automata to process.", file=sys.stderr)

    aut = spot.automata(args.autfile)

    for a in aut:

        origin = spot.automaton(a.to_str())
        print_aut(origin, "problem", "w")
        try:
            spot.cleanup_acceptance_here(a)
            acc_sets_count = a.get_acceptance().used_sets().count()
            clauses_count = max(len(a.get_acceptance().top_disjuncts()), len(a.get_acceptance().top_conjuncts()))
            print("formula:", a.get_acceptance(), "C:", clauses_count, "K:", acc_sets_count)

            if acc_sets_count == 0:
                auto = a
            else:
                auto = play(a, clauses_count, acc_sets_count)

            if args.outfile:
                print_aut(auto, args.outfile, "a")
            else:
                print_aut(auto, None, " ")

            if not spot.are_equivalent(auto, origin):
                print("nejsou ekvivalentni")
                return

            else:
                print("ekvivalentni")

        except RuntimeError:  # too many marks
            print(
                "Automaton has too many acceptance sets, 32 is the limit.",
                file=sys.stderr)


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
