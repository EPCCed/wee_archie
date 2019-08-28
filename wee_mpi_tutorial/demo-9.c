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
    
    int token = world_rank == 0 ? -1 : 0;

    // Tree
    //          0  1  2  3
    //          4  5  6  7
    //          8  9  10 11
    //          12 13 14 15

    for(int i = 1; i<world_size; i++) 
    {
        if(world_rank == 0) MPI_Ssend(&token, 1, MPI_INT, i, 0, MPI_COMM_WORLD);
        if(world_rank == i) MPI_Recv(&token, 1, MPI_INT, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    }

    // Finalize the MPI environment.
    MPI_Finalize();
}
