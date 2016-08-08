module vars
!This module contains the shared variables for the simulation, as well as
!parameters controlling the runs, and some miscellaneous subroutines/functions.


implicit none

    !grid parameters

    !number of cells in x and y direction (global)
    integer, parameter :: nx_global = 576
    integer, parameter :: ny_global = 576

    !number of cells in x and y direction (local)
    integer :: nx, ny

    !size of windtunnel in metres
    real, parameter :: xrange(2) = (/ -2., 2. /)
    real, parameter :: yrange(2) = (/ -2., 2. /)

    !grid spacing in "real" units
    real :: dxx = (xrange(2)-xrange(1))/(real(nx_global)-1)
    real :: dyy = (yrange(2)-yrange(1))/(real(ny_global)-1)

    !grid spacing in computational units
    real :: dx=1.
    real :: dy=1.



    ! vorticity parameters

    logical :: vorticity=.true. !set vorticity on/off
    real :: maxvort=5. !maximum allowed vorticity
    real :: r0 = 1E3 !Reynolds number (bigger = less viscous and hence less diffusion)
    real :: vortcoeff = 0.01 !vorticity generated by wings



    !medium parameters
    real :: p0=1. !pressure (atmospheres)
    real :: rho=1. !density (atomspheres)
    real :: airspeed = 100 !km/h


    !unit conversions
    real :: dtor=3.14159265/180. !deg to rad
    real :: rho_air = 1.3 !kg/m^3
    real :: p_air = 100000. !Pa
    real :: vconv = 1000./3600. !kmph - m/s


    !iteration parameters
    real :: crossing_times=1. !number of crossing times the sim runs for
    real :: dt !timestep
    real :: cfl_r0, cfl_v !timestep CFL conditions for diffusion and advection


    !shape patameters:

    integer :: nose=0 ! (0 centre, 1 nose, 2 centre of mass)

    integer :: shape =2 !1=ellipse, 2=aerofoil

    !position of centre of shape
    real :: x0=0.
    real :: y0=0.

    !angle of attack
    real :: alpha = 0. !degrees


    !ellipse parameters
    real :: a = 0.75 !axis in x direction
    real :: b = 0.75  !axis in y direction


    !aerofoil parameters
    real :: c=2. !chord (length of aerofoil)
    real :: m=0.05 !maximum camber
    real :: t=0.2 !thickness (fraction of length)
    real :: p=0.4 !location of maximum camber (fraction of length along chord)

    !define namelists for reading in config files
    NAMELIST /vortparams/ vorticity,maxvort,r0,vortcoeff
    NAMELIST /mediumparams/  p0,rho,airspeed
    NAMELIST /shapeparams/ shape, alpha, a, b, c, m, t, p





    !global variables
    real, allocatable :: x_global(:), y_global(:), u_global(:,:), v_global(:,:)
    real, allocatable :: psi_global(:,:), vort_global(:,:)
    integer, allocatable :: mask_global(:,:), boundary_global(:,:)

    !local variables
    real, allocatable, dimension(:) :: x, y

    real, allocatable, dimension(:,:) :: psi, vort, u, v

    real, allocatable, dimension(:,:) :: psidum, dw

    integer, allocatable, dimension(:,:) :: mask, boundary



    contains

    subroutine setup_local_arrays()

        allocate(psi(0:nx+1,0:ny+1), vort(0:nx+1,0:ny+1), v(nx,ny), u(nx,ny))
        allocate(psidum(0:nx+1,0:ny+1), dw(0:nx+1,0:ny+1))
        allocate(mask(nx,ny), boundary(nx,ny))

    end subroutine


    subroutine setup_global_arrays()

        allocate(x_global(nx_global), y_global(ny_global))
        allocate(psi_global(nx_global,ny_global), vort_global(nx_global,ny_global))
        allocate(v_global(nx_global,ny_global), u_global(nx_global,ny_global))
        allocate(mask_global(nx_global,ny_global), boundary_global(nx_global,ny_global))

    end subroutine


    integer function ellipse(xdum,ydum)
    !given input values of x and y returns 0 or 1 depending upon whether the input
    !coordinartes are within or outwith the allipse

        implicit none

        real :: xdum,ydum
        real :: r
        real :: xdum2, ydum2
        real :: angle

        !rotate the input coordinates by the angle of attack
        angle=alpha*dtor

        xdum2=xdum*cos(angle) - ydum*sin(angle)
        ydum2=ydum*cos(angle) + xdum*sin(angle)

        !equation for ellipse
        r = ((xdum2-x0)/a)**2 + ((ydum2-y0)/b)**2

        if (r .ge. 1) then
            ellipse=0
        else
            ellipse=1
        endif

    end function

    integer function aerofoil(xdum,ydum)
    !given input values of x and y returns 0 or 1 depending upon whether the input
    !coordinartes are within or outwith the aerofoil
    !The aerofoil is taken to be a 4-digit NACA aerofoil (https://en.wikipedia.org/wiki/NACA_airfoil)

        implicit none

        real :: xdum, ydum
        real :: xx, xc
        real :: yc, theta, yt
        real :: xu, yu, xl, yl

        real :: xdum2, ydum2
        real :: angle

        !rotate input coordinates by angle of attack
        angle=alpha*dtor

        xdum2=xdum*cos(angle) - ydum*sin(angle)
        ydum2=ydum*cos(angle) + xdum*sin(angle)

        !shift x coords back so the centre of the aerofoil is at the origin
        xx = xdum2+(c/2.)
        xc=xx/c

        if (xx .lt. 0. .or. xx .gt. c) then
            aerofoil=0
        else
            !create yc
            if (xx .le. p*c) then
                yc=m*xx/p/p * (2*p-xc)
                theta = 2.*m/p/p * (p-xc)
            else
                yc=m*(c-xx)/(1.-p)/(1.-p) * (1+xc-2*p)
                theta=2.*m/(1.-p)/(1.-p) * (p-xc)
            endif
            theta=atan(theta)

            yt=5*t *(0.2969*sqrt(xc)-0.1260*xc-0.3516*xc*xc+0.2843*xc*xc*xc-0.1015*xc*xc*xc*xc)

            xu=xx-yt*sin(theta)
            yu=yc+yt*cos(theta)

            xl=xx+yt*sin(theta)
            yl=yc-yt*cos(theta)

            if (ydum2 .lt. yu .and. ydum2 .gt. yl) then
                aerofoil=1
            else
                aerofoil=0
            endif
        endif
    end function


end module