#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "wee_mpi.h"
#include <curl/curl.h>

// Constants
const char URL_BASE[] = "http://localhost:5000/";
const char URL_BASE[] = "http://localhost:5555/";

// Global State
MPI_Comm WEE_MPI_COMM_WORLD; // Libray World, to allow for independent comms.
int WEE_MPI_WORLD_RANK;
char ** WEE_MPI_RANK_PROC_NAMES; // Record of processor names for IO.
char RANK_NAME[MPI_MAX_PROCESSOR_NAME];
int SILENT = 0;

// Allocates contiguous memory for 2d array.
void** alloc_2d(int rows, int cols, size_t size) {
    void *data = (void *)malloc(rows*cols*size);
    void **array= (void **)malloc(rows*sizeof(void *));
    for (int i=0; i<rows; i++) array[i] = data + i*cols*size;
    return array;
}

// Translates Comm Rank of arbitrary process
int translate_rank(MPI_Comm in_comm, MPI_Comm out_comm, int rank)
{
    MPI_Group in_grp, out_grp;

    MPI_Comm_group(in_comm, &in_grp);
    MPI_Comm_group(out_comm, &out_grp);

    int in_rank[1] = { rank };
    int out_rank[1];

    MPI_Group_translate_ranks(in_grp, 1, in_rank, out_grp, out_rank);

    MPI_Group_free(&in_grp);
    MPI_Group_free(&out_grp);

    return out_rank[0];
}

char * rank_proc_name(MPI_Comm comm, int rank)
{
    int world_rank = comm == WEE_MPI_COMM_WORLD ? rank : translate_rank(comm, WEE_MPI_COMM_WORLD, rank);
    return WEE_MPI_RANK_PROC_NAMES[world_rank];
}

// Initializes Global State
int MPI_Init(int *argc, char ***argv)
{
    int result = PMPI_Init(argc,argv); 
    
    // Sets up World Duplicate.
    MPI_Comm_dup(MPI_COMM_WORLD, &WEE_MPI_COMM_WORLD);
    int comm_size; MPI_Comm_size(WEE_MPI_COMM_WORLD, &comm_size);
    
    // Get World Rank
    MPI_Comm_rank(WEE_MPI_COMM_WORLD, &WEE_MPI_WORLD_RANK);
    
    // Get all processor names, to allow for easy spatial identification. 
    int name_len;
    MPI_Get_processor_name(RANK_NAME, &name_len);

    WEE_MPI_RANK_PROC_NAMES = (char**) alloc_2d(comm_size, MPI_MAX_PROCESSOR_NAME, sizeof(char));
    
    PMPI_Allgather(RANK_NAME, MPI_MAX_PROCESSOR_NAME, MPI_CHAR, WEE_MPI_RANK_PROC_NAMES[0], MPI_MAX_PROCESSOR_NAME, MPI_CHAR, WEE_MPI_COMM_WORLD);
    
    fprintf(stderr, "Initialized Wee MPI sucessfully.\n");
     
    if(WEE_MPI_WORLD_RANK == 0)
    {
        fprintf(stderr, "Rank Names are: \n");
        for(int i = 0; i < comm_size; i++) 
            fprintf(stderr, "Rank: %d Name: %s\n", i, WEE_MPI_RANK_PROC_NAMES[i]);
    }
    
    return result;
}

int wee_flags(int silent)
{
    SILENT = silent;
    return 0;
}

// Helper to make generic POST request
int wee_http_post(char *url, char *postfields)
{
    if(SILENT) return 0; 

    CURL *curl;
    CURLcode res;

    curl_global_init(CURL_GLOBAL_DEFAULT);

    curl = curl_easy_init();
          
    if(curl) 
    {
        fprintf(stderr, "POSTing to %s%s\n", url, postfields);
        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, postfields);

        res = curl_easy_perform(curl);
        if(res != CURLE_OK)
            fprintf(stderr, "curl_easy_perform() failed: %s\n",
                curl_easy_strerror(res));

        curl_easy_cleanup(curl);
    }

    curl_global_cleanup();
}

int wee_wait(int force) 
{
    char url[80], postfields[10];
    sprintf(url, "%swait/", URL_BASE);
    sprintf(postfields,"force=%d", force); 
    wee_http_post(url, postfields);
}

int wee_anim(char * anim)
{
    char url[80], postfields[strlen(anim)+20];
    sprintf(url, "%splay", URL_BASE);
    sprintf(postfields,"anim=%s", anim); 
    wee_http_post(url, postfields);
}

// Convenience function to reduce repetition, watch out for buffer size issues, takes processor names.
int wee_call_endpoint(char * endpoint, char * src, char * dest)
{
    char url[80], postfields[MPI_MAX_PROCESSOR_NAME*2 + 50];
    sprintf(url, "%s%s", URL_BASE, endpoint);
    sprintf(postfields, "src=%s&dest=%s", src, dest); 
    wee_http_post(url, postfields);
}

int MPI_Ssend(const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)
{
    wee_call_endpoint("send/", RANK_NAME, rank_proc_name(comm, dest));
    return PMPI_Ssend(buf, count, datatype, dest, tag, comm);
}

int MPI_Recv(void *buf, int count, MPI_Datatype datatype, int source, int tag, MPI_Comm comm, MPI_Status *status)
{
    wee_call_endpoint("receive/", rank_proc_name(comm, source), RANK_NAME);
    return PMPI_Recv(buf, count, datatype, source, tag, comm, status);
}

int MPI_Isend(const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm, MPI_Request *request)
{
    wee_call_endpoint("isend/", RANK_NAME, rank_proc_name(comm, dest));
    return PMPI_Isend(buf, count, datatype, dest, tag, comm, request);
}

int MPI_Irecv(void *buf, int count, MPI_Datatype datatype, int source, int tag, MPI_Comm comm, MPI_Request *request)
{
    wee_call_endpoint("ireceive/", rank_proc_name(comm, source), RANK_NAME);
    return PMPI_Irecv(buf, count, datatype, source, tag, comm, request);
}

int MPI_Sendrecv(const void *sendbuf, int sendcount, MPI_Datatype sendtype,
                int dest, int sendtag,
                void *recvbuf, int recvcount, MPI_Datatype recvtype,
                int source, int recvtag,
                MPI_Comm comm, MPI_Status *status) 
{
    wee_call_endpoint("sendrecv/", rank_proc_name(comm, source), rank_proc_name(comm, dest));
    return PMPI_Sendrecv(sendbuf, sendcount, sendtype, dest, sendtag, recvbuf,
            recvcount, recvtype, source, recvtag, comm, status);
}

int MPI_Bcast( void *buffer, int count, MPI_Datatype datatype, int root, MPI_Comm comm )
{
    char url[80], postfields[MPI_MAX_PROCESSOR_NAME*2 + 50];
    sprintf(url, "%s%s", URL_BASE, "bcast/");
    sprintf(postfields, "src=%s&host=%s", rank_proc_name(comm, root), RANK_NAME); 
    wee_http_post(url, postfields);
    return PMPI_Bcast(buffer, count, datatype, root, comm);
}

int MPI_Gather( const void *sendbuf, int sendcount, MPI_Datatype sendtype,
               void *recvbuf, int recvcount, MPI_Datatype recvtype,
               int root, MPI_Comm comm )
{
    char url[80], postfields[MPI_MAX_PROCESSOR_NAME*2 + 50];
    sprintf(url, "%s%s", URL_BASE, "gather/");
    sprintf(postfields, "dest=%s&host=%s", rank_proc_name(comm, root), RANK_NAME); 
    wee_http_post(url, postfields);
    return PMPI_Gather(sendbuf, sendcount, sendtype, recvbuf, recvcount, recvtype, root, comm);
}

int MPI_Scatter( const void *sendbuf, int sendcount, MPI_Datatype sendtype,
               void *recvbuf, int recvcount, MPI_Datatype recvtype, 
               int root, MPI_Comm comm )
{
    char url[80], postfields[MPI_MAX_PROCESSOR_NAME*2 + 50];
    sprintf(url, "%s%s", URL_BASE, "scatter/");
    sprintf(postfields, "src=%s&host=%s", rank_proc_name(comm, root), RANK_NAME); 
    wee_http_post(url, postfields);
    return PMPI_Scatter(sendbuf, sendcount, sendtype, recvbuf, recvcount, recvtype, root, comm);
}

const char* op_str(MPI_Op op)
{
    if(op == MPI_MAX) return "max";
    if(op == MPI_MIN) return "min";
    if(op == MPI_SUM) return "sum";
    if(op == MPI_PROD) return "prod";
}

int MPI_Reduce( const void *sendbuf, void *recvbuf, int count, MPI_Datatype datatype,
               MPI_Op op, int root, MPI_Comm comm )
{
    char url[80], postfields[MPI_MAX_PROCESSOR_NAME*2 + 50];
    sprintf(url, "%s%s", URL_BASE, "reduce/");
    sprintf(postfields, "dest=%s&host=%s&op=%s", rank_proc_name(comm, root), RANK_NAME, op_str(op)); 
    wee_http_post(url, postfields);
    return PMPI_Reduce(sendbuf, recvbuf, count, datatype, op, root, comm);
}

int MPI_Allgather( const void *sendbuf, int sendcount, MPI_Datatype sendtype,
                  void *recvbuf, int recvcount, MPI_Datatype recvtype,
                  MPI_Comm comm )
{
    return PMPI_Allgather(sendbuf, sendcount, sendtype, recvbuf, recvcount, recvtype, comm);
}

int MPI_Allreduce( const void *sendbuf, void *recvbuf, int count,
                  MPI_Datatype datatype, MPI_Op op, MPI_Comm comm )
{
    return PMPI_Allreduce(sendbuf, recvbuf, count, datatype, op, comm);
}

int MPI_Alltoall( const void *sendbuf, int sendcount, MPI_Datatype sendtype,
                 void *recvbuf, int recvcount, MPI_Datatype recvtype,
                 MPI_Comm comm )
{
    return PMPI_Alltoall(sendbuf, sendcount, sendtype, recvbuf, recvcount, recvtype, comm);
}

// Cleans up Global State
int MPI_Finalize() 
{
    free(WEE_MPI_RANK_PROC_NAMES[0]);
    free(WEE_MPI_RANK_PROC_NAMES);
    
    return PMPI_Finalize();
}


