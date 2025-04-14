OBJ=lib/block0.o lib/block1stevens00.o lib/block1stevens10.o lib/block1wang.o lib/md5.o lib/block1.o lib/block1stevens01.o lib/block1stevens11.o lib/main.o md5.o main.o


.PHONY: clean

coll_finder: $(OBJ)
	g++ $? -o $@

clean:
	rm -f coll_finder
	rm -f *.o
	cd lib && $(MAKE) clean
