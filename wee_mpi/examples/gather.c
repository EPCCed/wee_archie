#include <stdio.h>
#include <stdlib.h>
#include <wee_mpi.h>


int main(int argc, char** argv) {
    // initialize the mpi environment
    MPI_Init(&argc, &argv);
 
    // get the number of processes
    int world_size;
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);

    // get the rank of the process
    int world_rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);
    
    // get the name of the processor
    char processor_name[MPI_MAX_PROCESSOR_NAME]; int name_len;
    MPI_Get_processor_name(processor_name, &name_len);

    printf("Rank: %d, Proc Name:%s\n", world_rank, processor_name); 
    int data_arr[world_size];
    int data = world_rank;
    MPI_Gather(&data, 1, MPI_INT, data_arr, 1, MPI_INT, 0, MPI_COMM_WORLD);

    // Finalize the MPI environment.
    MPI_Finalize();
}
