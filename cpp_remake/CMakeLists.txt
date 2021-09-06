cmake_minimum_required(VERSION 3.16)

set( NAME reduce )
project( ${NAME} )

set( CMAKE_CXX_STANDARD 17 )

#add_library(spot SHARED IMPORTED) # or STATIC instead of SHARED
#set_target_properties(spot PROPERTIES
#        IMPORTED_LOCATION "/home/ter/usr/lib/x86_64-linux-gnu/libspot.so"
        #INTERFACE_INCLUDE_DIRECTORIES "${CMAKE_SOURCE_DIR}/include/libbar"
#        )

add_executable( ${NAME}
        main.cpp
        )


target_include_directories( ${NAME} PUBLIC ${SPOT_INCLUDE_DIR} ${CMAKE_SOURCE_DIR}/cxxopts/include )
target_link_libraries( ${NAME} ${SPOT_SHARED_LIB} ${BDD_SHARED_LIB} )
