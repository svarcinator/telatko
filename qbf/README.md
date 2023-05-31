# qbf_simplification

QBF simplification of acceptance formula of TELA.
Tries to simplify for each SCC and then turns on precision flag and simplified for every accepting cycle.

If you want to use the limboole solver (switch: -M limboole), you need to install limboole in ./../../solvers/. The process of instalation is described here: http://fmv.jku.at/limboole/.

Keep in mind that the limboole folder needs to be named `limboole1.2`.
