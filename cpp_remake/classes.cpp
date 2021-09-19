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

//

class PACC {
    /*
        Acceptance formula manipulation
    */



public:


    //PACC() = default;



    virtual ~PACC() = default;

    //virtual std::vector< std::vector< ACCMark > > parse_acc( spot::acc_cond code );

    int fce() {
        return 1;
    }



};



class CNF_PACC : public PACC {
    std::vector< std::vector< ACCMark > > formula;
    Satisfiable sat;

public:

    //CNF_PACC( spot::acc_cond code ) : PACC( code ) {}

    CNF_PACC( spot::acc_cond code ) {
        if ( code.is_f() ) {
            sat = Satisfiable::f;
        } else if ( code.is_t() ) {
            sat = Satisfiable::t;
        } else {
            formula = parse_acc( code );
            sat = Satisfiable::maybe;
        }
    }

    std::vector< std::vector< ACCMark > > parse_acc( spot::acc_cond code )  {
        std::vector< std::vector< ACCMark > > formula;

        auto con = code.top_conjuncts();
        int counter = 0;
        for ( auto dis : con ) {
            std::vector< ACCMark > vec;
            for ( auto term : dis.top_disjuncts() ) {
                vec.push_back( { MarkType::Inf, ++counter } );
            }
            formula.push_back(vec);
        }



        std::cout << "success\n";
        return formula;

    }

    void print() {
        for ( auto con : formula ) {
            std::cout << "( ";
            for ( auto dis : con )  {
                std::cout << dis.to_str() << " ";
                if ( dis != con.back() ) {
                    std::cout << "|";
                }
            }
            std::cout << " )";
            if ( con != formula.back() ) {
                std::cout << "&";
            }
        }
    }

};
