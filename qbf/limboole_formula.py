from telatko2.classes import SATformula
import copy


class Boole_f_ctor:
    def __init__(self, edge_dict, scc_edg, scc_edges_nums,
                 scc_state_info, C, K, mode):
        self.univ_vars = []
        self.exist_vars = []
        self.edge_dict = edge_dict
        self.scc_edg = scc_edg
        self.scc_edges_nums = scc_edges_nums

        self.scc_state_info = scc_state_info
        self.inner_edges_nums = [
            num for one_scc_edges_nums in scc_edges_nums for num in one_scc_edges_nums]
        self.C = C
        self.K = K
        self.mode = mode  # level of simplification

    def add_inf_fin(self, impl):
        inf_not_fin = self.inf_is_not_fin_clause()
        inf_or_fin = self.inf_or_fin_f()
        formula = SATformula("&", [impl, inf_not_fin, inf_or_fin])
        return formula

    def get_qbf_formula(self, aut):

        # adds universally quantified variables
        self.quant_all()

        if self.mode == 3:

            self.w_quant()

            laso = self.laso_cycles(aut)
            in_out = self.in_n_out()
            one_scc = self.one_scc_f()
            laso = SATformula("&", [laso, in_out, one_scc])

        elif self.mode == 2:
            laso = self.laso_f(aut)

        else:
            laso = self.one_scc_f()

        # old = self.old_formula(ACC_DNF(aut.get_acceptance().to_dnf()))
        old = self.rec_old_original_shape(aut.get_acceptance(), 'c', 0)
        # old.sanity_checks()

        new = self.new_formula()

        if old is not None:
            eq = self.equivalence_f(old, new)
        else:
            eq = new
        impl = SATformula("->", [laso, eq])
        formula = self.add_inf_fin(impl)

        if self.exist_vars:
            formula = SATformula(
                "?",
                subf_list=[formula],
                quantifier=True,
                quantified_vars=self.exist_vars)
            #formula = Exists(self.exist_vars, formula)
        formula = SATformula(
            "#",
            subf_list=[formula],
            quantifier=True,
            quantified_vars=self.univ_vars)
        #formula = ForAll(self.univ_vars, formula)

        return formula
# NEW CONDITION PART

    def inf_or_fin_f(self):
        clauses_dis = []
        for c in range(1, self.C + 1):
            sets_dis = []
            for k in range(1, self.K + 1):

                p = SATformula('p_' + str(c) + '_' + str(k))
                n = SATformula('n_' + str(c) + '_' + str(k))
                sets_dis.append(SATformula("|", [p, n]))

            clauses_dis.append(SATformula("|", sets_dis))
        return SATformula("|", clauses_dis)

    def inf_is_not_fin_clause(self):
        clauses_con = []
        for c in range(1, self.C + 1):
            set_con = []
            for k in range(1, self.K + 1):
                p = (SATformula(op="p_" + str(c) + "_" + str(k), negate=True))
                n = (SATformula("n_" + str(c) + "_" + str(k), negate=True))
                set_con.append(SATformula("|", [p, n]))
            clauses_con.append(SATformula("&", set_con))
        return SATformula("&", clauses_con)

    def one_fin(self, c, k):
        n = SATformula("n_" + str(c) + "_" + str(k))

        con = []
        for t in self.inner_edges_nums:
            e_var = SATformula("e_" + str(t), negate=True)
            f_var = SATformula("f_" + str(t) + "_" + str(k), negate=True)
            con.append(SATformula("|", [e_var, f_var]))
        return SATformula("->", [n, SATformula("&", con)])

    def one_inf(self, c, k):
        p = SATformula("p_" + str(c) + "_" + str(k))

        dis = []
        for t in self.inner_edges_nums:
            e_var = SATformula("e_" + str(t))
            f_var = SATformula("f_" + str(t) + "_" + str(k))
            dis.append(SATformula("&", [e_var, f_var]))
        return SATformula("->", [p, SATformula("|", dis)])

    def new_formula(self):
        clauses_disj = []
        for c in range(1, self.C + 1):
            sets_conj = []
            for k in range(1, self.K + 1):

                inf = self.one_inf(c, k)
                fin = self.one_fin(c, k)

                sets_conj.append(SATformula("&", [inf, fin]))
            clauses_disj.append(SATformula("&", sets_conj))
        return SATformula("|", clauses_disj)

    def equivalence_f(self, left_f, right_f):
        return SATformula("<->", [left_f, right_f])

    def marks_of_scc(self, edge_dict):
        """
          Edge_dict {mark num : [edges of scc]}
        """
        marks = []
        for key in edge_dict:
            if edge_dict[key]:
                marks.append(key)

        return marks

# OLD CONDITION PART

    def encode_acc_mark(self, acc):
        """
            acc - acceptance condition that has only one literal
            i.e. Fin(x) / Inf(x)

            Returns encoded literal.
        """

        inf, fin = acc.used_inf_fin_sets()
        used_set = acc.used_sets()

        assert (inf == [] or fin == [])
        assert (inf.count() == 1 or fin.count() == 1)
        assert (used_set.count() == 1)

        edges_vars = []

        # spot anomaly, cant extract number of mark the standard way
        # mark_num = -1
        for m in used_set.sets():
            mark_num = m
            break

        if mark_num in self.edge_dict:

            for e in list(set(self.edge_dict[mark_num]) & set(
                    self.inner_edges_nums)):
                var = SATformula("e_" + str(e))
                edges_vars.append(var)

            if edges_vars == []:
                if inf:
                    #  Inf(∅) = False
                    f_var = SATformula("false_var")
                    f_var2 = SATformula("false_var", negate=True)
                    return SATformula("&", [f_var, f_var2])
                    return False
                else:
                    #  Fin(∅) = True
                    t_var = SATformula("true_var")
                    t_var2 = SATformula("true_var", negate=True)
                    return SATformula("|", [t_var, t_var2])
                    return True
            if len(edges_vars) == 1:
                if inf:
                    return edges_vars.pop()
                else:
                    edges_vars[0].negate()
                    return edges_vars.pop()

            literal_formula = SATformula("|", edges_vars)
            if fin:
                literal_formula.negate()

        return literal_formula

    def rec_old_original_shape(self, acc, prev_type, level):

        if acc.top_disjuncts() == acc.top_conjuncts():
            return self.encode_acc_mark(acc)

        subformulas = []
        if prev_type == 'c':
            for a in acc.top_disjuncts():
                subformulas.append(
                    self.rec_old_original_shape(
                        a, 'd', level + 1,))
            return SATformula("|", subformulas)
        else:
            for a in acc.top_conjuncts():
                subformulas.append(
                    self.rec_old_original_shape(
                        a, 'c', level + 1))
            return SATformula("&", subformulas)

# LASO PART

    def disjunct_formula(self, edges):
        # to not to create more complex formula then necesary
        if len(edges) == 1:
            return SATformula(f"e_{str(edges[0])}")
        return SATformula("|", [SATformula("e_" + str(x)) for x in edges])

    def in_n_out(self):
        eq_list = []
        for dict in self.scc_state_info:
            for src_dst in dict.values():
                src = src_dst[0]
                dst = src_dst[1]
                eq_list.append(
                    self.equivalence_f(
                        self.disjunct_formula(dst),
                        self.disjunct_formula(src)))

        return SATformula("&", eq_list)

    def disjunct_formula_list(self, scc_edges_nums):
        
        alist = []
        for i in scc_edges_nums:
            dis = self.disjunct_formula(i)
            dis.negate()
            alist.append(dis)
        return alist

    def one_scc_f(self):
        formula_list = self.disjunct_formula_list(self.scc_edges_nums)
        dis = []
        for i in range(len(formula_list)):
            formula_list[i].negate()
            con = []
            for formula in formula_list:
                f = copy.deepcopy(formula)
                con.append(f)

            formula_list[i].negate()
            dis.append(SATformula("&", con))
        return SATformula("|", dis)

    def laso_f(self, aut):

        in_out = self.in_n_out()

        # edges that are true are in one SCC and none of edges from other SCCs is
        # true
        one_scc = self.one_scc_f()
        #least_one_edge = self.disjunct_formula(self.inner_edges_nums)

        laso = SATformula("&", [in_out, one_scc])
        return laso

    def laso_cycles(self, aut):
        main_dis = []
        con1, con2, con3 = [], [], []
        dis1, dis2 = [], []
        for alist in self.scc_edg:
            for e in alist:
                # part one -- both adges in group w
                src = str(e.src)
                dst = str(e.dst)
                c = SATformula(
                    "&", [SATformula("w_" + src), SATformula("w_" + dst)])
                impl = SATformula(
                    "->", [SATformula("e_" + str(aut.edge_number(e))), c])
                con1.append(impl)

                # part two -- both edges not in group w

                c1 = SATformula(
                    "&", [SATformula("w_" + src, negate=True), SATformula("w_" + dst, negate=True)])
                con2.append(SATformula(
                    "->", [SATformula("e_" + str(aut.edge_number(e))), c1]))

                # part three -- one edge in w, other one not
                # dis1
                c2 = SATformula("&", [SATformula("e_" + str(aut.edge_number(e))),
                                      SATformula("w_" + src), (SATformula("w_" + dst, negate=True))])
                dis1.append(c2)

                # dis2
                c3 = SATformula("&", [SATformula("e_" + str(aut.edge_number(e))),
                                      (SATformula("w_" + src, negate=True)), SATformula("w_" + dst)])
                dis2.append(c3)

        con3.append(SATformula("|", dis1))
        con3.append(SATformula("|", dis2))

        main_dis.append(SATformula("&", con1))
        main_dis.append(SATformula("&", con2))
        main_dis.append(SATformula("&", con3))

        laso = SATformula("|", main_dis)

        return laso
# QUANTIFIED PART

    def w_quant(self):
        for dict in self.scc_state_info:
            for key in dict:
                var = ("w_" + str(key))
                self.exist_vars.append(var)

    def quant_all(self):
        for e in self.inner_edges_nums:
            var = ("e_" + str(e))
            self.univ_vars.append(var)
