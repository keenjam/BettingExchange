#include <iostream>
#include <sys/types.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <string.h>
#include <string>
#include <unordered_map>
#include <chrono>
#include <stdexcept>

#define PORT 55000
#define VERSION 1
#define MAX_CLIENTS 20

using namespace std;


int main(int argc, char**argv) {
  cout << "SETTING UP EXCHANGE..." << endl;
  int masterSocket, addrlen, newSocket, clientSocket[MAX_CLIENTS], activity, i, valread, sd;
  int max_sd;

  uint8_t buffer[1025];

  fd_set readfds;

  // Initialise all client sockets to 0 so not checked
  for(int i = 0; i < MAX_CLIENTS; i++) {
    clientSocket[i] = 0;
  }

  // Create a master socket
  if((masterSocket = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
     cout << "Socket creation failed..." << endl;
     return -1;
  }

  sockaddr_in address;
  address.sin_family = AF_INET;
  address.sin_addr.s_addr = INADDR_ANY;
  address.sin_port = htons(PORT);

  // Bind socket to port
  if(bind(masterSocket, (sockaddr*)&address, sizeof(address)) == -1)  {
    cout << "Socket binding failed..." << endl;
    return -1;
  }
  else cout << "Socket binded successfully..." << endl;

  // Maximum pending connections should not be more than 3
  if(listen(masterSocket, 3) < 0) {
    cout << "Listening failure..." << endl;
  }

  // Accept incoming connection
  addrlen = sizeof(address);
  cout << "Waiting for connections..." << endl;

  while(true) {
    // Clear socket set
    FD_ZERO(&readfds);

    // Add master socket to set
    FD_SET(masterSocket, &readfds);
    max_sd = masterSocket;

    // Add child sockets to set
    for(int i = 0; i < MAX_CLIENTS; i++) {
      // Socket descriptor
      sd = clientSocket[i];

      // If valid socket descriptor then add to read list
      if(sd > 0) FD_SET(sd, &readfds);

      // Update highest file descriptor number
      if(sd > max_sd) max_sd = sd;
    }

    // Wait for activity on one of sockets
    activity = select(max_sd + 1, &readfds, NULL, NULL, NULL);

    if(FD_ISSET(masterSocket, &readfds)) {
      if((newSocket = accept(masterSocket, (sockaddr*)&address, (socklen_t*)&addrlen)) < 0) {
        cout << "Accept failure..." << endl;
        return -1;
      }

      cout << "New connection, socket fd is " << newSocket << " with address " << inet_ntoa(address.sin_addr) << endl;

      // Add new socket to array of sockets
      for(int i = 0; i < MAX_CLIENTS; i++) {
        // If position is empty
        if(clientSocket[i] == 0) {
          clientSocket[i] = newSocket;
          cout << "Adding to sockets as: " << i << endl;
          break;
        }
      }

    }

    // Perform computation from socket
    for(int i = 0; i < MAX_CLIENTS; i++) {
      sd = clientSocket[i];
      if(FD_ISSET(sd, &readfds)) {
        // Check if received value was a disconnect
        valread = read(sd, buffer, 1024);

        if(valread == 0) {
          cout << "Client Disconnected" << endl;
          getpeername(sd, (sockaddr*)&address, (socklen_t*)&addrlen);
          close(sd);
          clientSocket[i] = 0;
        }

        else {
          buffer[valread] = '\0';
          // perform computation
          for(auto n : buffer) {
            if(n == '\0') break;
            cout << n;
          }
          cout << endl;

          // Everytime there is new LOB activity, inform all others of new LOB state
          // waiting for confirmation each time
        }
      }
    }

    cout << "RACE PROGRESSION" << endl;
    // Update race state
    // Inform all agents, waiting for confirmation that they have finshed updating internal variables each time

  }

  return 0;
}
