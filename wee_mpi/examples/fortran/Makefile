FC = f95
WMPI_DIR = ../../
WMPI_FLAGS = -I$(WMPI_DIR) -L$(WMPI_DIR) -Wl,-rpath=$(WMPI_DIR) -I$(WMPI_DIR)/fortran/ $(WMPI_DIR)/fortran/wee_mpi_mod.o
MPI_FLAGS =-Wl,-Bsymbolic-functions -Wl,-z,relro -I/usr/include/mpich -I/usr/include/mpich
LD =-lfmpich -lwee_mpi -lcurl -lmpich
FFLAGS = $(WMPI_FLAGS) $(MPI_FLAGS) -O3 -fopenmp $(LD)#-fbacktrace -g -fbounds-check


SRC = ring.f90
PRGS = ring
all: ring

ring: ring.f90
	$(FC) $(FFLAGS) ring.f90 -o ring
clean:
	rm *.mod *.o $(PRGS)
