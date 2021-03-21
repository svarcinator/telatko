import random
from qbf.classes import *
from qbf.parser import process_variables


def create_one_inf_clause(clause, acc_set, T, sequence_num, sequence):
    """
    Create formula in shape of :
    p_ck -> (|_1<=t<=T (f_tk & e_ts)
    Args:
        clause: num of clause
        acc_set: num of acc set
        T: count of all edges
        sequence_num: num of sequence

    Returns:

    """
    seq = sequence[sequence_num - 1]
    s = str(sequence_num)
    c = str(clause)
    k = str(acc_set)
    impl = SATformula('->')
    impl.add_subf(SATformula('p_' + c + '_' + k))

    disjunction = SATformula('|')
    for t in seq:
        conj = SATformula('&')
        conj.add_subf(SATformula('f_' + str(t) + '_' + k))
        conj.add_subf(SATformula('e_' + str(t) + '_' + s))
        disjunction.add_subf(conj)
    impl.add_subf(disjunction)
    return impl


def create_one_fin_clause(clause, acc_set, T, sequence_num, sequence):
    """
    Create formula in shape of :
    n_ck -> (&_1<=t<=T (!f_tk | !e_ts)
    Args:
        clause: num of clause
        acc_set: num of acc set
        T: count of all edges
        sequence_num: num of sequence

    Returns:

    """
    seq = sequence[sequence_num - 1]
    s = str(sequence_num)
    c = str(clause)
    k = str(acc_set)
    impl = SATformula('->')
    impl.add_subf(SATformula('n_' + c + '_' + k))

    conjunction = SATformula('&')
    for t in seq:
        disj = SATformula('|')
        disj.add_subf(SATformula('!f_' + str(t) + '_' + k))
        disj.add_subf(SATformula('!e_' + str(t) + '_' + s))
        conjunction.add_subf(disj)
    impl.add_subf(conjunction)
    return impl


def iteration_over_inf_fin_clauses(
        clauses_count,
        acc_sets_count,
        edges_count,
        sequence_num,
        sequence):
    """
    Formula in shape:
    |_C &_K ((p_ck -> |(f_tk & e_ts)) & (n_ck -> &(!f_tk | !e_ts)))
    Args:
        clauses_count:
        acc_sets_count:
        edges_count:
        sequence_num:

    Returns:

    """

    clauses_disj = SATformula('|')
    for c in range(1, clauses_count + 1):
        sets_conj = SATformula('&')
        for k in range(1, acc_sets_count + 1):
            conj = SATformula('&')
            conj.add_subf(
                create_one_inf_clause(
                    c,
                    k,
                    edges_count,
                    sequence_num,
                    sequence))
            conj.add_subf(
                create_one_fin_clause(
                    c,
                    k,
                    edges_count,
                    sequence_num,
                    sequence))
            sets_conj.add_subf(conj)
        clauses_disj.add_subf(sets_conj)
    return clauses_disj


def inf_is_not_fin_clause(
        clauses_count,
        acc_sets_count, ):
    """
    Formula in shape of:
    &_1<=c<=C (&_1<=k<=K (!p_ck | !n_ck))
    Args:
        clauses_count:
        acc_sets_count:
        edges_count:
        sequence_num:

    Returns:

    """

    clauses_conj = SATformula('&')
    for c in range(1, clauses_count + 1):
        sets_conj = SATformula('&')
        for k in range(1, acc_sets_count + 1):
            disj = SATformula('|')
            disj.add_subf(SATformula('!p_' + str(c) + '_' + str(k)))
            disj.add_subf(SATformula('!n_' + str(c) + '_' + str(k)))
            sets_conj.add_subf(disj)
        """
        for k in range(1, acc_sets_count + 1):
            disj2 = SATformula('|')
            disj2.add_subf(SATformula('p_' + str(c) + '_' + str(k)))
            disj2.add_subf(SATformula('n_' + str(c) + '_' + str(k)))
            sets_conj.add_subf(disj2)
        """

        clauses_conj.add_subf(sets_conj)
    return clauses_conj


def create_new_formula(
        clauses_count,
        acc_sets_count,
        edges_count,
        sequence_num,
        sequence):
    """
    Formula:
    &_1<=c<=C (&_1<=k<=K (!p_ck | !n_ck))
    &
    |_1<=c<=C &_1<=k<=K ((p_ck -> |(f_tk & e_ts)) & (n_ck -> &(!f_tk | !e_ts)))
    Args:
        clauses_count:
        acc_sets_count:
        edges_count:
        sequence_num:

    Returns:

    """
    conjunction = SATformula('&')

    conjunction.add_subf(
        iteration_over_inf_fin_clauses(
            clauses_count,
            acc_sets_count,
            edges_count,
            sequence_num,
            sequence))
    return conjunction


def create_old_formula(acc, edge_dict, sequence_num):
    """

    Args:
        acc: Original acceptance condition in DNF
        edge_dict: Dictionary with number of acceptance set : numbers of edges that the acceptance set contains
        edges_count: Number of all edges.
        sequence_num: Number of current sequence

    Returns: Formula

    """

    disjunct_f = SATformula('|')
    for dis in acc.formula:
        conjunct_f = SATformula('&')
        for con in dis:
            new_shape = None
            if con.type == MarkType.Inf:
                new_shape = SATformula('|')
                for edge in edge_dict[con.num]:
                    new_shape.add_subf(
                        SATformula(
                            "e_" +
                            str(edge) +
                            '_' +
                            str(sequence_num)))
            else:
                new_shape = SATformula('&')
                for edge in edge_dict[con.num]:
                    new_shape.add_subf(
                        SATformula(
                            "!e_" +
                            str(edge) +
                            '_' +
                            str(sequence_num)))
            conjunct_f.add_subf(new_shape)
        disjunct_f.add_subf(conjunct_f)
    return disjunct_f





def create_equivalence_formula(old_formula, new_formula):
    equiv = SATformula('<->')
    equiv.add_subf(old_formula)
    equiv.add_subf(new_formula)
    return equiv


def for_all_sequences(
        acc,
        edge_dict,
        C,
        K,
        edges_count,
        sequence_count,
        sequence):
    """
    Creates formula for every sequence in automaton
    Args:
        acc: original acceptance formula in DNF
        edge_dict {number of acceptance set : [number of edge that is in this acc set]}:
        clauses_count: number of clauses from input
        acc_sets_count: number of sets from input
        edges_count: number of edges
        sequence_count: number denoting current sequence
        sequence: sequence of curret edges

    Returns:

    """

    formula = SATformula('&')
    for s in range(1, sequence_count + 1):
        formula.add_subf(
            create_equivalence_formula(
                create_old_formula(
                    acc, edge_dict, s), create_new_formula(
                    C, K, edges_count, s, sequence)))
    return formula


def create_requirements_f(sequences, T):
    """
    Adds e_t_s if edge t is present in sequence s otherwise adds negation
    Args:
        sequences: current sequence
        T: number of all edges in automaton

    Returns: part of SAT-formula

    """
    formula = SATformula('&')
    for i in range(len(sequences)):
        seq = sequences[i]
        for t in range(1, T + 1):
            if t in seq:
                formula.add_subf(SATformula('e_' + str(t) + '_' + str(i + 1)))
            else:
                formula.add_subf(SATformula('!e_' + str(t) + '_' + str(i + 1)))
    return formula


def create_SAT_f(all_sekv_f, requirements_f):
    """

    Args:
        all_sekv_f: Formula representing relationship of variables
        requirements_f: formula representing information about automaton

    Returns: SAT formula - input to SAT-solvet

    """
    sat_f = SATformula('&')
    sat_f.add_subf(all_sekv_f)
    sat_f.add_subf(requirements_f)
    return sat_f


def inf_or_fin_f(
        clauses_count,
        acc_sets_count, ):
    """
    Formula in shape of:
    &_1<=c<=C (&_1<=k<=K (p_ck | n_ck))
    Args:
        clauses_count:
        acc_sets_count:
        edges_count:
        sequence_num:

    Returns:

    """

    clauses_dis = SATformula('&')
    for c in range(1, clauses_count + 1):
        sets_dis = SATformula('&')
        for k in range(1, acc_sets_count + 1):
            disj = SATformula('|')
            disj.add_subf(SATformula('p_' + str(c) + '_' + str(k)))
            disj.add_subf(SATformula('n_' + str(c) + '_' + str(k)))
            sets_dis.add_subf(disj)

        clauses_dis.add_subf(sets_dis)
    return clauses_dis




