subroutine poisson(n)
! solves the poisson equation nabla^2 psi = -vort using the Jacobi method with successive over-relaxation (SOR)

!Jacobi method: psi(i,j,n+1) = 1/4( psi(i-1,j,n) + psi(i+1,j,n) + psi(i,j-1,n) + psi(i,j+1,n) + vort(i,j) )
! SOR: psi(n+1) = (1-w)*psi(n) + w*JacobiRHS

! First, the grid is split up into a chessboard, depending on whether i+j is even or odd
! Next the Jacobi SOR method is applied to even squares (using the odd squares to update even squares)
! Then the Jacobi SOR method is applied to odd squares (using the updated values of the even squares)

    use vars
    use parallel
    implicit none

    integer :: n, it
    integer :: i, j

    real :: w !successive over-relaxation parameter

    w=1./(1+pi/nx_global) !optimal value of w



    do it=1,n
        !! old Jacobi method
        ! !$OMP DO PRIVATE(j)
        ! do j=0,ny+1
        !     psidum(:,j) = psi(:,j)
        ! enddo
        ! !$OMP END DO

        ! !$OMP DO PRIVATE(i,j)
        ! do j=1,ny
        !     do i=1,nx
        !         if (mask(i,j) .eq. 0) then
        !             psi(i,j) = (psidum(i-1,j) + psidum(i+1,j))*dy*dy &
        !                  + (psidum(i,j-1)+psidum(i,j+1))*dx*dx +dx*dx*dy*dy*vort(i,j)
        !             psi(i,j) = psi(i,j)/2./(dx*dx+dy*dy)
        !         endif
        !     enddo
        ! enddo
        ! !$OMP END DO

        !update even squares
        !$OMP DO PRIVATE(i,j)
        do j=1,ny
            do i=1,nx
                if (mask(i,j) .eq. 0) then
                    if (mod(i+j,2) .eq. 0) then
                        psi(i,j) = (1-w)*psi(i,j) +w*( (psi(i-1,j) + psi(i+1,j))*dy*dy &
                             + (psi(i,j-1)+psi(i,j+1))*dx*dx +dx*dx*dy*dy*vort(i,j) ) &
                             /2./(dx*dx+dy*dy)
                    endif
                endif
            enddo
        enddo
        !$OMP END DO

         !$OMP SINGLE
         call haloswap(psi)
         !$OMP END SINGLE
         !$OMP BARRIER

        !update odd squares
        !$OMP DO PRIVATE(i,j)
        do j=1,ny
            do i=1,nx
                if (mask(i,j) .eq. 0) then
                    if (mod(i+j,2) .eq. 1) then
                        psi(i,j) = (1-w)*psi(i,j) +w*( (psi(i-1,j) + psi(i+1,j))*dy*dy &
                             + (psi(i,j-1)+psi(i,j+1))*dx*dx +dx*dx*dy*dy*vort(i,j) ) &
                             /2./(dx*dx+dy*dy)
                    endif
                endif
            enddo
        enddo
        !$OMP END DO

        !apply right boundary condition
        !$OMP DO PRIVATE(j)
        do j=1,ny
            psi(nx+1,j) = 2.*psi(nx,j) - psi(nx-1,j)
        enddo
        !$OMP END DO

        !$OMP SINGLE
        call haloswap(psi)
        !apply top/bottom boundary conditions
        if (down .eq. MPI_PROC_NULL) psi(:,0) = 2*psi(:,1) - psi(:,2)
        if (up .eq. MPI_PROC_NULL) psi(:,ny+1) = 2*psi(:,ny) - psi(:,ny-1)
        !$OMP END SINGLE
        !$OMP BARRIER

    enddo


end subroutine
