from telatko2.classes import *
from z3 import *
from qbf.q_main import FormulaCreator

def foo():
    p1 = Bool('p1')
    p2 = Bool('p1')

    #q = Bool('q')
    F = ForAll([p1, p2], Or(And(Not(p1),Not(p2)), And(p1,p2)))
    #solver = Solver()
    #solver.add(F)
    result = solver.check()
    print(F, result, solver.model())

class Z3_f_ctor(FormulaCreator):
    def __init__(self,  edge_dict, scc_edg, scc_state_info
                  ,inner_edges_nums,C, K, inner_edges
                  , mode, qbf_solver):
        super().__init__( edge_dict, scc_edg, scc_state_info
                      ,inner_edges_nums,C, K, inner_edges
                      , mode, qbf_solver)

        self.univ_vars = []
        self.exist_vars = []



    def get_qbf_formula(self, aut):
        # adds unif. quantified variables to
        self.quant_all()
        if self.mode > 2:

            self.w_quant(aut)

        if self.mode == 4:

            laso = self.laso_cycles(aut)
            laso = simplify(laso)
            in_out = self.in_n_out()
            laso = And(laso, in_out)
            #assert(False)

        else:
            laso = self.laso_f(aut)

        old = self.old_formula(ACC_DNF(aut.get_acceptance().to_dnf()))
        new = self.new_formula()
        old = simplify(old)
        #print(new)
        new = simplify(new)

        laso = simplify(laso)

        eq = self.equivalence_f(old, new)
        impl = Implies(laso, eq)
        inf_not_fin = self.inf_is_not_fin_clause()
        inf_or_fin = self.inf_or_fin_f()
        inf_not_fin = simplify(inf_not_fin)
        inf_or_fin = simplify(inf_or_fin)
        #print(inf_not_fin, inf_or_fin)
        #assert(False)

        formula = And(impl, inf_not_fin, inf_or_fin)
        if self.exist_vars:
            formula = ForAll(self.exist_vars, formula)

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
            c1 =And(Bool("!w_" + src), Bool("!w_" + dst))
            con2.append(Implies(Bool("e_" + str(aut.edge_number(e))),c1 ))

            # part three
            #dis1
            c2 = And(Bool("e_" + str(aut.edge_number(e))), Bool("w_" + src), Bool("!w_" + dst))
            dis1.append(c2)

            #dis2
            c3 = And(Bool("e_" + str(aut.edge_number(e))), Bool("!w_" + src), Bool("w_" + dst))
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
                p = Bool('!p_' + str(c) + '_' + str(k))
                n = Bool('!n_' + str(c) + '_' + str(k))
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
                for e in self.edge_dict[con.num]:
                    var = Bool("e_" + str(e))
                    edges_vars.append(var)
                literal_formula = Or(edges_vars)
                if con.type == MarkType.Fin:
                    literal_formula = Not(literal_formula)
                conjuncts.append(literal_formula)
            top_disjuncts.append(And(conjuncts))
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

    def connection(self, aut):
        con = []
        for e in self.inner_edges:
            src = e.src
            dst = e.dst
            if src != dst:
                eq = equivalence_f(Bool("w_" + str(src)), Bool("w_" + str(dst)))
                impl = Implies(Bool("e_" + str(edges_translator[aut.edge_number(e)])), eq)
                impl = SATformula("->")

                con.append(impl)
        if len(con) == 0:
            return None
        return And(con)

    def positive(self, aut):
        dis = []
        for e in self.inner_edges:
            con = And(Bool("e_" + str(edges_translator[aut.edge_number(e)])), Bool("w_" + str(e.src)))
            dis.append(con)
        if len(dis) == 0:
            return None
        return Or(dis)

    def negative(self, aut):
        dis = []
        for e in self.inner_edges:
            con = And(Bool("e_" + str(self.edges_translator[aut.edge_number(e)])), Bool("!w_" + str(e.src)))
            dis.append(con)
        if len(dis) == 0:
            return None
        return Or(dis)

    def negate_part(self, aut):
        connect = self.connection(aut)
        pos = self.positive(aut)
        neg = self.negative(aut)
        con_list = []
        if connect:
            con_list.append(connect)
        if pos:
            con_list.append(pos)
        if neg:
            con_list.append(neg)
        if not con_list:
            return None
        con = And(con_list)
        return Not(con)




    def laso_f(self, aut):

        in_out = self.in_n_out()


        # edges that are true are in one SCC and none of edges from other SCCs is
        # true
        one_scc = self.one_scc_f()

        laso = And(in_out, one_scc)


        # this part makes sure, that the edges are connected tzn QBF CONNECTED
        if self.mode == 3:
            # THIS IS NOT USED ANY MORE
            print("Mode  == 3")
            neg = self.negate_part(aut)
            laso = And(laso, neg)
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
