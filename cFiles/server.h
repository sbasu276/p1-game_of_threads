#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <fcntl.h>
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <string.h>
#include <sys/epoll.h>
#include <pthread.h>
#include <stdbool.h>
#include <errno.h>


#define SIGUNUSED   31

#define _NSIG       65  /* Biggest signal number + 1  
                   (including real-time signals).  */
#define SIGRTMIN        (__libc_current_sigrtmin ())  
#define SIGRTMAX        (__libc_current_sigrtmax ()) 

#define PORT 8080

#define CACHE_SIZE 2
#define THREAD_POOL_SIZE 1
#define MAX_CLIENTS 10
#define MAX_KEY_VALUE_SIZE 512

/* When a SIGUSR1 signal arrives, set this variable. */
volatile sig_atomic_t usr_interrupt = 0;

int request_pipe_fd[2];
int response_pipe_fd[2];

bool sock_event[MAX_CLIENTS+3];
int response_count = 0;

enum req_type {GET = 0, PUT = 1, INSERT = 2, DELETE = 3};
enum state {Clean = 0, Dirty = 1};

struct continuation {
  int file_op_type; //0 for get 1 for put
	enum req_type request_type ;
  char name[1024];
  int sock_fd;
  char defn[1024];
	bool key_found;
  time_t start_time, finish_time;
}*temp;

struct node {
  char *name;
  char *defn;
	enum state myState;
  struct node *next, *prev;
}*cache_head,*cache_tail,*curr,*temp_node;

struct sockaddr_in address;
pthread_t io_thread[THREAD_POOL_SIZE];
int addrlen, opt = 1;
int *val,*incoming;
int *temp_val;
int server_fd;
int global_cache_count = 0;
pid_t my_pid;
union sigval *v;
FILE *file;

/*function list*/
int max (int a, int b); // Helper function

char *strdups(char *s); // Helper function

struct node* get (char *s);

void put (char *name, char *defn);

void *io_thread_func(); // To be completed

static void incoming_connection_handler(int sig, siginfo_t *si, void *data); // To be completed

static void outgoing_data_handler(int sig, siginfo_t *si, void *data); // To be completed

static int make_socket_non_blocking (int sfd);

int server_func();

void event_loop_scheduler();
