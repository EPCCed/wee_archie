subroutine poisson(n)
! solves the poisson equation nabla^2 psi = -w using the Jacobi method
    use vars
    use parallel
    implicit none

    integer :: n, it
    integer :: i, j


    do it=1,n
        !$OMP DO PRIVATE(j)
        do j=0,ny+1
            psidum(:,j) = psi(:,j)
        enddo
        !$OMP END DO

        !$OMP DO PRIVATE(i,j)
        do j=1,ny
            do i=1,nx
                if (mask(i,j) .eq. 0) then
                    psi(i,j) = (psidum(i-1,j) + psidum(i+1,j))*dy*dy &
                        + (psidum(i,j-1)+psidum(i,j+1))*dx*dx +dx*dx*dy*dy*vort(i,j)
                    psi(i,j) = psi(i,j)/2./(dx*dx+dy*dy)
                endif
            enddo
        enddo
        !$OMP END DO

        !$OMP DO PRIVATE(j)
        do j=1,ny
            psi(nx+1,j) = 2.*psi(nx,j) - psi(nx-1,j)
        enddo
        !$OMP END DO

        !$OMP SINGLE
        call haloswap(psi)


        if (down .eq. MPI_PROC_NULL) psi(:,0) = 2*psi(:,1) - psi(:,2)
        if (up .eq. MPI_PROC_NULL) psi(:,ny+1) = 2*psi(:,ny) - psi(:,ny-1)
        !$OMP END SINGLE

    enddo


end subroutine
