program main
  use vars_mod
  use comms_mod
  use io_mod
  use step_mod
  use analysis_mod
  use MPI
  use omp_lib

  implicit none

  double precision :: ttarget=0.d0
  double precision :: dttarget=0.5
  integer :: i, j, fno
  integer :: jstart
  double precision :: t1, t2

  character(len=20) :: fname, type

  !initialise parallel decomposition, ioserver etc
  call init_comms()

  !allocate memory for compute processes
  if (.not. ioserver) then

    allocate(x(nx), x_global(nxglobal), y(0:ny+1), y_global(nyglobal))
    allocate(A(nx,0:ny+1), At(nx,0:ny+1), Axx(nx,0:ny+1), Ayy(nx,0:ny+1))
    allocate(depth(nx,0:ny+1), damping(nx,0:ny+1))
    allocate(hx(nx,0:ny+1), hy(nx,0:ny+1), mask(nx,0:ny+1))
    allocate(maxheight(ny), maxtime(ny), indices(ny))

    do i=1,nxglobal
      x_global(i) = (i-1)*dx
      x(i)=(i-1)*dx
    enddo

    do j=1,nyglobal
      y_global(j) = (j-1)*dy
    enddo

    jstart = (nyglobal/csize)*crank+1
    y(1:ny) = y_global(jstart:jstart+ny-1)

  endif

  !create a depth profile (will eventually be a seperate file)
  if (rank .eq. 0) then
    !call make_depth()
  endif

  !read in the depth profile
  fname="depth.dat"
  type="depth"
  call read_file(fname,type)

  fname="mask.dat"
  type="mask"
  call read_file(fname,type)

  fname="damping.dat"
  type="damping"
  call read_file(fname,type)

  if (.not. ioserver) then
    call haloswap(depth)
    call diffx(depth,Hx)
    call diffy(depth,Hy)
    print *, maxval(abs(hx)), maxval(abs(hy))
    call get_indices()
  endif

  ! open(unit=10,file="test",access="stream")
  ! write(10) nx, ny
  ! write(10) depth(1:nx,1:ny)
  ! write(10) Hx(1:nx,1:ny), Hy(1:nx, 1:ny)
  ! write(10) mask(1:nx,1:ny), damping(1:ny, 1:ny)
  ! close(10)
  !
  ! call MPI_Finalize(ierr)
  ! stop



  !begin step

  t=0.d0
  i=0
  fno=0

  call MPI_Barrier(comm,ierr)
  t1=MPI_Wtime()

  if (.not. ioserver) mask(:,:) = 1.d0

  !$OMP PARALLEL
  do while (t .lt. tmax)
    if (rank .eq. 0 .and. i .eq. 0) then
      if (OMP_GET_THREAD_NUM() .eq. 0) then
        print *, "Using nthreads=", OMP_GET_NUM_THREADS()
      endif
    endif

    !$OMP SINGLE
    if (t .ge. ttarget .or. 1 .eq. 0) then
      ttarget=ttarget+dttarget
      write(fname,"(a,i5.5,a)") "A_",fno,".dat"
      type="A"
      call write_file(fname,type)
      fno=fno+1
    endif
    !$OMP END SINGLE


    if (.not. ioserver) then
      call step()
      call analyse()
    endif

    !$OMP SINGLE
    t=t+dt
    i=i+1
    !$OMP END SINGLE
  enddo
  !$OMP END PARALLEL


  call MPI_Barrier(comm,ierr)
  t2=MPI_Wtime()

  call write_waveheights()

  if (rank .eq. 0) then
    print *, "Time taken=", t2-t1
  endif


  call MPI_Finalize(ierr)



contains

  subroutine make_depth()
    double precision, allocatable, dimension(:,:) :: data
    integer :: i, j
    character(len=20) :: type

    allocate(data(nxglobal,nyglobal))

    do j=1,nyglobal
      data(:,j) = 1.
    enddo

    type="depth"

    open(unit=10,file="depth.dat", access="stream")
    write(10) type
    write(10) nxglobal,nyglobal
    write(10) t
    write(10) data
    close(10)

    deallocate(data)

  end subroutine

  subroutine check_output()
    double precision, allocatable, dimension(:,:) :: data
    integer :: j
    character(len=20) :: type
    integer :: nxdum, nydum
    double precision :: tdum

    allocate(data(nxglobal,nyglobal))

    open(unit=10,file="test.dat",access="stream")
    read(10) type
    read(10) nxdum,nydum
    read(10) tdum
    read(10) data

    print *, "Validating output"

    do j=1,nyglobal
      print*, j, data(2,j)
    enddo

    close(10)

    deallocate(data)

  end subroutine


end program
