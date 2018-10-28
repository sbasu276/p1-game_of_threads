#include "server.h"
#include <arpa/inet.h>


int max (int a, int b) {
  return (a>b?a:b);
}

char *strdups(char *s) {/* make a duplicate of s */
    char *p;
    p = (char *) malloc(strlen(s)+1); /* +1 for ’\0’ */
    if (p != NULL)
       strcpy(p, s);
    return p;
}

struct node* get (char *s) {
  curr = cache_head;
  while (curr != NULL) {
    if (strcmp(curr->name, s) == 0) {
      //found in cache, move node to head of list
      // and return value of key

      if(curr != cache_head) {
        temp_node = curr->prev;
        if (curr == cache_tail) {
          temp_node->next = NULL;
          cache_tail = temp_node;
        } else {
          temp_node->next = curr->next;
          curr->next->prev = temp_node;
        }

        cache_head->prev = curr;
        curr->next = cache_head;
        curr->prev = NULL;
        cache_head = curr;
      }
      return cache_head;
    }
    curr = curr->next;
  }
  // Key not found in cache
  return NULL;
}

void put (char *name, char *defn) {
  struct node *cache_entry;
  if ((cache_entry = get(name)) == NULL) {
    // value not in cache
    temp_node = (struct node*) malloc (sizeof(struct node));
    temp_node->name = strdups(name);
    temp_node->defn = strdups(defn);
		temp_node->state = Dirty;
    temp_node->next = temp_node->prev = NULL;
    if(cache_head == NULL) {
      cache_head = cache_tail = temp_node;
    } else {
      cache_head->prev = temp_node;
      temp_node->next = cache_head;
      temp_node->prev = NULL;
      cache_head = temp_node;
    }
    if (global_cache_count >= CACHE_SIZE) {
      // cache is full, evict the last node
      // insert a new node in the list
			// Write-back if it is a dirty entry	
			if(cache_tail->state == Dirty){
        pending_node = (struct pending_queue*) malloc (sizeof(struct pending_queue));
        pending_node->cont = cache_tail;
        pending_node->next = NULL;
        if (pending_head == NULL) {
          pending_head = pending_tail = pending_node;
        } else {
          pending_tail->next = pending_node;
          pending_tail = pending_node;
        }
			}
      cache_tail = cache_tail->prev;
      cache_tail->next = NULL;
      //TODO: Free the memory as you evict nodes
    } else {
      // Increase the count
      global_cache_count++;
    }
  } else {
    // update cache entry
    cache_entry->defn		= strdups(defn);
		cache_entry->state	= Dirty;
  }
}

void *io_thread_func() {
  // This function should handle incoming I/O requests,
  // once the request is processed, the thread notifies
  // the event schuduler using a signal

  // Complete this function to implement I/O functionality
  // for incoming requests and handle proper synchronization
  // among other helper threads
	int retval, written, i;
	size_t len;
	char *token, *request_key, *request_value, *request_type, *response_value, *request;
	FILE* myFile;

  while(1) {
    if (pending_head != NULL) {

	    if((myFile = fopen("names.txt", "rb+")) == NULL){
				printf("Unable to open file\n");
				exit(0);
			}

			request = pending_head->cont->buffer;
			char* line = malloc (MAX_KEY_VALUE_SIZE);
			request_type	= strtok(request, " ");
			request_key		= strtok(NULL, " ");
			request_value	= strtok(NULL, " ");
			printf("Working on %s %s request\n", request_type, request_key);

			len = MAX_KEY_VALUE_SIZE;
			rewind(myFile);

      if (pending_head->cont->request_type == 0) { //GET Request
				while((retval = getline(&line, &len, myFile)) > 0){
					token = strtok(line, " ");
					if(strcmp(token, request_key) == 0){
						printf("Key found in file!!\n");
						response_value = strtok(NULL, " ");
						response_value = strtok(response_value, "\n");
      			strcpy(pending_head->cont->result, response_value);
						printf("Response for GET %s is %s\n",request_key, response_value);
						break;
					}
				}
      }
			else { //PUT Request - assuming a maximum key value pair size. else data will be overwritten
				while((retval = getline(&line, &len, myFile)) > 0){
					token = strtok(line, " ");
					if(strcmp(token, request_key) == 0){
						printf("Key found in file!!\n");
						strcpy(request, request_key);
						strcat(request, " ");
						strcat(request, request_value);
						printf("Writing %s to file\n", request);
						fseek(myFile, -retval, SEEK_CUR);
						if(fputs(request, myFile)<=0)
							printf("Error while writing to file\n");
						for (i = strlen(request); i < retval-2; i++) //cleaning up the old data
							fputs(" ", myFile);
						strcpy(pending_head->cont->result, "ACK");
						break;
					}
				}
			}
      v = (union sigval*) malloc (sizeof(union sigval));
      v->sival_ptr = pending_head->cont;
      sigqueue(my_pid, SIGRTMIN+4, *v);
      pending_head = pending_head->next;
			fclose(myFile);
    }
  }
}

static void incoming_connection_handler(int sig, siginfo_t *si, void *data) {

	struct sockaddr_in in;
	socklen_t sz = sizeof(in);
	int incoming = accept(si->si_fd, (struct sockaddr*)&in, &sz);

	char ip[INET_ADDRSTRLEN];
	inet_ntop(AF_INET, &(in.sin_addr), ip, INET_ADDRSTRLEN);
	printf("Connected to client: %s with fd: %d\n",ip, incoming);

	int fl = fcntl(incoming, F_GETFL);
	fl |= O_ASYNC|O_NONBLOCK;     /* want a signal on fd ready */
	fcntl(incoming, F_SETFL, fl);
	fcntl(incoming, F_SETSIG, SIGRTMIN + 3);
	fcntl(incoming, F_SETOWN, getpid());

	sock_event[incoming] = 1;
}

static void incoming_request_handler(int sig, siginfo_t *si, void *data) {
	sock_event[si->si_fd] = 1;
}

static void process_signal(int incoming) {
  int valread;
  char *request_string, *request_key, *request_value, *tokens;
  char *temp_string;

	printf("Processing signal from fd %d\n", incoming); 

  temp_string = (char *) malloc (1024 * sizeof(char));
	valread = read( incoming , temp_string, 1024);
  if(valread > 0){

    temp = (struct continuation*) malloc (sizeof (struct continuation));
    memset(temp->buffer, 0, 1024);
    temp_string = strtok(temp_string, "\n");
    strcpy (temp->buffer, temp_string);

    tokens = strtok(temp_string, " ");
		//printf(tokens);

    if (strcmp(tokens, "GET") == 0) {
      temp->request_type = 0;
			printf("received a GET request.\n");
    } else {
      temp->request_type = 1;
			printf("received a PUT request.\n");
    }

    memset(temp->result, 0, 1024);
    temp->fd = incoming;

    // Servicing the request
    if (temp->request_type == 0) {

      // This is a GET request, check the cache first
      tokens = strtok(NULL, " ");
      temp_node = get(tokens);
      if (temp_node != NULL) {

        // Result found in cache
        printf("\nResult found in cache\n\n");
        strcpy(temp->result, temp_node->defn);
        send(temp->fd ,temp->result , strlen(temp->result) , 0);
      } else {

        // Not found in cache, issue request to I/O
        pending_node = (struct pending_queue*) malloc (sizeof(struct pending_queue));
        pending_node->cont = temp;
        pending_node->next = NULL;
        if (pending_head == NULL) {
          pending_head = pending_tail = pending_node;
        } else {
          pending_tail->next = pending_node;
          pending_tail = pending_node;
        }
      }
    } else if (temp->request_type == 1) {

      // This is a PUT request, complete the function
      // to service the request.

      pending_node = (struct pending_queue*) malloc (sizeof(struct pending_queue));
      pending_node->cont = temp;
      pending_node->next = NULL;
      if (pending_head == NULL) {
        pending_head = pending_tail = pending_node;
      } else {
        pending_tail->next = pending_node;
        pending_tail = pending_node;
      }
    }
	}
	else if(valread == 0){
		printf("Shutting socket with fd: %d\n",incoming);
		close(incoming);
	}
	else{
		printf("Irrelevant signal on socket with fd: %d\n", incoming);
	}
	free(temp_string);
}

static void outgoing_response_handler(int sig, siginfo_t *si, void *data) {
  // Function to be completed.

  struct continuation *temp_cont_to_send = (struct continuation*)si->si_value.sival_ptr;
  send(temp_cont_to_send->fd, temp_cont_to_send->result, strlen(temp_cont_to_send->result), 0);
  free(temp_cont_to_send);
}


int init_server_sock() {
  int server_fd;
  addrlen = sizeof(address);

  // Creating socket file descriptor
  if ((server_fd = socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK, 0)) == 0) {
      perror("socket failed");
      exit(EXIT_FAILURE);
  }

  // Forcefully attaching socket to the port 8080
  if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT,
                                                &opt, sizeof(opt))) {
    perror("setsockopt");
    exit(EXIT_FAILURE);
  }
  address.sin_family = AF_INET;
  address.sin_addr.s_addr = INADDR_ANY;
  address.sin_port = htons( PORT );

  // Forcefully attaching socket to the port 8080
  if (bind(server_fd, (struct sockaddr *)&address,
                               sizeof(address))<0) {
    perror("bind failed");
    exit(EXIT_FAILURE);
  }

	int fl = fcntl(server_fd, F_GETFL);
	fl |= O_ASYNC|O_NONBLOCK;     /* want a signal on fd ready */
	fcntl(server_fd, F_SETFL, fl);
	fcntl(server_fd, F_SETSIG, SIGRTMIN + 2);
	fcntl(server_fd, F_SETOWN, getpid());
	
	if (listen(server_fd, 5000) < 0) {
		perror("listen");
		exit(EXIT_FAILURE);
	}

  return server_fd;
}

void event_loop_scheduler() {
	int i;
	server_fd = init_server_sock();

  while (1) {
		for(i = 0; i < MAX_CLIENTS+3; i++){
			if(sock_event[i] == 1){
				printf("Signal was raised by socket with fd: %d\n", i);
				sock_event[i] = 0;
				process_signal(i);
			}
			else{
				//printf("No events!\n");
			}
		}
		sleep(1);
  }
}

void issue_IO_request(struct continuation *cref) {

	if(write(request_pipe_fd, cref, sizeof(continuation) == -1)
		printf("Sending request through pipe failed!\n");
	
}

int main (void)
{
  struct sigaction listen, act, react;
  my_pid = getpid();

  pending_head = pending_tail = NULL;
  cache_head = cache_tail = curr = temp_node = NULL;

	pipe(request_pipe_fd);
	pipe(response_pipe_fd);

  listen.sa_sigaction = incoming_connection_handler;
  sigemptyset(&listen.sa_mask);
  listen.sa_flags = SA_SIGINFO;
  sigaction(SIGRTMIN + 2, &listen, NULL);

  act.sa_sigaction = incoming_request_handler;
  sigemptyset(&act.sa_mask);
  act.sa_flags = SA_SIGINFO;
  sigaction(SIGRTMIN + 3, &act, NULL);

  react.sa_sigaction = outgoing_response_handler;
  sigemptyset(&react.sa_mask);
  react.sa_flags = SA_SIGINFO;
  sigaction(SIGRTMIN + 4, &react, NULL);

	printf("Spawning threads!\n");

  //Creating I/O thread pool
  for (int i = 0; i < THREAD_POOL_SIZE; i++) {
    pthread_create(&io_thread[i], NULL, io_thread_func, NULL);
  }

	printf("Threads spawned successfully!\n");

  event_loop_scheduler();

  return 0;
}
