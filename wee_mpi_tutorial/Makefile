WMPI_DIR := ../wee_mpi
LDFLAGS := -L $(WMPI_DIR) -Wl,-rpath,$(WMPI_DIR)  -lwee_mpi -lmpi -lcurl
CFLAGS_INC := -I ../wee_mpi
CFLAGS := -std=c11 -g -Wall $(CFLAGS_INC)

SRCS := $(wildcard *.c)
PRGS := $(patsubst %.c,%,$(SRCS))

OBJS := $(patsubst %,%.o,$(PRGS))

all : $(PRGS)

.SECONDEXPANSION:
OBJ = $(patsubst %,%.o,$@)
BIN = $@

$(PRGS): $(OBJS)
	$(CC) $(OBJ)  $(LDFLAGS) -o $(BIN)

veryclean:
	$(RM) $(PRGS)

rebuild: veryclean all
