FC = mpif90
FFLAGS = -O3 -Wall -fopenmp# -g -fbounds-check #-ffixed-line-length-0 -ffpe-trap=invalid -fbounds-check

module = vars.o
mpimod = parallel.o
files =  windtunnel.o solver.o setup.o navier_stokes.o poisson.o getv.o writetofile.o getvort.o get_params.o



windtunnel : $(module) $(mpimod) $(files)
	$(FC) $(FFLAGS) $(module) $(mpimod) $(files) -o windtunnel

$(module) : vars.f90
	$(FC) -c $(FFLAGS) vars.f90

$(mpimod) : $(module) parallel.f90
	$(FC) -c $(FFLAGS) parallel.f90


%.o : %.f90 $(module) $(mpimod)
	$(FC) -c $(FFLAGS) $< #-o $@





clean:
	rm *.o *.mod
