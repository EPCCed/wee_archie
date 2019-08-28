CC 	= mpicc
DEBUG = 0
CFLAGS = -std=c11 -fPIC -Wall -Wextra -O2 -g -DDEBUG=$(DEBUG) -DPROFILELIB
LDFLAGS = -shared -lcurl 

RM = rm -f 

TARGET_LIB = libwee_mpi.so 
SRCS = wee_mpi.c
OBJS = $(SRCS:.c=.o)

.PHONY: all
all: ${TARGET_LIB}

$(TARGET_LIB): $(OBJS)
	$(CC) ${LDFLAGS} -o $@ $^

$(SRCS:.c=.d):%.d:%.c
	$(CC) $(CFLAGS) -MM $< >$@

include $(SRCS:.c=.d)

.PHONY: clean
clean:
	-${RM} ${TARGET_LIB} ${OBJS} $(SRCS:.c=.d)
