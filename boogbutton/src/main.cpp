#include "Esp32Button.h"

#include <cstring>
#include <iostream>
#include <string>
#include <cstdio>

#include <arpa/inet.h>
#include <netdb.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

Esp32Button::DualActionButton button(35, true);
constexpr const char* serverIP = "127.0.0.1";
constexpr const int serverPort = 54045;
constexpr const char* payload = "letsrock";

bool state(false);

void setup();
void loop();
int lets_rock();
int main();

enum boog_err
{
    sock_failed = 1,
    invalid_addr,
    connect_failed,
};

void setup()
{
    button.set_debounce_duration_ms(250);
    button.set_trigger(&state);
}

void loop()
{
    if (button.read())
    {
        int rc = lets_rock();
        printf("rc: %d\n", rc);
        // button.toggle();
    }

}

int lets_rock()
{
    struct sockaddr_in serv; 

    int sock = 0;
   
    serv.sin_family = AF_INET;
    serv.sin_port = htons(serverPort); 

    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) return sock_failed;
    if (inet_pton(AF_INET, serverIP, &serv.sin_addr) <= 0) return invalid_addr;
    if (connect(sock, (struct sockaddr*)&serv, sizeof(serv)) < 0) return connect_failed;

    /* Start the party */
    send(sock, payload, sizeof(payload), 0);

    /* Don't forget to clean up */
    close(sock);

    return 0;
}

int main()
{
    setup();
    while (true)
    {
        loop();
    }
    return 0;
}
