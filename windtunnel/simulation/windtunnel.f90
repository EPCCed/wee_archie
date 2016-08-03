program windtunnel
!simulates an object in a windtunnel

    use vars
    use parallel

    implicit none
    
    call setup_MPI()

    call setup()
    
    call solver()
    
    call writetofile('output.dat')
    
    call MPI_Finalize(ierr)

end program
