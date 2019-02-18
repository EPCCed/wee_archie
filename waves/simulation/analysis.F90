module analysis_mod
  use vars_mod

contains

  subroutine get_indices()
    integer :: i, j

    do j=1,ny
      do i=nx,1,-1
        if (mask(i,j) .gt. 0.1) exit
      enddo
      !print *, "j=", j, "i=",i
      indices(j) = i
    enddo

  end subroutine

  subroutine analyse()
    integer :: j
    !$OMP DO
    do j=1,ny
      !maxheight(j) = maxheight(j) + A(indices(j),j)**2 * dt
      if (abs(A(indices(j),j)) .gt. maxheight(j)) then
       maxheight(j) = abs(A(indices(j),j))
       maxtime(j) = t
      endif
    enddo
    !$OMP END DO

  end subroutine

end module
