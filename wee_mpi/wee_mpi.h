#ifndef WEE_MPI_H
#define WEE_MPI_H

#include <mpi/mpi.h>

// IO Operations
int wee_flags(int silent);
int wee_http_post( char *url, char *postfields );

// Runs arbitrary animation folder
int wee_anim(char * anim);

// Flow Control
int wee_wait(int force);

// MPI Overrides
int MPI_Init( int *argc, char ***argv );
int MPI_Finalize();

// P2P Communications
int MPI_Ssend( const void *buf, int count, MPI_Datatype datatype, int dest,
        int tag, MPI_Comm comm );

int MPI_Recv( void *buf, int count, MPI_Datatype datatype, int source,
        int tag, MPI_Comm comm, MPI_Status *status );

int MPI_Isend( const void *buf, int count, MPI_Datatype datatype, int dest,
        int tag, MPI_Comm comm, MPI_Request *request );

int MPI_Sendrecv(const void *sendbuf, int sendcount, MPI_Datatype sendtype,
                int dest, int sendtag,
                void *recvbuf, int recvcount, MPI_Datatype recvtype,
                int source, int recvtag,
                MPI_Comm comm, MPI_Status *status);
// Collective Communications

// One to Many / Many to One
int MPI_Bcast( void *buffer, int count, MPI_Datatype datatype, int root, MPI_Comm comm );

int MPI_Gather( const void *sendbuf, int sendcount, MPI_Datatype sendtype,
               void *recvbuf, int recvcount, MPI_Datatype recvtype,
               int root, MPI_Comm comm );

int MPI_Scatter( const void *sendbuf, int sendcount, MPI_Datatype sendtype,
               void *recvbuf, int recvcount, MPI_Datatype recvtype, int root,
               MPI_Comm comm );

int MPI_Reduce( const void *sendbuf, void *recvbuf, int count, MPI_Datatype datatype,
               MPI_Op op, int root, MPI_Comm comm );

// Many to Many
// TODO: Implement
int MPI_Allgather( const void *sendbuf, int sendcount, MPI_Datatype sendtype,
                  void *recvbuf, int recvcount, MPI_Datatype recvtype,
                  MPI_Comm comm );

int MPI_Allreduce( const void *sendbuf, void *recvbuf, int count,
                  MPI_Datatype datatype, MPI_Op op, MPI_Comm comm );

int MPI_Alltoall( const void *sendbuf, int sendcount, MPI_Datatype sendtype,
                 void *recvbuf, int recvcount, MPI_Datatype recvtype,
                 MPI_Comm comm );

#endif
