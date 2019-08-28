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
    
    int token = world_rank == 9 ? -1 : 0;

    // Tree
    //        0  1  2  3
    //        4  5  6  7
    //        8  9  10 11
    //        12 13 14 15

    // Round 1
	if(world_rank == 9) MPI_Ssend(&token, 1, MPI_INT, 5, 0, MPI_COMM_WORLD);
    if(world_rank == 5) MPI_Recv(&token, 1, MPI_INT, 9, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

    // Round 2
	if(world_rank == 9) MPI_Ssend(&token, 1, MPI_INT, 10, 0, MPI_COMM_WORLD);
    if(world_rank == 10) MPI_Recv(&token, 1, MPI_INT, 9, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    
	if(world_rank == 5) MPI_Ssend(&token, 1, MPI_INT, 6, 0, MPI_COMM_WORLD);
  if(world_rank == 6) MPI_Recv(&token, 1, MPI_INT, 5, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
  
  // Round 3	
  if(world_rank == 9) MPI_Ssend(&token, 1, MPI_INT, 13, 0, MPI_COMM_WORLD);
  if(world_rank == 13) MPI_Recv(&token, 1, MPI_INT, 9, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

  if(world_rank == 5) MPI_Ssend(&token, 1, MPI_INT, 1, 0, MPI_COMM_WORLD);
  if(world_rank == 1) MPI_Recv(&token, 1, MPI_INT, 5, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

  if(world_rank == 10) MPI_Ssend(&token, 1, MPI_INT, 14, 0, MPI_COMM_WORLD);
  if(world_rank == 14) MPI_Recv(&token, 1, MPI_INT, 10, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

  if(world_rank == 6) MPI_Ssend(&token, 1, MPI_INT, 2, 0, MPI_COMM_WORLD);
  if(world_rank == 2) MPI_Recv(&token, 1, MPI_INT, 6, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
  
  // Round 4
  if(world_rank == 1) MPI_Ssend(&token, 1, MPI_INT, 0, 0, MPI_COMM_WORLD);
  if(world_rank == 0) MPI_Recv(&token, 1, MPI_INT, 1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

  if(world_rank == 5) MPI_Ssend(&token, 1, MPI_INT, 4, 0, MPI_COMM_WORLD);
  if(world_rank == 4) MPI_Recv(&token, 1, MPI_INT, 5, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

  if(world_rank == 9) MPI_Ssend(&token, 1, MPI_INT, 8, 0, MPI_COMM_WORLD);
  if(world_rank == 8) MPI_Recv(&token, 1, MPI_INT, 9, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

  if(world_rank == 13) MPI_Ssend(&token, 1, MPI_INT, 12, 0, MPI_COMM_WORLD);
  if(world_rank == 12) MPI_Recv(&token, 1, MPI_INT, 13, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
  
  if(world_rank == 2) MPI_Ssend(&token, 1, MPI_INT, 3, 0, MPI_COMM_WORLD);
  if(world_rank == 3) MPI_Recv(&token, 1, MPI_INT, 2, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

  if(world_rank == 6) MPI_Ssend(&token, 1, MPI_INT, 7, 0, MPI_COMM_WORLD);
  if(world_rank == 7) MPI_Recv(&token, 1, MPI_INT, 6, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

  if(world_rank == 10) MPI_Ssend(&token, 1, MPI_INT, 11, 0, MPI_COMM_WORLD);
  if(world_rank == 11) MPI_Recv(&token, 1, MPI_INT, 10, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

  if(world_rank == 14) MPI_Ssend(&token, 1, MPI_INT, 15, 0, MPI_COMM_WORLD);
  if(world_rank == 15) MPI_Recv(&token, 1, MPI_INT, 14, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
  
  

    // Finalize the MPI environment.
    MPI_Finalize();
}
