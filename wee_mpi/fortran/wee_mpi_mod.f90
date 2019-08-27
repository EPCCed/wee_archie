module wee_mpi
implicit none 
    interface 
        integer function wee_flags(silent) bind(C)
            integer, value:: silent
        end function 

        integer function wee_anim(string) bind(C)
            use iso_c_binding, only: c_char
            character(kind=c_char) :: string(*)
        end function
    end interface
    contains
        integer function f_wee_anim(string)
            use iso_c_binding, only: C_CHAR, C_NULL_CHAR
            character(len=*, kind=c_char), intent(in) :: string
            f_wee_anim  = wee_anim(string//C_NULL_CHAR) 
        end function
end module
