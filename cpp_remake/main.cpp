#include <iostream>
#include <fstream>
#include <spot/tl/formula.hh>
#include <spot/misc/version.hh>
#include <spot/twaalgos/dot.hh>
#include <spot/twa/twagraph.hh>
#include <spot/twaalgos/hoa.hh>
#include <spot/parseaut/public.hh>
#include <spot/twaalgos/sccfilter.hh>
#include "cxxopts/include/cxxopts.hpp"
#include "telatko2/t_main.cpp"




 int main( int argc, char* argv[] ) {
     spot::bdd_dict_ptr dict = spot::make_bdd_dict();

   cxxopts::Options options("reduce", "Tool for automata reduction");

   options.add_options()
           ("F,autfile", "file containing automata in HOA format", cxxopts::value<std::string>())
           ("h,help", "print usage")
           ("O,output", "output file", cxxopts::value<std::string>())
           ("L,level", "level of simplification", cxxopts::value<int>())
           ("T,timeout", "QBF solver timeout", cxxopts::value<int>())
           ;
   options.allow_unrecognised_options();

   auto result = options.parse(argc, argv);
   int level = 1;
   int timeout = 40;

   if (result.count("help"))
   {
       std::cout << options.help() << std::endl;
       exit(0);
   }


   if ( !result.count( "autfile" ) ) {
       std::cerr << "missing input: use parameter -F (see help)";
   }

   if ( result.count( "level" ) ) {
     level = result[ "level" ].as< int >();
     if ( level > 4 ) {
       level = 4;
     }

   }

   if ( result.count( "timeout" ) ) {
     timeout = result[ "timeout" ].as< int >();

   }

   auto dump = [&](const auto &what) {
       what->prop_reset();
       if (!result.count("output")) {
           print_hoa(std::cout, what);
           return;
       }
       std::ofstream out(result["output"].as<std::string>());
       print_hoa(out, what);
   };

   try {
       if ( result.count( "autfile" ) ) {
           auto parser = spot::automaton_stream_parser( result[ "autfile" ].as<std::string>() );
           auto aut = parser.parse( dict )->aut;
           while ( aut != nullptr ){
               process_aut( aut, level, timeout );  // telatko
               dump( aut );
               aut = parser.parse( dict )->aut;
           }
       }

   } catch ( std::runtime_error& e ) {
       std::cerr << "Error during parsing automaton.\n" << e.what();
       return 1;
   }
   return 0;

}
