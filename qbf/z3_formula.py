from z3 import *
from telatko2.classes import ACC, ACC_DNF, MarkType


class Z3_f_ctor:
    def __init__(self, edge_dict, scc_edg,scc_edges_nums, scc_state_info, C, K, mode):
        self.univ_vars = []
        self.exist_vars = []
        self.edge_dict = edge_dict
        self.scc_edg = scc_edg
        self.scc_edges_nums = scc_edges_nums

        self.scc_state_info = scc_state_info
        self.inner_edges_nums = [num for one_scc_edges_nums in scc_edges_nums for num in one_scc_edges_nums]
        self.C = C
        self.K = K
        self.mode = mode  # level of simplification

    def add_inf_fin(self, impl):
        inf_not_fin = self.inf_is_not_fin_clause()
        inf_or_fin = self.inf_or_fin_f()
        inf_not_fin = simplify(inf_not_fin)
        inf_or_fin = simplify(inf_or_fin)
        formula = And(impl, inf_not_fin, inf_or_fin)
        return formula

    
    def get_qbf_formula(self, aut):


        # adds universally quantified variables
        self.quant_all()
    

        if self.mode == 3:

            self.w_quant()

            laso = self.laso_cycles(aut)
            laso = simplify(laso)
            #in_out = self.in_n_out()
            #one_scc = self.one_scc_f()
            #laso = And(laso, in_out, one_scc)
            least_one_edge = self.disjunct_formula( self.inner_edges_nums)
            laso = And(laso, least_one_edge)

        elif self.mode == 2:
            laso = self.laso_f(aut)

        else: 
            #laso = self.laso_f(aut)
            laso = self.disjunct_formula( self.inner_edges_nums)

        old = self.old_formula(ACC_DNF(aut.get_acceptance().to_dnf()))

        new = self.new_formula()

        new = simplify(new)

        laso = simplify(laso)

        if old is not None:
            old = simplify(old)
            eq = self.equivalence_f(old, new)
        else:
            eq = new
        impl = Implies(laso, eq)
        formula = self.add_inf_fin(impl)
        if self.exist_vars:
            formula = Exists(self.exist_vars, formula)

        formula = ForAll(self.univ_vars, formula)

        return formula

# NEW CONDITION PART

    def inf_or_fin_f(self):
        clauses_dis = []
        for c in range(1, self.C + 1):
            sets_dis = []
            for k in range(1, self.K + 1):

                p = Bool('p_' + str(c) + '_' + str(k))
                n = Bool('n_' + str(c) + '_' + str(k))
                sets_dis.append(Or(p, n))

            clauses_dis.append(Or(sets_dis))
        return Or(clauses_dis)

    def inf_is_not_fin_clause(self):
        clauses_con = []
        for c in range(1, self.C + 1):
            set_con = []
            for k in range(1, self.K + 1):
                p = Not(Bool("p_" + str(c) + "_" + str(k)))
                n = Not(Bool("n_" + str(c) + "_" + str(k)))
                set_con.append(Or(p, n))
            clauses_con.append(And(set_con))
        return And(clauses_con)

    def one_fin(self, c, k):
        n = Bool("n_" + str(c) + "_" + str(k))

        con = []
        for t in self.inner_edges_nums:
            e_var = Bool("e_" + str(t))
            f_var = Bool("f_" + str(t) + "_" + str(k))
            con.append(Or(Not(e_var), Not(f_var)))
        return Implies(n, And(con))

    def one_inf(self, c, k):
        p = Bool("p_" + str(c) + "_" + str(k))

        dis = []
        for t in self.inner_edges_nums:
            e_var = Bool("e_" + str(t))
            f_var = Bool("f_" + str(t) + "_" + str(k))
            dis.append(And(e_var, f_var))
        return Implies(p, Or(dis))

    def new_formula(self):
        clauses_disj = []
        for c in range(1, self.C + 1):
            sets_conj = []
            for k in range(1, self.K + 1):

                inf = self.one_inf(c, k)
                fin = self.one_fin(c, k)

                sets_conj.append(And(inf, fin))
            clauses_disj.append(And(sets_conj))
        return Or(clauses_disj)

    def equivalence_f(self, left_f, right_f):
        a = Implies(left_f, right_f)
        b = Implies(right_f, left_f)
        return And(a, b)

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

    def old_formula(self, acc):
        # top disjunct

        tmp_acc = copy.deepcopy(acc)
        tmp_acc.clean_up2(self.marks_of_scc(self.edge_dict))

        top_disjuncts = []
        for dis in tmp_acc.formula:
            conjuncts = []
            for con in dis:
                edges_vars = []
                if con.num in self.edge_dict:
                    for e in list(set(self.edge_dict[con.num]) & set(self.inner_edges_nums)):
                        var = Bool("e_" + str(e))
                        edges_vars.append(var)
                    assert(edges_vars != [])
                    literal_formula = Or(edges_vars)
                    if con.type == MarkType.Fin:
                        literal_formula = Not(literal_formula)
                    conjuncts.append(literal_formula)

            if conjuncts:
                top_disjuncts.append(And(conjuncts))
        if len(top_disjuncts) == 1:
            return top_disjuncts[0]
        elif len(top_disjuncts) == 0:
            return None
        return Or(top_disjuncts)


# LASO PART

    def disjunct_formula(self, edges):
        alist = []
        for e in edges:
            var = Bool("e_" + str(e))
            alist.append(var)
        return Or(alist)

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
        return And(eq_list)

    def disjunct_formula_list(self, scc_edges_nums):
        alist = []
        for i in scc_edges_nums:
            dis = self.disjunct_formula(i)
            dis = Not(dis)
            alist.append(dis)
        return alist

    def one_scc_f(self):
        formula_list = self.disjunct_formula_list(self.scc_edges_nums)
        dis = []
        for i in range(len(formula_list)):
            formula_list[i] = simplify(Not(formula_list[i]))
            con = []
            for formula in formula_list:
                f = copy.deepcopy(formula)
                con.append(f)
            tmp = simplify(Not(formula_list[i]))
            formula_list[i] = tmp
            dis.append(And(con))
        return Or(dis)

    def laso_f(self, aut):

        in_out = self.in_n_out()

        # edges that are true are in one SCC and none of edges from other SCCs is
        # true
        #one_scc = self.one_scc_f()
        least_one_edge = self.disjunct_formula( self.inner_edges_nums)

        laso = And(in_out, least_one_edge)
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
                c = And(Bool("w_" + src), Bool("w_" + dst))
                impl = Implies(Bool("e_" + str(aut.edge_number(e))), c)
                con1.append(impl)

                # part two -- both edges not in group w
                c1 = And(Not(Bool("w_" + src)), Not(Bool("w_" + dst)))
                con2.append(Implies(Bool("e_" + str(aut.edge_number(e))), c1))

                # part three -- one edge in w, other one not
                # dis1
                c2 = And(Bool("e_" + str(aut.edge_number(e))),
                         Bool("w_" + src), Not(Bool("w_" + dst)))
                dis1.append(c2)

                # dis2
                c3 = And(Bool("e_" + str(aut.edge_number(e))),
                         Not(Bool("w_" + src)), Bool("w_" + dst))
                dis2.append(c3)
        con3.append(Or(dis1))
        con3.append(Or(dis2))

        main_dis.append(And(con1))
        main_dis.append(And(con2))
        main_dis.append(And(con3))

        
        laso = Or(main_dis)

        return laso

# QUANTIFIED PART
    def w_quant(self):
        for dict in self.scc_state_info:
            for key in dict:
                var = Bool("w_" + str(key))
                self.exist_vars.append(var)

    def quant_all(self):
        for e in self.inner_edges_nums:
            var = Bool("e_" + str(e))
            self.univ_vars.append(var)
