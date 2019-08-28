module io_mod
  use vars_mod
  use wee_mpi
  use comms_mod
  use MPI

  implicit none
contains

  !reads in a file (rank 0) and distributes its contents to the compute processes.
  subroutine read_file(fname, type)
    character(len=20), intent(in) :: fname, type
    character(len=20) :: typetest
    integer :: nxtest, nytest
    double precision :: timetest

    double precision, allocatable, dimension(:,:) :: data

    if (rank .eq. 0) then
      print *,""
      print *, "Reading file '",trim(fname),"'"
      open(unit=10,file=fname, access="stream")

      read(10) typetest
      read(10) nxtest,nytest
      read(10) timetest

      if ((nxtest .ne. nxglobal) .or. (nytest .ne. nyglobal)) then
        print *, "Error: incompatible grid sizes"
        print *, "File reports", nxtest, nytest
        print *, "Code expects", nxglobal, nyglobal
        call MPI_Abort(comm,1,ierr)
        stop
      endif

      allocate(data(nxglobal,nyglobal))
      read(10) data
      close(10)

      if (typetest .ne. type) then
        print*, "Error: invalid variable type"
        print*, "Expected '",type,"'"
        print *,"Got      '",typetest,"'"
        print *, "aborting"
        call MPI_Abort(comm,1,ierr)
      endif
    endif


    if (type .eq. "depth") then
      call distribute_data(data,depth)
    else if (type .eq. "mask") then
      call distribute_data(data,mask)
    else if (type .eq. "damping") then
      call distribute_data(data,damping)
    else
      print *, 'Error invalid type'
      stop
    endif

    if (rank .eq. 0) deallocate(data)

  end subroutine



  subroutine write_file(fname,type)
    character(len=20), intent(in) :: fname
    double precision, allocatable, dimension(:,:) :: data
    character(len=20), intent(in) :: type

    if (rank .eq. 0) allocate(data(nxglobal,nyglobal))

    if (type .eq. "depth") then
      call collate_data(depth,data)
    else if (type .eq. "A") then
      call collate_data(A,data)
    else
      print *, "Error: invalid type: ", type
      call MPI_Finalize(ierr)
      stop
    endif

    if (rank .eq. 0) then
      print *, "Opening '", trim(fname), "' for writing"
      open(unit=20, file=fname, access="stream",status="replace")
      write(20) type
      write(20) nxglobal, nyglobal
      write(20) t
      write(20) data
      close(20)
      deallocate(data)
    endif
  end subroutine

  subroutine write_waveheights()
    character(len=20) :: fname
    double precision, allocatable, dimension(:) :: data1, data2
    character(len=20) :: type

    if (rank .eq. 0) allocate(data1(nyglobal), data2(nyglobal))

    call collate_1d(maxheight,data1)
    call collate_1d(maxtime,data2)

    type="waveheights"
    fname="waveheights.dat"

    if (rank .eq. 0) then
      print *, "Opening '", trim(fname), "' for writing"
      open(unit=20, file=fname, access="stream",status="replace")
      write(20) type
      write(20) nxglobal, nyglobal
      write(20) t
      write(20) data1!sqrt(data1)/tmax
      write(20) data2
      close(20)
      deallocate(data1,data2)
    endif
  end subroutine


  !data global data held on rank 0 (io server or otherwise) distributed to other processes
  subroutine distribute_data(data,var)
    double precision, allocatable, dimension(:,:), intent(in) :: data
    double precision, dimension(:,:), allocatable, intent(inout) :: var

    integer :: pstart, pend, p
    integer :: jstart, jend
    integer :: dy
    integer :: status(MPI_STATUS_SIZE)
    integer :: err
    
    err = wee_flags(1) 

    dy = nyglobal/csize

    if (rank .eq. 0) then

      if (ioserver_enabled) then !send all data to procs 1:end
        pstart=1
        pend=csize
      else !Still want to send to 1:end, but also copy local data in memory
        pstart=0
        pend=csize-1
        var(:,1:dy) = data(:,1:dy)
      endif

      do p=1,pend
        jstart=(p-pstart)*dy+1
        jend=jstart+dy-1
        print *, "sending to", p, jstart, jend
        call MPI_Send(data(:,jstart:jend),nx*dy,MPI_DOUBLE_PRECISION,p,0,comm,ierr)
      enddo

    else
      call MPI_Recv(var(1,1),nx*ny,MPI_DOUBLE_PRECISION,0,0,comm,status,ierr)
    endif

    call MPI_Barrier(comm,ierr)

  end subroutine


  !collects data from all compute processes onto rank 0
  subroutine collate_data(var,data)
    double precision, intent(in), dimension(:,:), allocatable :: var
    double precision, intent(inout), allocatable, dimension(:,:) :: data
    integer :: request
    integer :: p, pstart, pend, dy, jstart, jend
    integer :: status(MPI_STATUS_SIZE)
    integer, parameter :: TAG=10
    integer :: err
    
    err = wee_flags(1) 

    dy = nyglobal/csize

    if (rank .ne. 0) then
      !send our data
      call MPI_Send(var(:,1:ny),nx*ny,MPI_DOUBLE_PRECISION,0,TAG,comm,ierr)
    else
      if (.not. ioserver) then
        data(:,1:ny) = var(:,1:ny) !can copy local data in memory
        pstart=0
        pend=csize-1
      else
        pstart=1
        pend=csize
      endif

      !receive data
      do p=1,pend
        jstart=(p-pstart)*dy+1
        jend=jstart+dy-1
        !print *, p, jstart, jend
        call flush()
        call MPI_Recv(data(1,jstart),nx*dy,MPI_DOUBLE_PRECISION,p,TAG,comm,status,ierr)
      enddo
    endif

  end subroutine

  subroutine collate_1d(var,data)
    double precision, intent(in), dimension(:), allocatable :: var
    double precision, intent(inout), allocatable, dimension(:) :: data
    integer :: request
    integer :: p, pstart, pend, dy, jstart, jend
    integer :: status(MPI_STATUS_SIZE)
    integer, parameter :: TAG=10
    integer :: err
    
    err = wee_flags(1) 

    dy = nyglobal/csize

    if (rank .ne. 0) then
      !send our data
      call MPI_Send(var(1:ny),ny,MPI_DOUBLE_PRECISION,0,TAG,comm,ierr)
    else
      if (.not. ioserver) then
        data(1:ny) = var(1:ny) !can copy local data in memory
        pstart=0
        pend=csize-1
      else
        pstart=1
        pend=csize
      endif

      !receive data
      do p=1,pend
        jstart=(p-pstart)*dy+1
        jend=jstart+dy-1
        !print *, p, jstart, jend
        call flush()
        call MPI_Recv(data(jstart),dy,MPI_DOUBLE_PRECISION,p,TAG,comm,status,ierr)
      enddo
    endif

  end subroutine




end module
