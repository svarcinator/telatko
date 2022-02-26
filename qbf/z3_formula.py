from telatko2.classes import *
from z3 import *
from qbf.q_main import FormulaCreator



class Z3_f_ctor(FormulaCreator):
    def __init__(self,  edge_dict, scc_edg, scc_state_info
                  ,inner_edges_nums,C, K, inner_edges
                  , mode, qbf_solver):
        super().__init__( edge_dict, scc_edg, scc_state_info
                      ,inner_edges_nums,C, K, inner_edges
                      , mode, qbf_solver)

        self.univ_vars = []
        self.exist_vars = []


    def foo(self):
        var1 = Bool('a')
        var2 = Bool('b')
        var3 = Bool('c')
        f = Or(var1, var2)
        f = And(var3, f)
        f = Exists(var1, f)
        s = Solver()
        s.add(f)
        if s.check() == sat:
            print("--satisfiable--")
            s = s.model()
            print(s)

    def prune_scc_edg(self, representants):
        tmp = []
        for alist in self.scc_edg:
            tmp.append(list(filter(lambda e: e in representants,  alist)))
        self.scc_edg = tmp

    def get_level1(self, aut, representants ):
        self.quant_all()

        self.prune_scc_edg(representants)
        laso = self.one_scc_f()
        old = self.old_formula(ACC_DNF(aut.get_acceptance().to_dnf()))
        self.inner_edges_nums = representants
        new = self.new_formula()
        old = simplify(old)
        new = simplify(new)
        eq = self.equivalence_f(old, new)
        impl = Implies(laso, eq)
        inf_not_fin = self.inf_is_not_fin_clause()
        inf_or_fin = self.inf_or_fin_f()
        inf_not_fin = simplify(inf_not_fin)
        inf_or_fin = simplify(inf_or_fin)
        formula = And(impl, inf_not_fin, inf_or_fin)
        formula = ForAll(self.univ_vars, formula)

        return formula

    def get_qbf_formula(self, aut):
        # adds unif. quantified variables to
        #self.foo()
        #assert(False)
        self.quant_all()
        if self.mode > 2:

            self.w_quant(aut)


        if self.mode == 3:

            laso = self.laso_cycles(aut)
            laso = simplify(laso)
            in_out = self.in_n_out()
            laso = And(laso, in_out)
            #assert(False)

        else:
            laso = self.laso_f(aut)

        old = self.old_formula(ACC_DNF(aut.get_acceptance().to_dnf()))

        new = self.new_formula()
        #print(new)
        old = simplify(old)
        #print(new)
        new = simplify(new)

        laso = simplify(laso)

        eq = self.equivalence_f(old, new)
        #print(eq)
        impl = Implies(laso, eq)
        inf_not_fin = self.inf_is_not_fin_clause()
        inf_or_fin = self.inf_or_fin_f()
        inf_not_fin = simplify(inf_not_fin)
        inf_or_fin = simplify(inf_or_fin)
        #print(inf_not_fin, inf_or_fin)
        #assert(False)

        formula = And(impl, inf_not_fin, inf_or_fin)
        if self.exist_vars:
            formula = Exists(self.exist_vars, formula)

        formula = ForAll(self.univ_vars, formula)

        return formula

    def laso_cycles(self, aut):
        main_dis = []
        con1, con2, con3 = [], [], []
        dis1, dis2 = [], []
        for e in self.inner_edges:
            # part one
            src = str(e.src)
            dst = str(e.dst)
            c = And(Bool("w_" + src), Bool("w_" + dst))
            impl = Implies(Bool("e_" + str(aut.edge_number(e))),c)
            con1.append(impl)

            # part two
            c1 =And(Not(Bool("w_" + src)), Not(Bool("w_" + dst)))
            con2.append(Implies(Bool("e_" + str(aut.edge_number(e))),c1 ))

            # part three
            #dis1
            c2 = And(Bool("e_" + str(aut.edge_number(e))), Bool("w_" + src), Not(Bool("w_" + dst)))
            dis1.append(c2)

            #dis2
            c3 = And(Bool("e_" + str(aut.edge_number(e))), Not(Bool("w_" + src)), Bool("w_" + dst))
            dis2.append(c3)
        con3.append(Or(dis1))
        con3.append(Or(dis2))

        main_dis.append(And(con1))
        main_dis.append(And(con2))
        main_dis.append(And(con3))
        #print("main dis: ", main_dis)
        one_scc = self.one_scc_f()
        laso = And(Or(main_dis), one_scc)

        return laso



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
                p = Not(Bool('p_' + str(c) + '_' + str(k)))
                n = Not(Bool('n_' + str(c) + '_' + str(k)))
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

    def old_formula(self, acc):
        # top disjunct

        top_disjuncts = []
        for dis in acc.formula:
            conjuncts = []
            for con in dis:
                edges_vars = []
                if con.num in self.edge_dict:
                    for e in self.edge_dict[con.num]:
                        var = Bool("e_" + str(e))
                        edges_vars.append(var)
                    literal_formula = Or(edges_vars)
                    if con.type == MarkType.Fin:
                        literal_formula = Not(literal_formula)
                    conjuncts.append(literal_formula)
            top_disjuncts.append(And(conjuncts))
        if len(top_disjuncts) == 1:
            return top_disjuncts[0]
        return Or(top_disjuncts)


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


                eq_list.append(self.equivalence_f(self.disjunct_formula(dst), self.disjunct_formula(src)))
        return And(eq_list)

    def disjunct_formula_list(self, scc_edg):
        alist = []
        for i in scc_edg:
            dis = self.disjunct_formula(i)
            dis = Not(dis)
            alist.append(dis)
        return alist

    def one_scc_f(self):
        formula_list = self.disjunct_formula_list(self.scc_edg)
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
        one_scc = self.one_scc_f()

        laso = And(in_out, one_scc)
        return laso


    def w_quant(self, aut):
        num_states = aut.num_states()
        for i in range(num_states):
            var  = Bool("w_" + str(i))
            self.exist_vars.append(var)

    def quant_all(self):
        for e in self.inner_edges_nums:
            var = Bool("e_" + str(e))
            self.univ_vars.append(var)
