subroutine writetofile(fname)
!writes the results of the simulation to a binary file
!also calculates the pressure and ram pressure forces on the object
    use vars
    use parallel
    implicit none

    character (len=*) :: fname
    real, allocatable :: u2(:,:), pressure(:,:)
    real :: bernoulli
    integer :: i, j

    real, allocatable, dimension(:,:) :: toppres, sidepres, du, dv
    real, allocatable, dimension(:,:) ::  sideboundary, toptheta, sidetheta

    real :: frontarea, toparea


    real :: plift, pdrag, ram, ramlift, lift, drag
    real :: u0
    real :: c_lift, c_drag


    !update velocities
    call getv()

    !populate global array
    call collate_data()


    if (irank .eq. 0) then

        allocate(u2(nx_global,ny_global))
        allocate(pressure(nx_global,ny_global))
        allocate(sideboundary(nx_global,ny_global))

        allocate(toppres(nx_global,ny_global), sidepres(nx_global,ny_global))
        allocate(du(nx_global,ny_global), dv(nx_global,ny_global))
        allocate(toptheta(nx_global,ny_global),sidetheta(nx_global,ny_global))

        ! |v|^2
        u2 = u_global*u_global + v_global*v_global

        ! incoming velocity
        u0=u2(1,ny_global/2)

        !From Bernoulli's equation 1/2rhov^2 + p = const
        bernoulli = p0*p_air + 0.5*rho*u0 *(rho_air) * (airspeed*vconv)**2 !bernoulli constant for the gas

        pressure = bernoulli - 0.5*rho*u2 *(rho_air) * (airspeed*vconv)**2 !pressure as a function of position

        pressure=pressure/p_air!*(1-mask_global)


        !calculate pressure on top/bottom boundary (pressure 1 gridcell up/down from boundary)
        toppres(:,:)=0
        toptheta(:,:)=0
        do j=1,ny_global
            do i=1,nx_global
                if (boundary_global(i,j) .ne. 0) then
                    if (boundary_global(i,j) .eq. 1) then !top
                        toppres(i,j) = pressure(i,j+2)
                        !toptheta(i,j) = atan(v_global(1,j+2),u_global(i,j+2))
                    else !bottom
                        toppres(i,j) = pressure(i,j-2)
                        !toptheta(i,j) = atan(v_global(1,j-2),u_global(i,j-2))
                    endif
                endif
            enddo
        enddo


        sideboundary(:,:) = 0



        !find the side boundary
        do j=1,ny_global
            do i=1,nx_global
                if(mask_global(i,j) .eq. 1) then
                    sideboundary(i,j)=sideboundary(i,j)-1 !left - normal vector is negative
                    exit
                endif
            enddo

            if (i .ne. nx) then
                do i=nx_global,1,-1
                    if (mask_global(i,j) .eq. 1) then
                        sideboundary(i,j) = sideboundary(i,j)+1 !right, normal vector is positive
                        exit
                    endif
                enddo
            endif
        enddo

        !get pressure and u,v on side boundary

        sidepres=0
        dv=0
        du=0
    !    sidetheta(:,:)=0.
        do j=1,ny_global
            do i=1,nx_global
                if (sideboundary(i,j) .ne. 0) then
                    if (sideboundary(i,j) .lt. 0) then !front
                        sidepres(i,j) = pressure(i-2,j)
                        dv(i,j) = v_global(i-2,j)
                        du(i,j)= abs(u_global(i-2,j)-sqrt(u0))
                        !sidetheta(i,j) = atan(v_global(i-2,j),u_global(i-2,j))
                    else !back
                        sidepres(i,j) = pressure(i+2,j)
                        !sidetheta(i,j) = atan(v_global(i+2,j),u_global(i+2,j))
                    endif
                endif
            enddo
        enddo

        !toptheta(:,:)=0.
        !sidetheta(:,:) = 3.141592/2.


        plift = -sum( toppres*boundary_global)*dxx * p_air ! f = oint -p(yhat.da)
        pdrag = -sum( sidepres*sideboundary)*dyy*p_air !! f = oint -p(xhat.da)

        !ram pressure:
        ! f = dp/dt = m*dv/dt.
        !in n seconds, u0*rho kg of air pass through each m^2 per unit time
        ! if the gas changes velocity by dv then
        ! f = u0*rho*dv

        ram =-sum(sideboundary*sqrt(u0)*du) *(rho*rho_air) * (vconv*airspeed)**2 * dyy
        ramlift =-sum(sideboundary*sqrt(u0)*(dv)) *(rho*rho_air) * (vconv*airspeed)**2 * dyy

        lift=plift+ramlift
        drag=pdrag+ram


        frontarea=sum(abs(sideboundary))/2*dyy
        !print*,"frontarea=",frontarea

        toparea=sum(abs(boundary_global))/2*dxx
        !print*,'toparea=',toparea

        !calculate lift and drag coefficients
        ! C_l = lift/(1/2 rho u^2) / A

        c_lift = lift / (0.5*rho*u0*rho_air * (vconv*airspeed)**2 )/toparea

        !c_d = drag /(1/2*rho*u^2)/A

        c_drag= drag / (0.5*rho*u0*rho_air * (vconv*airspeed)**2 )/frontarea




        print*,"-------------------------------------------------------------------------------"
        print *, "pressure lift=", plift
        print *, "ram lift     =", ramlift
        print *,''
        print *, "pressure drag=", pdrag
        print *, "ram drag     =", ram
        print*, ''
        print*," ------------------------------------"
        print *, "|Total lift   =", lift, "N/m |"
        print* , "|Total drag   =", drag, "N/m |"
        print *, ' ----------------------------------'
        print *, "Lift Coefficient=",c_lift
        print *, "Drag Coefficient=",c_drag
        print *, "Lift to drag    =",lift/drag
        print *, ''





        u2=sqrt(u2)*airspeed

        open (unit=10,file=fname,access='stream',status='REPLACE')
        write(10) nx_global,ny_global
        write(10) x_global, y_global
        write(10) psi_global/(1-mask_global)
        write(10) mask_global
        write(10) u_global, v_global
        write(10) u2/(1-mask_global), pressure/(1-mask_global)
        write(10) vort_global/(1-mask_global)
        write(10) plift, ramlift, pdrag, ram, lift, drag
        write(10) c_lift, c_drag, c_lift*toparea, c_drag*frontarea
        close(10)

        print *, "Written '",fname,"' to file."
        print*,"-------------------------------------------------------------------------------"

    endif

end subroutine
