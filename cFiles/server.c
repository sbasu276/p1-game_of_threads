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

void put(char *name, char *defn) {
	printf("Inserting %s %s to the cache\n", name, defn);
	int ret;
  struct node *cache_entry;
  if ((cache_entry = get(name)) == NULL) {
    // value not in cache
    temp_node = (struct node*) malloc (sizeof(struct node));
    temp_node->name = strdups(name);
    temp_node->defn = strdups(defn);
		temp_node->myState = Dirty;
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
			if(cache_tail->myState == Dirty){
		    temp = (struct continuation*) malloc (sizeof (struct continuation));
		    memset(temp->name, 0, 1024);
		    memset(temp->defn, 0, 1024);
		    temp->request_type = PUT;
				strcat(temp->name, cache_tail->name);
				strcat(temp->defn, cache_tail->defn);
				temp->file_op_type = 1;	//Writing to file
				temp->sock_fd = -1;	//No clients to respond to
				printf("Inserting %s %s to the cache\n", temp->name, temp->defn);

				while((ret = write(request_pipe_fd[1], temp, sizeof(struct continuation))) <= 0)
					printf("Trying to end data to pipe, write returns %d \n",ret);
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
		cache_entry->myState	= Dirty;
  }
}

void *io_thread_func() {
  // This function should handle incoming I/O requests,
  // once the request is processed, the thread notifies
  // the event schuduler using a signal

	int retval, written, i, ret;
	size_t len;
	char *token, *request_key, *request_value, *response_value;
	char request[1024];
	FILE* myFile;
	struct continuation req, *cont_req;

	cont_req = &req;
  while(1) {
    if ((ret = read(request_pipe_fd[0], cont_req, sizeof(struct continuation))) > 0) {
			printf("HT %ld: Received a request\n",pthread_self());
	    if((myFile = fopen("names.txt", "rb+")) == NULL){
				printf("HT: Unable to open file\n");
				exit(0);
			}

			char* line = malloc (MAX_KEY_VALUE_SIZE);
			request_key		= cont_req->name;
			request_value	= cont_req->defn;
			printf("HT: Working on %d %s request\n", cont_req->file_op_type, request_key);

			len = MAX_KEY_VALUE_SIZE;
			rewind(myFile);

      if (cont_req->file_op_type == 0) { //GET Op
				while((retval = getline(&line, &len, myFile)) > 0){
					token = strtok(line, " ");
					if(strcmp(token, request_key) == 0){
						printf("HT: Key found in file!!\n");
						response_value = strtok(NULL, " ");
						response_value = strtok(response_value, "\n");
						if(cont_req->request_type == GET)
	      			strcpy(cont_req->defn, response_value);
						cont_req->key_found = 1;
						printf("HT: Response for GET %s is %s\n",request_key, response_value);
						break;
					}
				}
      }
			else { //PUT Request - assuming a maximum key value pair size. else data will be overwritten
				while((retval = getline(&line, &len, myFile)) > 0){
					token = strtok(line, " ");
					if(strcmp(token, request_key) == 0){
						printf("HT: Key found in file!!\n");
						cont_req->key_found = 1;
						strcpy(request, request_key);
						printf("HT: CHECKPOINT\n");
						strcat(request, " ");
						strcat(request, request_value);
						printf("HT: Writing %s to file\n", request);
						fseek(myFile, -retval, SEEK_CUR);
						if(fputs(request, myFile)<=0)
							printf("HT: Error while writing to file\n");
						for (i = strlen(request); i < retval-2; i++) //cleaning up the old data
							fputs(" ", myFile);
						break;
					}
				}
			}

			if(write(response_pipe_fd[1], cont_req, sizeof(struct continuation)) < 0)
				printf("HT: Write to pipe failed!\n");

			//TODO: Cleanup
      v = (union sigval*) malloc (sizeof(union sigval));
      v->sival_ptr = NULL;
      sigqueue(my_pid, SIGRTMIN+4, *v);
			fclose(myFile);
    }
//		if (ret == -1)
//			printf("Pipe read returned an error = %s\n", strerror(errno)); TODO: why -1?
//		else
//			printf("HT %ld: Didn't find anything to work on!\n", pthread_self());
		sleep(1);
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
	printf("ISH: Setting the bit for fd %d\n",si->si_fd);
}

static void process_signal(int incoming) {
  int valread, ret;
  char *request_string, *request_key, *request_value, *tokens;
  char *temp_string;
  temp_string = (char *) malloc (1024 * sizeof(char));

  memset(temp_string, 0, 1024);
	printf("Processing signal from fd %d\n", incoming); 
	valread = read(incoming , temp_string, 1024);
  if(valread > 0){
    temp = (struct continuation*) malloc (sizeof (struct continuation));
    memset(temp->name, 0, 1024);
    memset(temp->defn, 0, 1024);

    temp_string = strtok(temp_string, "\n");
    tokens = strtok(temp_string, " ");
    strcpy(temp->name, strtok(NULL, " "));
    temp->sock_fd = incoming;

    if (strcmp(tokens, "GET") == 0) {
      temp->request_type = GET;
			printf("received a GET request for key %s\n", temp->name);
    } else {
      temp->request_type = PUT;
    	strcpy(temp->defn, strtok(NULL, " "));
			printf("received a PUT request for key %s\n", temp->name);
    }

    // Servicing the request
    if (temp->request_type == GET) {
      // This is a GET request, check the cache first
      temp_node = get(temp->name);
      if (temp_node != NULL) {
        // Result found in cache
        printf("Key found in cache\n");
        strcpy(temp->defn, temp_node->defn);
        send(temp->sock_fd ,temp->defn , strlen(temp->defn) , 0);
      } else {
				printf("Key missed in cache\n");
	      // Not found in cache, issue request to I/O
				temp->file_op_type = GET;
				while((ret = write(request_pipe_fd[1], temp, sizeof(struct continuation))) <= 0)
					printf("Trying to end data to pipe, write returns %d \n",ret);
			}
    } else if (temp->request_type == PUT) {
      temp_node = get(temp->name);
      if (temp_node != NULL) { //Key found in cache
				printf("Key found in cache\n");
				strcpy(temp_node->defn, temp->defn);
				temp_node->myState = Dirty;
        send(temp->sock_fd, "ACK" , 3 , 0);
			}
			else{
				printf("Key missed in cache\n");
				temp->file_op_type = GET;
				printf("Size of continuation structure = %ld\n", sizeof(struct continuation));
				while((ret = write(request_pipe_fd[1], temp, sizeof(struct continuation))) <= 0)
					printf("Trying to end data to pipe, write returns %d \n",ret);
			}
    }
		free(temp);
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

static void incoming_response_handler(int sig, siginfo_t *si, void *data) {
	response_count++;
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
	int i, ret;
	struct continuation *resp, my_resp;
	server_fd = init_server_sock();
	resp = &my_resp;

  while (1) {
		//Stage1: Processing incoming requests
		for(i = 0; i < MAX_CLIENTS+3; i++){
			if(sock_event[i] == 1){
				printf("Signal was raised by socket with fd: %d\n", i);
				sock_event[i] = 0;
				process_signal(i);
			}
			else{
//				printf("No event for fd %d!\n", i);
			}
		}

		//Stage2: Processing the responses from threads
		int num_resp = response_count;
		response_count = 0;
		//printf("Stage2: Number of responses received %d\n", num_resp);
		for(i = 0; i < num_resp; i++){
			if((ret = read(response_pipe_fd[0], resp, sizeof(struct continuation))) > 0){
				if(resp->file_op_type == 0){//Read operation
					if(resp->request_type == GET){//GET Request
						if(resp->key_found == 1){
							put(resp->name, resp->defn);
							send(resp->sock_fd, resp->defn, strlen(resp->defn), 0);
						}
						else{
							send(resp->sock_fd, "-1", 2, 0);
						}
					}
					else{//PUT Request
						if(resp->key_found == 1){
							printf("Key found for  PUT operation\n");
							send(resp->sock_fd, "ACK", 3, 0);
							put(resp->name, resp->defn);							
						}
						else
							send(resp->sock_fd, "-1", 2, 0);
					}
				}
				else {//Write Operation
					printf("Op for fd %d completed\n", resp->sock_fd);
					if(resp->sock_fd == -1)
						printf("Write back of %s %s completed\n", resp->name, resp->defn);
					else
						send(resp->sock_fd, "ACK", 3, 0);
				}
			}
			printf("Response pipe read return value %d\n", ret);
		}
		sleep(1);
  }
}

int main (void)
{
  struct sigaction listen, act, react;
  my_pid = getpid();

  cache_head = cache_tail = curr = temp_node = NULL;

	pipe(request_pipe_fd);
	pipe(response_pipe_fd);

	fcntl(request_pipe_fd[0], F_SETFL, O_NONBLOCK);
	fcntl(response_pipe_fd[1], F_SETFL, O_NONBLOCK);

  listen.sa_sigaction = incoming_connection_handler;
  sigemptyset(&listen.sa_mask);
  listen.sa_flags = SA_SIGINFO;
  sigaction(SIGRTMIN + 2, &listen, NULL);

  act.sa_sigaction = incoming_request_handler;
  sigemptyset(&act.sa_mask);
  act.sa_flags = SA_SIGINFO;
  sigaction(SIGRTMIN + 3, &act, NULL);

  react.sa_sigaction = incoming_response_handler;
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
