FC = f95
FFLAGS = -c -I. -Wl,-Bsymbolic-functions -Wl,-z,relro -I/usr/include/mpich -I/usr/include/mpich -L. -Wl,-rpath=/home/pi/Documents/sohpc-19/wee_mpi -lfmpich -lwee_mpi -lcurl -lmpich
RM = rm -f 
FTARGET = wee_mpi.mod
FSRCS = wee_mpi_mod.f90

.PHONY: all
all: ${FTARGET}

.PHONY: clean
clean:
	-${RM}  $(FSRCS:.f90=.o) *.mod

$(FTARGET): $(FSRCS)
	$(FC) $(FFLAGS) $^
