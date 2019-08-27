program ring
    use MPI
    use wee_mpi 
    use iso_c_binding, only: C_CHAR, C_NULL_CHAR

    implicit none

    integer, parameter :: comm=MPI_COMM_WORLD
    integer :: rank, len, size, ierr, token, istat(MPI_STATUS_SIZE)
    character*(MPI_MAX_PROCESSOR_NAME) name
    call MPI_Init(ierr)
    call MPI_Comm_size(comm, size, ierr)
    call MPI_Comm_rank(comm, rank, ierr)
    call MPI_GET_PROCESSOR_NAME(name, len, ierr)
    
    ierr = f_wee_anim("arrow-up")  

    print *, "Rank, Name", rank, name
    if (rank .eq. 0) token = 1 
    if (rank .ne. 0 ) then 
        call MPI_Recv(token, 1, MPI_INTEGER, rank - 1, 0, comm, istat, ierr)
        print *, "Process ", rank, " received ", token, " from process ", rank-1 
    endif 
    
    call MPI_SSend(token, 1, MPI_INTEGER, modulo(rank + 1, size), 0, comm, ierr)

    if (rank .eq. 0) then
        call mpi_recv(token, 1, mpi_integer, size - 1, 0, comm, istat, ierr)
        print *, "process ", rank, " received ", token, " from process ", size-1 
    endif

    call MPI_Finalize(ierr)
end 
