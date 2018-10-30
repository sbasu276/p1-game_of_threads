#include <stdio.h>
#include <sys/socket.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <pthread.h>
#define PORT 8080

char *first[] = {"PUT Aman Jain\n"};
char *sec[] = {"GET Roger\n"};
char *third[] = {"GET Aman\n"};
char *fourth[] = {"PUT Aman Patra\n"};
struct sockaddr_in *serv_addr;

void *client_func() {
  int sock = 0, valread, i;

  char buffer[1024] = {0};
  char buffer1[1024] = {0};
  char buffer2[1024] = {0};
  char buffer3[1024] = {0};

  if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
  {
      printf("\n Socket creation error \n");
      exit(0);
  }

  if (connect(sock, (struct sockaddr *)serv_addr, sizeof(struct sockaddr_in)) < 0)
  {
      printf("\nConnection Failed \n");
      exit(0);
  }

	for(i = 0; i < 100; i++){
	  send(sock , first[0] , strlen(first[0]) , 0 );
  	printf("REQUEST SENT: %s", first[0]);
	  valread = read( sock , buffer, 1024);
  	printf("RESPONSE: %s\n",buffer );
	  send(sock , sec[0] , strlen(sec[0]) , 0 );
  	printf("REQUEST SENT: %s", sec[0]);
	  valread = read( sock , buffer1, 1024);
  	printf("RESPONSE: %s\n",buffer1);
	  send(sock , third[0] , strlen(third[0]) , 0 );
  	printf("REQUEST SENT: %s", third[0]);
	  valread = read( sock , buffer2, 1024);
  	printf("RESPONSE: %s\n",buffer2);
	  send(sock , fourth[0] , strlen(fourth[0]) , 0 );
  	printf("REQUEST SENT: %s", fourth[0]);
	  valread = read( sock , buffer3, 1024);
  	printf("RESPONSE: %s\n",buffer3);
	}

}

int main(int argc, char const *argv[])
{
    pthread_t client_thread;

    serv_addr = (struct sockaddr_in*) malloc (sizeof(struct sockaddr_in));

    memset(serv_addr, '0', sizeof(serv_addr));

    serv_addr->sin_family = AF_INET;
    serv_addr->sin_port = htons(PORT);

    // Convert IPv4 and IPv6 addresses from text to binary form
    if(inet_pton(AF_INET, "127.0.0.1", &serv_addr->sin_addr)<=0)
    {
        printf("\nInvalid address/ Address not supported \n");
        return -1;
    }

    pthread_create(&client_thread, NULL, client_func, NULL);

    pthread_join(client_thread, NULL);

    return 0;
}
