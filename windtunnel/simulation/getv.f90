subroutine getv()
! calculates the velocities in the grid by u = d(psi)/dy, v=-d(psi)/dx

    use vars
    use parallel

    implicit none

    integer :: i, j


    !calculate velocities
    !$OMP DO PRIVATE(j,i)
    do j=1,ny
        do i=1,nx
            if (j .gt. 1 .or. j .lt. ny) u(i,j) = (psi(i,j+1)-psi(i,j-1))/2./dy
            if (i .gt. 1 .or. i .lt. nx) v(i,j) = -(psi(i+1,j)-psi(i-1,j))/2./dx
        enddo
    enddo
    !$OMP END DO

    !apply top/bottom boundary conditions
    !$OMP SINGLE
    if (down .eq. MPI_PROC_NULL) u(:,1) = u(:,2)
    if (up .eq. MPI_PROC_NULL) u(:,ny)=u(:,ny-1)
    !$OMP END SINGLE


    !$OMP DO PRIVATE(j)
    do j=1,ny
        !apply side
        v(1,j) = v(2,j)
        v(nx,j)=v(nx-1,j)

        !ensure u and v are zero inside the object
        u(:,j)=u(:,j)*(1-mask(:,j))
        v(:,j)=v(:,j)*(1-mask(:,j))
    enddo
    !$OMP END DO



end subroutine
