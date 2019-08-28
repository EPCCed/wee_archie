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
    
    float rand_nums[world_size];
    for(int i =0; i < world_size; i++) rand_nums[i] = i;
    // Sum the numbers locally
    float local_sum = 0;
    int i;
    for (i = 0; i < world_size; i++) {
      local_sum += rand_nums[i];
    }

    // Print the random numbers on each process
    printf("Local sum for process %d - %f, avg = %f\n",
           world_rank, local_sum, local_sum / world_size);

    // Reduce all of the local sums into the global sum
    float global_sum;
    MPI_Reduce(&local_sum, &global_sum, 1, MPI_FLOAT, MPI_SUM, 0,
               MPI_COMM_WORLD);

    // Print the result
    if (world_rank == 0) {
      printf("Total sum = %f, avg = %f\n", global_sum,
             global_sum / (world_size * world_size));
    }
    
    // Finalize the MPI environment.
    MPI_Finalize();
}
