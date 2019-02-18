module vars_mod
  use MPI
  implicit none

  !!user-definable parameters

  !grid/domain options
  integer, parameter :: nxglobal=240, nyglobal=240
  double precision, parameter :: xmin=0.d0, xmax=10.d0
  double precision, parameter :: ymin=0.d0, ymax=10.d0

  !Seafloor options
  double precision, parameter :: H0=1.d0 !base depth of sea

  double precision, parameter :: dx=(xmax-xmin)/dble(nxglobal)
  double precision, parameter :: dy=(ymax-ymin)/dble(nyglobal)

  !timesteping options
  double precision, parameter :: tmax=30.d0
  double precision, parameter :: CFL=0.2d0
  double precision, parameter :: dt = CFL*dx/H0

  !! Non-user-definable parameters
  double precision, parameter :: pi=3.1415926535d0



  integer :: nx, ny




  !x and y coordinates

  double precision, allocatable, dimension(:) :: x, y, x_global, y_global

  !gridded values
  double precision, allocatable, dimension(:,:) :: A, At, Axx, Ayy
  double precision, allocatable, dimension(:,:) :: depth, damping
  double precision, allocatable, dimension(:,:) :: hx, hy, mask

  double precision :: t

  !wave heights and times
  double precision, allocatable, dimension(:) :: maxheight, maxtime
  integer, allocatable, dimension(:) :: indices

end module
