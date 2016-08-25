module parallel
!this module contains subroutines and variables concerning the parallelisation
!of the code. This includes MPI and OpenMP.

    use MPI
    use vars
    use OMP_lib

    implicit none

    integer :: threads=2 !number of openMP threads per MPI process

    integer :: isize, irank !size and rank

    integer :: up, down !processes above and below the current one in the Cartesian topology

    integer :: comm=MPI_COMM_WORLD
    integer :: ierr

    integer, parameter :: ndims=1 !number of dimensions of parallelisation
    integer :: dims(ndims)
    logical :: periods(ndims) = (/ .false. /) !non periodic boundary conditions
    logical :: reorder = .false. !reorder the ranks for more efficiency?
    integer :: status(MPI_STATUS_SIZE)

    contains

    subroutine setup_MPI()

        implicit none

        call OMP_set_num_threads(threads) !set number of OpenMP Threads

        call MPI_Init(ierr)

        call MPI_Comm_size(MPI_COMM_WORLD, isize, ierr)


        if (modulo(ny_global,isize) .ne. 0) then
            print*, "Incompatible ny with number of processors"
            stop
        endif

        ny = ny_global/isize
        nx = nx_global

        !create Cartesian grid
        call MPI_Dims_create(isize,ndims,dims,ierr)
        if (ierr .ne. MPI_SUCCESS) then
        print*, "DIMS not created properly"
        stop
        endif

        CALL MPI_Cart_create(MPI_COMM_WORLD,ndims,dims,periods,reorder,comm,ierr)


        call MPI_Comm_rank(comm, irank, ierr)

        !find the processes above and below the current one
        call MPI_Cart_shift(comm,0,1,down,up,ierr)

        if (irank .eq. 0) then
            print*,"Running on ",isize," processes"
            print*,"With",threads," threads per process"
            print*,"Total parallel regions=",isize*threads
        endif


    end subroutine


    subroutine distribute_data()
    ! Takes the global arrays and distributes them to the processes

        call MPI_Scatter(u_global,nx*ny,MPI_REAL,u,nx*ny,MPI_REAL,0,comm,ierr)
        call MPI_Scatter(v_global,nx*ny,MPI_REAL,v,nx*ny,MPI_REAL,0,comm,ierr)

        call MPI_Scatter(psi_global,nx*ny,MPI_REAL,psi(1:nx,1:ny),nx*ny,MPI_REAL,0,comm,ierr)
        call MPI_Scatter(vort_global,nx*ny,MPI_REAL,vort(1:nx,1:ny),nx*ny,MPI_REAL,0,comm,ierr)

        call MPI_Scatter(boundary_global,nx*ny,MPI_INTEGER,boundary,nx*ny,MPI_INTEGER,0,comm,ierr)
        call MPI_Scatter(mask_global,nx*ny,MPI_INTEGER,mask,nx*ny,MPI_INTEGER,0,comm,ierr)


    end subroutine

    subroutine collate_data()
    !takes the local arrays and collects them into the global arrays

        call MPI_Gather(u,nx*ny,MPI_REAL,u_global,nx*ny,MPI_REAL,0,comm,ierr)
        call MPI_Gather(v,nx*ny,MPI_REAL,v_global,nx*ny,MPI_REAL,0,comm,ierr)

        call MPI_Gather(psi(1:nx,1:ny),nx*ny,MPI_REAL,psi_global,nx*ny,MPI_REAL,0,comm,ierr)
        call MPI_Gather(vort(1:nx,1:ny),nx*ny,MPI_REAL,vort_global,nx*ny,MPI_REAL,0,comm,ierr)

        call MPI_Gather(boundary,nx*ny,MPI_INTEGER,boundary_global,nx*ny,MPI_INTEGER,0,comm,ierr)
        call MPI_Gather(mask,nx*ny,MPI_INTEGER,mask_global,nx*ny,MPI_INTEGER,0,comm,ierr)

    end subroutine

    subroutine haloswap(array)
    ! swaps the halo values for 'array'

        implicit none
        real :: array(0:nx+1,0:ny+1)

        !send top, recieve bottom
        call MPI_Sendrecv(array(:,ny),nx+2,MPI_REAL,up,1,array(:,0),nx+2,MPI_REAL,down,1,comm,status,ierr)

        !send bottom, receive top
        call MPI_Sendrecv(array(:,1),nx+2,MPI_REAL,down,0,array(:,ny+1),nx+2,MPI_REAL,up,0,comm,status,ierr)

    end subroutine


end module
