# Wee MPI Visualisation Library

Intended to be used with the Wee Archie LED Animation Server, this is a
C/Fortran profiling library for MPI which will display LED visualisations before
completing MPI operations for educational purposes.

## Using this library

Due to weak symbols not behaving correctly on all compilers/MPI versions, you
should not use the normal `mpicc` or `mpif90` to compile. Instead, as shown in
the examples folder, you should use the compiler command of your choice and,
insert the flags manually, adding linker parameters so that wee mpi is added
before mpi.

## Potential Improvements

 - All MPI operations implemented.
 - Two way communications with server using websockets, pipes, or similar.
