
from telatko2.classes import *
from telatko2.simplify import *
import copy
import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)


def shift_fst_acc(aut, acc, scc, m):
    next_m = m + 1
    log = {}
    #

    for dis in acc.formula:
        for con in dis:
            if con.num in log:
                con.num = log[con.num]
            else:
                add_dupl_marks(aut, scc, con.num, next_m)
                log[con.num] = next_m
                con.num = next_m
                next_m += 1
    scc_clean_up_edges(aut, acc, scc)


def count_cost(dis1, dis2):
    inf, fin = 0, 0
    for con in dis1:
        if con.type == MarkType.Inf:
            inf -= 1
        else:
            fin -= 1
    for con in dis2:
        if con.type == MarkType.Inf:
            inf += 1
        else:
            fin += 1
    if inf < 0:
        inf = 0
    if fin < 0:
        fin = 0
    return inf + fin


def make_matrix(acc1, acc2):
    m = []
    for i in range(len(acc1)):
        row = []
        for j in range(len(acc1)):
            if j >= len(acc2):
                row.append(0)
            else:
                row.append(count_cost(acc1[i], acc2[j]))
        m.append(row)
    return m


def replace_marks(aut, scc, origin_m, new_m):
    for s in scc.states():
        for e in aut.out(s):
            if e.dst in scc.states() and origin_m in e.acc.sets():
                e.acc.clear(origin_m)
                if new_m not in e.acc.sets():
                    e.acc.set(new_m)


def longest_expr_in_acc(acc):
    max = 0
    for expr in acc.formula:
        if len(expr) > max:
            max = len(expr)
    return max


def partition(accs, sccs, low, high):
    """
    Formula is in dnf, len == number of disjuncts
    Args:
        accs: list of acceptance formulas
        sccs: list of sccs corressponding to accs
        low: int
        high: int

    Returns:

    """
    i = (low - 1)
    pivot = len(accs[high])

    for j in range(low, high):
        if len(accs[j]) > pivot:
            i += 1
            accs[i], accs[j] = accs[j], accs[i]
            sccs[i], sccs[j] = sccs[j], sccs[i]
        elif len(accs[j]) == pivot and longest_expr_in_acc(accs[j]) > longest_expr_in_acc(accs[high]):
            # longest disjunct in acc
            i += 1
            accs[i], accs[j] = accs[j], accs[i]
            sccs[i], sccs[j] = sccs[j], sccs[i]

    accs[i + 1], accs[high] = accs[high], accs[i + 1]
    sccs[i + 1], sccs[high] = sccs[high], sccs[i + 1]
    return (i + 1)


def acc_quicksort(accs, sccs, low, high):
    """
    Sorts accs and sccs(correspondingly to accs). Acc formulas are in DNF.
    Primary key is length of formula, aka number of disjuncts.
    Secondary key is length of longest disjunct in formula.
    Args:
        accs: list of acceptance formulas
        sccs: list of sccs corressponding to accs
        low:
        high:

    Returns:

    """
    if low < high:
        pi = partition(accs, sccs, low, high)

        acc_quicksort(accs, sccs, low, pi - 1)
        acc_quicksort(accs, sccs, pi + 1, high)


def place_con(dis, con, used, dis_remaining):
    if con in dis and not used[dis.index(con)]:
        return dis.index(con)
    # list of numbers of marks that remain unpaired (whatever comes after the
    # current conjunct in the clause)
    remaining = []
    for c in dis_remaining:
        if con == c or remaining:
            remaining.append(c.num)

    for i in range(len(dis)):
        if dis[i].type == con.type and not used[i] and dis[i].num not in remaining:
            return i

    for i in range(len(dis)):
        if dis[i].type == con.type and not used[i]:
            return i
    return None


def get_short_accs(aut, accs):
    """

    :param aut:
    :param accs: simplified accs in DNF
    :return: simplified accs in original(short) form
    """
    short_accs = []
    orig = aut.get_acceptance()
    for a in accs:
        if orig.is_cnf():
            if a.sat is None:
                to_be_removed = []
                new_acc = ACC_CNF(aut.get_acceptance())
                for i in range(len(new_acc.formula)):
                    expr = new_acc.formula[i]
                    for z in range(len(expr)):
                        one = expr[z]
                        if one.num not in a.int_list():
                            to_be_removed.append((one.num, i))

                for item, index in to_be_removed:
                    new_acc.rem_from_expr(index, item)

                new_acc.formula = list(filter(None, new_acc.formula))
                new_acc.sat = a.sat
                new_acc.resolve_redundancy()
                short_accs.append(new_acc)
            else:
                new_acc = ACC_CNF(aut.get_acceptance())
                new_acc.formula = []
                new_acc.sat = a.sat
                short_accs.append(new_acc)
        else:
            short_accs.append(a)
    return short_accs


def mergeable(merged_f, acc):
    """

    :param merged_f: future acc of simplified automata
    :param acc: acc to merge on merged_f
    :return: log{acc_index : merged_f index}
    """
    m = make_matrix(merged_f, acc)
    row_i, col_i = linear_sum_assignment(m)
    # col_i, row_i = (list(t) for t in zip(*sorted(zip(col_i, row_i))))
    log = {}
    for i in range(len(row_i)):
        if col_i[i] < len(acc):
            log[col_i[i]] = row_i[i]
    return log


def get_set_nums(expr):
    """

    :param expr: one conjunct(cnf) or disjunct(dnf)
    :return: list of present ACCMark.num in expression
    """
    nums = []
    for one in expr:
        nums.append(one.num)
    return nums


def shift_first_acc(acc, m):
    """
    Shifts base acc formula so there is no intersection with original formula.
    example: Fin(3) | Inf(4) >> Fin(5) | Fin(6)
    :param acc:
    :param m: max set number of original acc formula
    :return:
    """
    next_m = m + 1
    log = {}

    for dis in acc.formula:
        for con in dis:
            if con.num in log:
                con.num = log[con.num]
            else:
                log[con.num] = next_m
                con.num = next_m
                next_m += 1


def place_ACCset(literal, expr, used):
    """
    Returns index of disjunkt from m_con(conjunct in merged_f) on which will be mapped dis
    :param one: disjunct or conjunct(ACCMark)
    :param expr: conjunct or disjunct of ACCMarks
    :param used: bool if certain ACCMark was already used
    :return:
    """
    for i in range(len(expr)):
        if literal.type == expr[i].type and not used[i]:
            return i


def duplicate(merged_f, aut, scc, one, m_scc, m_expr, index):
    """
    Exchanges one acceptance set from merged_f with new one.
    Args:
        merged_f:
        aut:
        scc:
        one: ACCMark from expression
        m_scc: SCC that belongs to original merged_f
        m_expr: expression from merged_f
        index: index in m_expr on which will be "one" mapped

    Returns:

    """
    new_num = merged_f.max() + 1
    add_dupl_marks(aut, scc, one.num, new_num)
    # proc je zde tohle?
    add_dupl_marks(aut, m_scc, m_expr[index].num, new_num)
    m_expr[index].num = new_num


def map_paired(aut, m_expr, expr, scc, merge_log,
               merged_f, m_scc, dependencies):
    """
    Maps those disjuncts, which are mergable.
    :param aut:
    :param m_expr: conjunct/disjunct from merged_f on which will be mapped
    :param expr: con/dis to be mapped
    :param scc: scc2
    :param merge_log: report about merge
    :return:
    """
    used = [False] * len(m_expr)
    for j in range(len(expr)):
        one = expr[j]
        # na ktery literal z m_expr se namapuje literal z expr
        index = place_ACCset(one, m_expr, used)
        #print(one.num, index)
        if index is None:
            used.append(True)
            new_num = merged_f.max() + 1
            merge_log[one.num] = new_num
            new_one = ACCMark(one.type, new_num)
            m_expr.append(new_one)
            add_dupl_marks(aut, scc, one.num, new_num)

        else:
            used[index] = True
            # on one acc set are mapped two acc sets from expr
            if m_expr[index].num in merge_log.values():
                for key in merge_log.keys():
                    # acc sets are different (otherwise already mapped)
                    if merge_log[key] == m_expr[index].num and key != one.num:
                        # Creates new acceptance set in merged_f
                        duplicate(
                            merged_f, aut, scc, one, m_scc, m_expr, index)
            else:
                # adds mark from merged_f to the edges
                merge_log[one.num] = m_expr[index].num
                add_dupl_marks(aut, scc, one.num, m_expr[index].num)
        """
        for i in range(j + 1):
            m_one = m_expr[i]
            if not used[i] and m_one.num in merge_log.values():
                if any(used):
                    duplicate(merged_f, aut, scc, one, m_scc, m_expr, i)
        """

    unpaired_dependencies = []

    # Why not this???
    for i in range(len(m_expr)):
        m_one = m_expr[i]
        if not used[i] and m_one.num in merge_log.values():
            if any(used):
                duplicate(merged_f, aut, scc, one, m_scc, m_expr, i)
        elif not used[i] and m_one.num in dependencies:
            unpaired_dependencies.append(m_one)
    return unpaired_dependencies


def new_merge(
        aut,
        merged_f,
        acc,
        pairing_log,
        scc,
        m_scc,
        dependencies,
        unmaped_dependence, sccs):
    """
    fce that merges conjuncts or disjuncts on merged_f
    :param aut:
    :param merged_f: base acc formula
    :param acc: acc to be merged on merged_f
    :param pairing_log: dict {acc index, merged_f index}
    :param scc:
    :return: {int(previous number) : int(new_number)}
    """
    merge_log = {}  # which number of acceptance set is mapped on which
    unmaped_dep_log = {}  # index of expr : ACCMark.num
    not_paired_dependencies = {}  # index of expr(clause) : ACCMark.num
    used = [False] * len(merged_f)
    for i in range(len(acc)):
        expr = acc.formula[i]
        if i in pairing_log:
            used[pairing_log[i]] = True
            # returns list of unpaired dependencies
            not_paired_dependencies[pairing_log[i]] = map_paired(aut,
                                                                 merged_f.formula[pairing_log[i]],
                                                                 expr,
                                                                 scc,
                                                                 merge_log,
                                                                 merged_f, m_scc, dependencies)
    #print("used: ", used)
    for j in range(len(merged_f)):
        if not used[j]:
            for literal in merged_f.formula[j]:
                if literal.num in dependencies and literal.num in merge_log.values():
                    unmaped_dep_log[j] = literal.num
    unmaped_dependence.append(unmaped_dep_log)
    """
    for index in not_paired_dependencies:
        for literal in not_paired_dependencies[index]:
            if literal.num in merge_log.values():
                for m_one in merged_f[index]:
                    if literal == m_one:
                        #duplicate(merged_f, aut, scc, literal, m_scc, merged_f[index], index)
                        new_num = merged_f.max() + 1
                        literal.num = new_num
    """
    return merge_log


def clauses_mapping(merged_f, acc):
    m = make_matrix(merged_f, acc)
    row_i, col_i = linear_sum_assignment(m)
    # col_i, row_i = (list(t) for t in zip(*sorted(zip(col_i, row_i))))
    log = {}
    for i in range(len(row_i)):
        if col_i[i] < len(acc):
            log[col_i[i]] = row_i[i]
            acc.clauses_mapping[col_i[i]] = row_i[i]
    return log


def map_paired2(m_clause, acc, clause_index, merge_log, merged_f):
    # clause from acc
    clause = acc.formula[clause_index]

    # keeps track which literals from m_clause had been already mapped
    used = [False] * len(m_clause)

    for literal_index in range(len(clause)):
        literal = clause[literal_index]
        index = place_ACCset(literal, m_clause, used)

        if index is None:
            used.append(True)
            new_num = merged_f.max() + 1
            m_clause.append(ACCMark(literal.type, new_num))
            # index of literal in merged_f
            literal.set_map_literal(len(m_clause) - 1)
            merge_log[literal.num] = new_num
            # acc.literals_mapping[clause_index][literal_index] = len(m_clause) - 1
        else:
            used[index] = True
            literal.set_map_literal(index)
            if m_clause[index].num in merge_log.values():
                for key in merge_log.keys():
                    # acc sets are different
                    if merge_log[key] == m_clause[index].num and key != literal.num:
                        # Creates new acceptance set in merged_f
                        new_num = merged_f.max() + 1
                        m_clause[index].num = new_num
                        #merge_log[literal.num] = new_num
                        # break

            else:
                # adds mark from merged_f to the edges
                merge_log[literal.num] = m_clause[index].num

    """
    for i in range(len(m_clause)):
        m_literal = m_clause[i]
        if not used[i] and m_literal.num in merge_log.values():
            if any(used):
                duplicate(merged_f, aut, scc, one, m_scc, m_expr, i)
    """


def set_map_clause_index(clause, index):
    for literal in clause:
        literal.set_map_clause(index)


def test_mapping(acc):
    #print("acc: ", acc)
    for clause in acc.formula:
        for literal in clause:
            # print(literal)
            # print(literal.map_clause_index)
            # print(literal.map_literal_index)
            assert(literal.map_clause_index is not None)
            assert(literal.map_literal_index is not None)


def get_mapping(merged_f, acc):
    # inserts mapping positions into acc.clauses_mapping
    pairing_log = clauses_mapping(merged_f, acc)
    merge_log = {}

    for clause_index in pairing_log:

        set_map_clause_index(
            acc.formula[clause_index],
            pairing_log[clause_index])
        map_paired2(merged_f.formula[pairing_log[clause_index]],
                    acc, clause_index, merge_log, merged_f)
    #print("merged_f: ", merged_f)
    #print("acc: ", acc)
    # print(merge_log)


def duplicate_marks(aut, merged_f, acc, sccs):
    #print("merged_f: ", merged_f)
    #print("acc: ", acc)
    for clause in acc.formula:
        for literal in clause:
            m_literal = merged_f.formula[literal.map_clause_index][literal.map_literal_index]
            add_dupl_marks(aut, sccs[acc.scc_index],
                           literal.num, m_literal.num)

            #print("old: ", literal.num, " new: ", m_literal.num)


def resolve_unused_clause_dep(aut, scc, merged_f, acc):
    #print("clause map vls: ", (merged_f.clauses_mapping))
    unused_dep_log = {}
    for m_clause_index in range(len(merged_f)):
        m_clause = merged_f[m_clause_index]
        if m_clause_index not in list(acc.clauses_mapping.values()):
            for i in range(len(m_clause)):
                m_literal = m_clause[i]
                if m_literal.num in merged_f.dependencies:
                    if any(
                            m_lit.num not in merged_f.dependencies for m_lit in m_clause):
                        unused_dep_log[m_clause_index] = m_literal.num
                    else:
                        # continue
                        new_num = merged_f.max() + 1
                        add_dupl_marks(aut, scc, m_literal.num, new_num)
                        new_lit = ACCMark(m_literal.type, new_num)
                        merged_f[m_clause_index][i] = new_lit
    return unused_dep_log


def get_index(m_clause_index, m_lit_num, merged_f):

    #print("indeices: c = ", m_clause_index, " l = ", m_lit_num, merged_f)
    m_clause = merged_f.formula[m_clause_index]
    for i in range(len(m_clause)):
        if m_clause[i].num == m_lit_num:
            return i
    # If we get here merged_f.dependencies have wrong clause index in values
    assert(False)


def is_mapped(m_clause_index, m_lit_index, acc):
    """
        Return value:
            True -- used clause, mapped on literal
            False -- used clause, not mapped on literal
            None -- unused clause
    """

    if m_clause_index not in list(acc.clauses_mapping.values()):
        return None

    for key in acc.clauses_mapping:
        value = acc.clauses_mapping[key]
        if value == m_clause_index:
            for lit in acc.formula[key]:
                if lit.map_literal_index == m_lit_index:
                    assert(value == lit.map_clause_index)
                    return True
    return False


def resolve_unmapped_dep_lit(aut, scc, merged_f, acc):
    #print("merged_f.dependencies: ", merged_f.dependencies)
    for m_lit_num in merged_f.dependencies:
        indices = []
        used_clauses = 0

        for m_clause_index in merged_f.dependencies[m_lit_num]:
            m_lit_index = get_index(m_clause_index, m_lit_num, merged_f)

            is_m_lit_mapped = is_mapped(m_clause_index, m_lit_index, acc)
            #print(m_lit_index, m_clause_index, is_m_lit_mapped)
            if is_m_lit_mapped is not None:
                used_clauses += 1
                if is_m_lit_mapped == False:
                    # append indices of unmapped literals
                    indices.append((m_clause_index, m_lit_index))

        if used_clauses > len(indices):
            new_num = merged_f.max() + 1
            for cl_index, lit_index in indices:
                new_lit = ACCMark(merged_f[cl_index][lit_index].type, new_num)
                add_dupl_marks(
                    aut, scc, merged_f[cl_index][lit_index].num, new_num)

                merged_f[cl_index][lit_index] = new_lit


def resolve_dependencies(aut, merged_f, short_accs, sccs):
    unused_clauses_depend = []
    # update of dependencies, might have changed during mapping

    for acc in short_accs:
        if acc.sat is not None or not acc.formula:
            unused_clauses_depend.append({})
            continue

        scc = sccs[acc.scc_index]
        merged_f.get_dependencies()
        resolve_unmapped_dep_lit(aut, scc, merged_f, acc)
        merged_f.get_dependencies()

        unused_dep_log = {}

        unused_dep_log = resolve_unused_clause_dep(aut, scc, merged_f, acc)
        # print(unused_dep_log)
        unused_clauses_depend.append(unused_dep_log)
        # update of dependencies, might have changed during
        # resolve_unused_clause_dep
    return unused_clauses_depend
