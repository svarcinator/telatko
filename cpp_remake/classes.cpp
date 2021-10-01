#include <string>


enum MarkType {Inf, Fin};
enum Satisfiable {t, f, maybe};




class ACCMark {
    /*
        Represents an acceptance set
    */

    MarkType mtype;
    int num;

public:

    ACCMark( MarkType m, int n )
        : mtype( m ), num(n)
        {}

    std::string to_str() {
        if ( mtype == MarkType::Inf ) {
            return "Inf(" + std::to_string(num) + ")";
        } else {
            return "Fin(" + std::to_string(num) + ")";
        }
    }


    friend bool operator==( const ACCMark& m1, const ACCMark& m2 ) {
        /*
        Compare two ACCMarks, return true if they are the same, false otherwise.

        Arguments:
            other {ACCMark} -- the other ACCMark

        Returns:
            bool -- true if marks are the same, false otherwise
            */

        return ( m1.mtype == m2.mtype &&
                 m1.num == m2.num );
    }

    friend bool operator!=( const ACCMark& m1, const ACCMark& m2 ) {

        return ( m1.mtype != m2.mtype ||
                 m1.num != m2.num );
    }



};

std::vector< std::vector< ACCMark > > parse_acc_cnf( spot::acc_cond code );
std::vector< std::vector< ACCMark > > parse_acc_dnf( spot::acc_cond code );

class PACC {
    /*
        Acceptance formula manipulation
    */


public:

    std::vector< std::vector< ACCMark > > formula;



    PACC( spot::acc_cond code ) {
        if ( code.get_acceptance().is_dnf() ) {
            formula = parse_acc_dnf( code );
        } else {
            formula = parse_acc_cnf( code );
        }

    }



    virtual ~PACC() = default;

    //virtual std::vector< std::vector< ACCMark > > parse_acc( spot::acc_cond code );

    int fce() {
        std::cout << "PAC fce\n";
        return 1;
    }



};



class CNF_PACC : public PACC {

    Satisfiable sat;

public:

    CNF_PACC( spot::acc_cond code ) : PACC( code ) {
        if ( code.is_f() ) {
            sat = Satisfiable::f;
        } else if ( code.is_t() ) {
            sat = Satisfiable::t;
        } else {
            //formula = parse_acc( code );
            sat = Satisfiable::maybe;
        }
    }



    void print() {
        for ( auto con : formula ) {
            std::cout << "( ";
            for ( auto dis : con )  {
                std::cout << dis.to_str();
                if ( dis != con.back() ) {
                    std::cout << " | ";
                }
            }
            std::cout << " )";
            if ( con != formula.back() ) {
                std::cout << " & ";
            }
        }
    }



};


class DNF_PACC : public PACC {
    //std::vector< std::vector< ACCMark > > formula;
    Satisfiable sat;

public:

    DNF_PACC( spot::acc_cond code ) : PACC(code) {
        if ( code.is_f() ) {
            sat = Satisfiable::f;
        } else if ( code.is_t() ) {
            sat = Satisfiable::t;
        } else {
            //formula = parse_acc( code );
            sat = Satisfiable::maybe;
        }
    }



    void print() {
        for ( auto con : formula ) {
            std::cout << "( ";
            for ( auto dis : con )  {
                std::cout << dis.to_str();
                if ( dis != con.back() ) {
                    std::cout << " & ";
                }
            }
            std::cout << " )";
            if ( con != formula.back() ) {
                std::cout << " | ";
            }
        }
    }

};

std::vector< std::vector< ACCMark > > parse_acc_dnf( spot::acc_cond code )  {
    std::vector< std::vector< ACCMark > > formula;

    auto dis = code.top_disjuncts();
    int counter = 0;
    for ( auto con : dis ) {
        std::vector< ACCMark > vec;
        for ( auto term : con.top_conjuncts() ) {
            if ( term.fin_one() == -1 ) {
                // super inelegant way of getting the number of acc_code
                vec.push_back( { MarkType::Inf, term.get_acceptance().used_sets().max_set() - 1 } );
            } else {
                vec.push_back( { MarkType::Fin,term.get_acceptance().used_sets().max_set() - 1 } );
            }

        }

        formula.push_back(vec);
    }
    return formula;

}

std::vector< std::vector< ACCMark > > parse_acc_cnf( spot::acc_cond code )  {
    std::vector< std::vector< ACCMark > > formula;
    auto con = code.top_conjuncts();
    int counter = 0;
    for ( auto dis : con ) {
        std::vector< ACCMark > vec;
        for ( auto term : dis.top_disjuncts() ) {
            if ( term.fin_one() == -1 ) {
                // super inelegant way of getting the number of acc_code
                vec.push_back( { MarkType::Inf, term.get_acceptance().used_sets().max_set() - 1 } );
            } else {
                vec.push_back( { MarkType::Fin,term.get_acceptance().used_sets().max_set() - 1 } );
            }
        }
        formula.push_back(vec);
    }
    return formula;
}
