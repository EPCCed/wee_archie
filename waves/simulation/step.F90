module step_mod
  use vars_mod
  use comms_mod

  implicit none

  double precision, parameter :: period=2.d0
  double precision, parameter :: hhx=1.d0/dx/2.d0
  double precision, parameter :: hhy=1.d0/dy/2.d0
  double precision, parameter :: hhxx=1./dx/dx, hhyy=1./dy/dy

contains


  subroutine step()
    integer :: j

    !solves d^2 A /dt^2 = H*laplacian(A) + grad(H).grad(A) - D * dA/dt
    ! Where A is the wave function, H is the depth of the sea and D is a diffusion coefficient
    !$OMP SINGLE
    call driver()
    !$OMP END SINGLE

    !$OMP SINGLE
    call haloswap(A)
    !$OMP END SINGLE

    !get laplacian A and add to dA/dt

    call diffxx(A,Axx)
    call diffyy(A,Ayy)

    !$OMP DO
    do j=1,ny
      At(:,j) = At(:,j) + depth(:,j)*Axx(:,j)*dt
      At(:,j) = At(:,j) + depth(:,j)*Ayy(:,j)*dt
    enddo
    !$OMP END DO

    !get grad(A).grad(H), add to dA/dt

    call diffx(A,Axx)
    call diffy(A,Ayy)

    !$OMP DO
    do j=1,ny
      At(:,j) = At(:,j) + Hx(:,j)*Axx(:,j)*dt + Hy(:,j)*Ayy(:,j)*dt
    enddo
    !$OMP END DO

    !call haloswap(At)


    ! damping term: -D * dA/dt
    !$OMP DO
    do j=1,ny
      At(:,j) = At(:,j) - damping(:,j)*At(:,j)*dt
    enddo
    !$OMP END DO

    At(:,:) = At(:,:)*mask(:,:)

    !update A
    !$OMP DO
    do j=1,ny
      A(2:nx,j) = A(2:nx,j) + At(2:nx,j)*dt
    enddo
    !$OMP END DO


  end subroutine


  subroutine driver()
    A(1,1:ny) = exp(-((ymax-ymin)/2. - y(1:ny))**2)*sin(2.*pi/period*t)
    A(1,1:ny) = 1.5*sin(2.*pi/period*t)
    !A(1,1:ny) = 2*exp(-(t-5)**2)
  end subroutine

  subroutine diffx(f,fx)
    double precision, allocatable, dimension(:,:), intent(in) :: f
    double precision, allocatable, dimension(:,:), intent(inout) :: fx
    integer :: j

    !$OMP DO
    do j=1,ny
      fx(1,j) = 0.
      fx(2:nx-1,j) = hhx*(f(3:nx,j)-f(1:nx-2,j))
      fx(nx,j) = 0.
    enddo
    !$OMP END DO

  end subroutine


  subroutine diffy(f,fy)
    double precision, allocatable, dimension(:,:), intent(in) :: f
    double precision, allocatable, dimension(:,:), intent(inout) :: fy
    integer :: j

    !$OMP DO
    do j=1,ny
      fy(:,j) = hhy*(f(:,j+1)-f(:,j-1))
    enddo
    !$OMP END DO

  end subroutine

  subroutine diffxx(f,fxx)
    double precision, allocatable, dimension(:,:), intent(in) :: f
    double precision, allocatable, dimension(:,:), intent(inout) :: fxx
    integer :: j

    !$OMP DO
    do j=1,ny
      fxx(1,j) = hhxx * 2 *(f(2,j) - f(1,j))
      fxx(2:nx-1,j) = hhxx * (f(1:nx-2,j) - 2.*f(2:nx-1,j) + f(3:nx,j))
      fxx(nx,j) = hhxx*2*(f(nx-1,j) - f(nx,j))
    enddo
    !$OMP END DO
  end subroutine

  subroutine diffyy(f,fyy)
    double precision, allocatable, dimension(:,:), intent(in) :: f
    double precision, allocatable, dimension(:,:), intent(inout) :: fyy
    integer :: j

    !$OMP DO
    do j=1,ny
      fyy(:,j) = hhyy * (f(:,j+1) - 2.*f(:,j) + f(:,j-1))
    enddo
    !$OMP END DO
  end subroutine







end module
