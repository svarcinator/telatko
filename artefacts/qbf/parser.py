from telatko2.classes import *
from z3 import is_true


def create_acc(variables):
    """

    Args:
        variables [[{Variable}]]: list of lists of variables - each var in list has the same clause number.

    Returns:
        [[MarkType]] - list of list of MartType of the same structure as input

    """
    acc = []
    for dis in variables:
        disjunct = []
        for con in dis:
            if con.type == 'p':
                disjunct.append(ACCMark(MarkType.Inf, con.set))
            else:
                disjunct.append(ACCMark(MarkType.Fin, con.set))

        acc.append(disjunct)
    return acc


def string_formula(acc):
    """
    Returns string interpretation
    Args:
        acc [[MarkType]]:  acceptance condition

    Returns: string - string interpretation of input acc

    """
    f = []
    for dis in acc:
        f.append('(')
        for con in dis:
            f.append(str(con))
            if con is not dis[-1]:
                f.append(" & ")
        f.append(')')
        if dis is not acc[-1]:
            f.append(" | ")
    return ''.join(f)


def prepare_acc_vars(acc_vars):
    """

    Args:
        acc_vars[string]: list of variables, that represent future acceptance condition
        and were labeled as true by SAT solver

    Returns:
        [[Variable]] - each sublist contains {Variable}s with the same conjunct number

    """
    condition_vars_class = list(
        map(lambda var: Variable(var.split('_')), acc_vars))
    condition_vars_class.sort(key=lambda x: x.clause, reverse=False)
    clause_num = condition_vars_class[0].clause
    clause_max_num = condition_vars_class[-1].clause
    var_list = []
    while clause_num != (clause_max_num + 1):
        var_list.append(
            list(
                filter(
                    lambda x: x.clause == clause_num,
                    condition_vars_class)))

        clause_num += 1
    return var_list


def clear_aut_edges(aut):
    for e in aut.edges():
        e.acc = spot.mark_t()


def print_edges(aut):
    for edge in aut.edges():
        print("edges[{e}].src={src}, edges[{e}].dst={dst}, edges[{e}].acc={acc}".format(
            e=aut.edge_number(edge), src=edge.src, dst=edge.dst, acc=edge.acc))


def parse_dict(f_list):
    """
    Decodes f variables and saves them as dictionary
    Args:
        f_list[String]: f_t_k = acceptance mark number k is on edge t

    Returns:

    """
    f_dict = {}

    for item in f_list:

        item = item.split('_')
        if int(item[1]) not in f_dict.keys():
            f_dict[int(item[1])] = [int(item[2].split('=')[0])]
        else:
            f_dict[int(item[1])].append(int(item[2].split('=')[0]))
    return f_dict


def marks_on_edges(aut, f_dict):
    """
    Puts marks on edges.
    Args:
        aut:
        f_dict: dictionary {edge number : [acceptance set number]}

    Returns:

    """
    for e in aut.edges():
        if aut.edge_number(e) in f_dict.keys():
            alist = f_dict[aut.edge_number(e)]
            for num in alist:
                e.acc.set(num)


def process_f_variables(aut, acc_set_vars):
    """
    Decodes variables denoted as f_t_k, which means: acc. set number k is on edge t.
    Args:
        aut:
        acc_set_vars[String]: SAT-variables that has been assigned as true

    Returns:

    """
    # removes all acceptance marks from edges
    clear_aut_edges(aut)
    # creates dictionary {edge number : [acceptance set number]}
    f_dict = parse_dict(acc_set_vars)

    # puts marks corresponding to dict on edges
    marks_on_edges(aut, f_dict)
    return f_dict


def max_set_num(acc):
    """
    Maximal number of accepting set in acceptance formula.
    Args:
        acc [[MarkType]] : acc formula

    Returns:

    """
    num = acc[0][0].num
    for dis in acc:
        for con in dis:
            if con.num > num:
                num = con.num
    return num


def parse_limboole(model):
    # list of variables that are true and are denoted as p/n - acceptance
    # condition variables
    condition_vars = list(filter(lambda var: (
        var[0] == "p" or var[0] == "n") and var[-1] == '1', model))
    # list of variables that are true and denoted as f - acceptance sets
    acc_set_vars = list(
        filter(lambda var: var[0] == "f" and var[-1] == '1', model))

    return condition_vars, acc_set_vars


def parse_z3(model):

    condition_vars = []
    acc_set_vars = []
    for t in model.decls():
        if is_true(model[t]):
            if str(t)[0] == 'p' or str(t)[0] == 'n':
                condition_vars.append(str(t))
            elif str(t)[0] == 'f':
                acc_set_vars.append(str(t))

    return condition_vars, acc_set_vars


def clone_to_representant(aut, f_dict, scc_equiv_edges):
    for scc_dict in scc_equiv_edges:
        for val in scc_dict.values():
            if aut.edge_number(val[0]) in f_dict:
                for m in f_dict[aut.edge_number(val[0])]:
                    for e in val[1:]:
                        e.acc.set(m)


def process_variables(aut, model, scc_equiv_edges, mode):
    """
    Filters SAT-variables that are true and splits them. Then calls functions to process these variables.
    Args:
        aut: input automata
        model: output from SAT-solver
        qbf_solver : type of solver (solver output)

    Returns:

    """

    condition_vars, acc_set_vars = parse_z3(model)

    # returns acceptance condition [[MarkType]]
    acc = create_acc(prepare_acc_vars(condition_vars))

    # puts new acceptance marks on edges and removes old acc. marks
    f_dict = process_f_variables(aut, acc_set_vars)
    if mode == 1:
        clone_to_representant(aut, f_dict, scc_equiv_edges)

    max_num = max_set_num(acc)

    aut.set_acceptance(max_num + 3, spot.acc_code(string_formula(acc)))

    spot.cleanup_acceptance_here(aut)


def print_aut(aut, output, m):
    """
    Prints automata to given output
    Args:
        aut:
        output:
        m: mode

    Returns:

    """
    if output is not None:
        f = open(output, m)
        f.write(aut.to_str() + '\n')
        f.close()
    else:
        print(aut.to_str())
