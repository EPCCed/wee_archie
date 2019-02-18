program smooth

implicit none

integer, parameter :: maxits=10000

double precision, allocatable :: vals(:,:), mask(:,:)

integer :: nx,ny

integer :: i, j, nits

character(len=20) :: type




open(unit=10,file="coast.img",access="stream")
read(10) nx, ny
print *, nx,ny
allocate(vals(nx,ny), mask(nx,ny))
read(10) mask
close(10)

where (mask .lt. 0.9d0)
 mask=0.d0
elsewhere
mask=1.d0
endwhere

vals = mask

!$OMP PARALLEL
do nits = 1,maxits
    !$OMP WORKSHARE
    vals=vals*mask
    !$OMP END WORKSHARE
    !$OMP SINGLE
    if (mod(nits,100) .eq. 0) print *, nits, "of", maxits
    !$OMP END SINGLE
    !$OMP DO private(i)
    do j=2,ny-1
        do i=2,nx-1
           vals(i,j) = 0.25*(vals(i-1,j) + vals(i+1,j) + vals(i,j-1) + vals(i,j+1))
        enddo
    enddo
    !$OMP END DO
    !$OMP SINGLE
    do i=2,nx-1
           vals(i,1) = 0.25*(vals(i-1,1) + vals(i+1,1) + vals(i,ny) + vals(i,2))
    enddo
    do i=2,nx-1
           vals(i,ny) = 0.25*(vals(i-1,ny) + vals(i+1,ny) + vals(i,ny-1) + vals(i,1))
    enddo
    !$OMP END SINGLE
enddo
!$OMP END PARALLEL

!vals=vals*0.95+0.05

open(unit=11,file="depth_profile.dat",access="stream")
write(type,"(a)") "depth_profile"
write(11) type
write(11) nx, ny
write(11) 0.d0
write(11) vals
close(11)

open(unit=11,file="mask.dat",access="stream")
write(type,"(a)") "mask"
write(11) type
write(11) nx, ny
write(11) 0.d0
write(11) mask
close(11)

! open(unit=11,file="damping.dat",access="stream")
! write(type,"(a)") "damping"
! write(11) type
! write(11) nx, ny
! write(11) 0.d0
! write(11) (1-vals)*0.2
! close(11)



end program
