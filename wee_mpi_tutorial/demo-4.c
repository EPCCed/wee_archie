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
  
    int buffer = world_rank, total = 0;
    
    MPI_Request req;
    
    // Do a ring sum
	for(int i = 0; i < world_size; i++) {
	    
        MPI_Isend(&buffer, 1, MPI_INT, (world_rank + 1) % world_size,
			 0, MPI_COMM_WORLD, &req);
        MPI_Recv(&buffer, 1, MPI_INT, (world_rank + world_size - 1) % world_size, 0,
				 MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        MPI_Wait(&req, MPI_STATUS_IGNORE);
        
        total += buffer;
		printf("Process %d received buffer %d from process %d, total is %d\n",
			   world_rank, buffer, (world_rank + world_size - 1) % world_size, total);

	}

    // Finalize the MPI environment.
    MPI_Finalize();
}
