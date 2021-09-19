#include <spot/twaalgos/cleanacc.hh>
#include "./../classes.cpp"

void process_aut( spot::twa_graph_ptr &aut, int level, int timeout ) {

    std::cout << "Automat v procesu\n" << "level:" << level << " timeout: " << timeout << std::endl;
    int  K = aut->acc().num_sets();
    int C = aut->get_acceptance().to_dnf().top_disjuncts().size();
    std::cout << "K: " << K << "C: " << C << std::endl;

    auto original_cpy = aut;

    cleanup_acceptance_here( aut );
    if ( aut->get_acceptance().used_sets().count() < 1 ||
         aut->prop_state_acc() == spot::trival::yes_value ) {
        return;
    }

    if ( aut->get_acceptance().to_dnf().size() < aut->get_acceptance().to_cnf().size() ) {

        // dnf simplification
        std::cout << "Future DNF simplification\n";
    } else {
      // cnf simplification
      std::cout << "Future CNF simplification\n";
      auto formula = CNF_PACC(aut->get_acceptance().to_cnf());
      int a = formula.fce();
      formula.print();

    }





    return;
}
