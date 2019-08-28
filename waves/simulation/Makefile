FC = f95
WMPI_DIR = /home/pi/sohpc-19/wee_archie/wee_mpi
WMPI_FLAGS = -I$(WMPI_DIR) -L$(WMPI_DIR) -Wl,-rpath=$(WMPI_DIR) -I$(WMPI_DIR)/fortran $(WMPI_DIR)/fortran/wee_mpi_mod.o
MPI_FLAGS =-Wl,-Bsymbolic-functions -Wl,-z,relro -I/usr/include/mpich -I/usr/include/mpich 
LD =-lfmpich -lwee_mpi -lcurl -lmpich 
FFLAGS = $(WMPI_FLAGS) $(MPI_FLAGS) -O3 -fopenmp $(LD)#-fbacktrace -g -fbounds-check


SRC = main.F90 step.F90 vars.F90 comms.F90 io.F90 analysis.F90

all: waves generate_depth generate_ic

waves: vars_mod.mod comms_mod.mod io_mod.mod step_mod.mod analysis_mod.mod $(SRC)
	$(FC) $(FFLAGS) main.F90 vars.o comms.o io.o step.o analysis.o -o waves

comms_mod.mod : vars_mod.mod comms.F90
	$(FC) $(FFLAGS) -c comms.F90

io_mod.mod : vars_mod.mod comms_mod.mod io.F90
	$(FC) $(FFLAGS) -c io.F90

vars_mod.mod: vars.F90
	$(FC) $(FFLAGS) -c vars.F90

step_mod.mod: step.F90 vars_mod.mod comms_mod.mod analysis_mod.mod
	$(FC) $(FFLAGS) -c step.F90

analysis_mod.mod: vars_mod.mod analysis.F90
	$(FC) $(FFLAGS) -c analysis.F90

generate_depth: generate_depth.F90
	$(FC) $(FFLAGS) generate_depth.F90 -o generate_depth

generate_ic: generate_ic.F90
	$(FC) $(FFLAGS) generate_ic.F90 -o generate_ic

clean:
	rm *.mod *.o
