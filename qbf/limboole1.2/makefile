CC=gcc
CFLAGS=-O3 -DNDEBUG -DVERSION=1.2 -DLIMBOOLE_USE_PICOSAT -I../picosat -DLIMBOOLE_USE_DEPQBF -I../depqbf
LIBS= -L../picosat -lpicosat -L../depqbf -lqdpll
DEPS= ../picosat/picosat.h ../picosat/libpicosat.a ../depqbf/qdpll.h ../depqbf/libqdpll.a

all: limboole testlimboole dimacs2boole

limboole: main.o limboole.o $(DEPS)
	$(CC) $(CFLAGS) -o $@ main.o limboole.o $(LIBS)
testlimboole: test.o limboole.o $(DEPS)
	$(CC) $(CFLAGS) -o $@ test.o limboole.o $(LIBS)
dimacs2boole: dimacs2boole.c makefile
	$(CC) $(CFLAGS) -o $@ dimacs2boole.c

limboole.o: limboole.c makefile $(DEPS)
	$(CC) $(CFLAGS) -c limboole.c
test.o: test.c makefile
	$(CC) $(CFLAGS) -c test.c
main.o: main.c makefile
	$(CC) $(CFLAGS) -c main.c

clean:
	rm -f limboole testlimboole dimacs2boole
	rm -f makefile
	rm -f *.o *.a
	rm -f log/*.log
	rm -f *.bb *.bbg  *.gcov *.da
	rm -f *~
