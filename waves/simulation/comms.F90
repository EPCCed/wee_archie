!Sets up the parallel decomposition, IO server (if applicable) and deals with haloswapping
module comms_mod
  use MPI
  use vars_mod

  implicit none

  logical, parameter :: IOSERVER_REQUESTED=.true.
  logical, parameter :: periodic = .true.


  logical :: ioserver_enabled, ioserver

  integer, parameter :: comm=MPI_COMM_WORLD
  integer :: rank, size, ierr
  integer :: ccomm, csize, crank

  integer :: up, down

contains

  !initialise commuications, setup ioserver and decomposition
  subroutine init_comms()
    integer :: group

    call MPI_Init(ierr)

    !get global number of processes and rank
    call MPI_comm_size(comm,size,ierr)
    call MPI_Comm_rank(comm,rank,ierr)


    !Determine if we should use the IO server functionality
    IOSERVER_ENABLED = IOSERVER_REQUESTED .and. (size .gt. 1)

    if (rank .eq. 0) then
      Print *, "Welcome to the EPCC wave simulator!"
      print *, ""
      if (IOSERVER_ENABLED) then
        write(*,"(a,i2,a)") "IO Server enabled: 1 IO server process and ",size-1," compute processes"
      else
        write(*,"(a,i2,a)") "IO Server disabled: 0 IO server processs and ",size," compute processes"
      endif
      print *, ""
    endif

    ! Split communicator if using the IO server. Else use original communicator
    if (IOSERVER_ENABLED) then
      if (rank .eq. 0) then
        group = MPI_UNDEFINED
        ioserver=.true.
      else
        group = 1
        ioserver=.false.
      endif
      !create commuicator group for compute processes
      call MPI_Comm_split(comm, group,rank,ccomm,ierr)
      csize=size-1
    else
      ccomm=comm
      csize=size
      ioserver=.false.
    endif


    !check if we can divide grid into csize bits
    if (mod(nyglobal,csize) .ne. 0) then
      if (rank .eq. 0) print *, "Error: Cannot divide spatial domain into nprocs"
      call MPI_Finalize(ierr)
      stop
    endif

    ny=nyglobal/csize
    nx=nxglobal

    if (rank .eq. 0) write(*,"(a,i3,a,i3,a)") "Each process contains ",nx," x ",ny," cells"
    if (rank .eq. 0) print *, "Processes and neighbours:"
    !set up decomposition and local grids
    if (.not. ioserver) then
      !create Cartesian processor topology
      call MPI_Cart_create(ccomm, 1, (/csize/), (/periodic/),.False.,ccomm,ierr)

      !determine rank of process in this topology
      call MPI_Comm_rank(ccomm,crank,ierr)

      !determine neighbours
      call MPI_Cart_shift(ccomm,0,1,down,up,ierr)

      print *, "rank, down, up", crank, down,up
    endif

    call flush()

    call MPI_Barrier(comm,ierr)




  end subroutine

  subroutine haloswap(arr)
    double precision, intent(inout), dimension(:,:), allocatable :: arr
    integer :: status(MPI_STATUS_SIZE)

    !send up, recv down
    call MPI_Sendrecv(arr(:,ny), nx, MPI_DOUBLE_PRECISION, up, 1,&
                      arr(:,0),nx, MPI_DOUBLE_PRECISION, down, 1, &
                      ccomm, status,ierr)

    !send down recv up
    call MPI_Sendrecv(arr(:,1), nx, MPI_DOUBLE_PRECISION, down, 1,&
                      arr(:,ny+1),nx, MPI_DOUBLE_PRECISION, up, 1, &
                      ccomm, status,ierr)

  end subroutine


end module
