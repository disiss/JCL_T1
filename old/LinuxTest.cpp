#define _WINSOCK_DEPRECATED_NO_WARNINGS
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <thread>
#include <set>
#include <vector>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <list>
#include <string.h>
#include <algorithm>

#pragma comment (lib, "ws2_32.lib")

//char support_socks_version = 0x05;
//char support_auth_method = 0x01; // 0x00 without auth

void exchange_loop(int client, int remote) {
    while (true) {
        fd_set readfds;
        FD_ZERO(&readfds);
        FD_SET(client, &readfds);
        FD_SET(remote, &readfds);

        int max_fd = std::max(client, remote) + 1;
        int result = select(max_fd, &readfds, nullptr, nullptr, nullptr);
        if (result == -1) {
            std::cerr << "Error in select" << std::endl;
            break;
        }

        if (FD_ISSET(client, &readfds)) {
            char data[4096];
            ssize_t num_bytes = recv(client, data, sizeof(data), 0);
            if (num_bytes <= 0) {
                break;
            }
            if (send(remote, data, num_bytes, 0) <= 0) {
                break;
            }
        }

        if (FD_ISSET(remote, &readfds)) {
            char data[4096];
            ssize_t num_bytes = recv(remote, data, sizeof(data), 0);
            if (num_bytes <= 0) {
                break;
            }
            if (send(client, data, num_bytes, 0) <= 0) {
                break;
            }
        }
    }
}

bool CheckAuth(int clientSocket, std::string client_ip, char* buf)
{
    int bytesReceived;

    bytesReceived = recv(clientSocket, buf, 1, 0);
    int version = buf[0];

    std::cout << client_ip << ": buf " << (int)buf[0] << " bytesReceived " << bytesReceived << std::endl;

    if (version != 1) { //if bytesReceived != 1 connection is unestablish 
        shutdown(clientSocket, SHUT_RDWR);
        return false;
    }

    bytesReceived = recv(clientSocket, buf, 1, 0);
    std::cout << " - " << client_ip << ": buf " << (int)buf[0] << " bytesReceived " << bytesReceived << std::endl;
    int username_len = buf[0];

    bytesReceived = recv(clientSocket, buf, username_len, 0);
    std::cout << "buf: " << buf << std::endl;
    
    std::cout << "buf: " << strcmp(buf, "username") << std::endl;
    std::cout << "buf: " << strcmp(buf, "uusssername") << std::endl;
    if (strcmp(buf, "username") != 0)
    {
        std::cout << "Username is FALIED" << std::endl;
        return false;
    }

    std::cout << "Username is PASSED" << std::endl;

    bytesReceived = recv(clientSocket, buf, 1, 0);
    std::cout << " - " << client_ip << ": buf " << (int)buf[0] << " bytesReceived " << bytesReceived << std::endl;
    int password_len = buf[0];

    bytesReceived = recv(clientSocket, buf, password_len, 0);
    std::cout << "buf: " << buf << std::endl;
    
    if (strcmp(buf, "password") != 0)
    {
        std::cout << "Password is FALIED" << std::endl;
        return false;
    }

    std::cout << "Password is PASSED" << std::endl;
    std::cout << "All auths is PASSED" << std::endl;

    return true;

    /*
    if ((strcmp(username, "username") == 1) && (strcmp(password, "password") == 1)) //если не нашли пароль в char
    {
        std::cout << "Username and Password PASSED" << std::endl;
        char answer[] = { version, 0 };
        send(clientSocket, answer, sizeof(answer), 0); //отправка статуса аута клиенту
        return true;
    }
    else {
        std::cout << "Auth Failure!" << std::endl;
        char answer[] = { version, 0xFF };
        send(clientSocket, answer, sizeof(answer), 0); //отправка статуса аута клиенту
        return false;
    }*/
}

std::list<int> getAvailableMethods(int clientSocket, std::string client_ip, int nmethods, char* buf)
{
    std::list<int> available_methods = {};
    int bytesReceived;

    for (int i = 1; i <= nmethods; ++i)
    {
        bytesReceived = recv(clientSocket, buf, 1, 0);

        available_methods.push_back((int)buf[0]);

        std::cout << client_ip << ": recv socks availables methods " << (int)buf[0] << " bytesReceived " << bytesReceived << std::endl;
    }

    return available_methods;
}

void clientSocketHandler(int clientSocket, std::string client_ip)
{
    char buf[4096];

    std::thread::id thread_id = std::this_thread::get_id();
    std::cout << thread_id << " - " << client_ip << ": connected" << std::endl;

    int bytesReceived = recv(clientSocket, buf, 2, 0);

    std::cout << thread_id << " - " << client_ip << ": recv socks client version " << (int)buf[0] << " bytesReceived " << bytesReceived << std::endl;

    char version = buf[0];
    char nmethods = buf[1];

    // Проверка на версию протокола и поддерживаемые методы
    if (version != '\x05') {
        std::cout << thread_id << " - " << client_ip << ": bad socks client version! " << buf[0] << std::endl;
        shutdown(clientSocket, SHUT_RDWR);
        return;
    }

    std::list<int> methods = getAvailableMethods(clientSocket, client_ip, nmethods, buf);
    std::cout << "methods " << std::endl;
    for (int n : methods)
    {
        std::cout << n << "\t";
    }
    std::cout << std::endl;

    if (std::find(methods.begin(), methods.end(), 2) == methods.end()) //проверка метода аутенфикации, должно быть 2(username, password)
    {
        std::cout << thread_id << " - " << client_ip << ": bad socks client auth versions! " << std::endl;
        shutdown(clientSocket, SHUT_RDWR);
        return;
    }

    // Отправка сообщения о поддерживаемых методах (с аутентификацией '0x02' login и password)
    char answer[] = {0x05, 0x02};
    std::cout << "sizeof answer " << sizeof(answer) << std::endl;
    
    send(clientSocket, answer, sizeof(answer), 0); //отправка приветственного сообщения клиенту

    bool status = CheckAuth(clientSocket, client_ip, buf);
    if (status != true)
    {
        answer[0] = version;
        answer[1] = 0xFF; //failure

        send(clientSocket, answer, sizeof(answer), 0); //отправка статуса аута клиенту
        shutdown(clientSocket, SHUT_RDWR);
        return;
    }

    answer[0] = version;
    answer[1] = 0; //succ

    send(clientSocket, answer, sizeof(answer), 0); //отправка статуса аута клиенту

    bytesReceived = recv(clientSocket, buf, 4, 0);
    std::cout << "buf " << int(buf[4]) << std::endl;
    int socksClientVersion = buf[0];
    int socksCmd = buf[1];
    int socksReservedByte = buf[2];
    int addressType = buf[2];

    //buf[0] - socks client version
    //buf[1] - socks cmd (0x01 - установка TCP/IP соединения; 0x02 - назначение TCP/IP порта (binding); 0x03 - ассоциирование UDP-порта)
    //buf[2] - socks reserved byte, must be 0x00(int - 0)
    //buf[3] - address type (0x01 - IPv4; 0x03 - domain; 0x04 - IPv6)

    char remote_ip[INET_ADDRSTRLEN];
    if (buf[3] == 0x01)
    {
        std::cout << "IPv4 " << std::endl;
        bytesReceived = recv(clientSocket, buf, 4, 0);
        std::cout << "buf " << buf << std::endl;

        inet_ntop(AF_INET, (void*)(&buf), remote_ip, sizeof(remote_ip));
        std::cout << "IPv4: " << remote_ip << "\n";
    }

    bytesReceived = recv(clientSocket, buf, 2, 0);
    unsigned char first_Ubuf_byte = (unsigned char)buf[0];
    unsigned char second_Ubuf_byte = (unsigned char)buf[1];
    unsigned int port = (first_Ubuf_byte << 8) | second_Ubuf_byte;

    std::cout << "port " << port << std::endl;
    std::cout << "socksClientVersion " << socksClientVersion << std::endl;
    std::cout << "socksCmd " << socksCmd << std::endl;
    std::cout << "socksReservedByte " << socksReservedByte << std::endl;
    std::cout << "addressType " << addressType << std::endl;

    if (socksCmd == 0x01)
    {
        std::cout << "trying to Connect: " << remote_ip << std::endl;

        struct sockaddr_in addr;
        int addrLen = sizeof(addr);

        addr.sin_addr.s_addr = inet_addr(remote_ip);
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port);

        int remote = socket(AF_INET, SOCK_STREAM, 0);
        if (connect(remote, (struct sockaddr *)&addr, addrLen) == 0) {
            std::cout << "Connected! to: " << remote_ip << std::endl;

            char myIP[16]; //myIP text
            wchar_t pcwstrMyIP[16]; //myIP wchar_t

            struct sockaddr_in bindAddress;
            socklen_t bindAddressLength = sizeof(bindAddress);

            getsockname(remote, (struct sockaddr*)&bindAddress, &bindAddressLength);

            std::string bindAddressStr = inet_ntoa(bindAddress.sin_addr);
            std::cout << "bind_address " << bindAddressStr << std::endl;

            uint32_t addr = ntohl(inet_addr(bindAddressStr.c_str()));
            uint16_t bindPort = ntohs(bindAddress.sin_port);
            
            std::cout << "addr " << addr << std::endl;
            std::cout << "port " << bindPort << std::endl;
            
            char AddrrBytes[] = {
                (addr >> 24) & 0xFF,
                (addr >> 16) & 0xFF,
                (addr >> 8) & 0xFF,
                addr & 0xFF
            };

            std::cout << "AddrrBytes " << AddrrBytes << std::endl;

            char PortBytes[] = {
                (bindPort >> 8) & 0xFF,
                bindPort & 0xFF
            };
            
            std::cout << "PortBytes " << PortBytes << std::endl;

            
            char reply[] = {
                5,
                0,
                0,
                1,
                (addr >> 24) & 0xFF,
                (addr >> 16) & 0xFF,
                (addr >> 8) & 0xFF,
                addr & 0xFF,
                (bindPort >> 8) & 0xFF,
                bindPort & 0xFF
            };

            send(clientSocket, reply, sizeof(reply), 0); //отправка ответа клиенту
            exchange_loop(clientSocket, remote);
        }
    }

    shutdown(clientSocket, SHUT_RDWR);
    return;

    /*
    while (true)
    {

        if (bytesReceived == 0)
        {

            std::cout << thread_id << " - " << client_ip << ": disconnected" << std::endl;

            break;

        }

        if (bytesReceived > 0)
        {

            std::cout << thread_id << " - " << client_ip << ": " << std::string(buf, 0, bytesReceived) << std::endl;

            send(clientSocket, buf, bytesReceived + 1, 0);

        }

    }
    */

    std::cout << thread_id << " - " << client_ip << ": closing client socket & exiting thread..." << std::endl;

    shutdown(clientSocket, SHUT_RDWR);

}

void waitForConnections(int serverSocket)
{

    unsigned int port = 1338;
    char host[] = {"127.0.0.1"};

    struct sockaddr_in address;
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = inet_addr(host);
    address.sin_port = htons(port);

    bind(serverSocket, (struct sockaddr *)&address, sizeof(address));
    listen(serverSocket, 5);
    std::cout << "* Socks5 proxy server is running on " << ":" << port << std::endl;

    while (true) {
        int clientSocket;
        struct sockaddr_in client_address;
        socklen_t client_address_len = sizeof(client_address);

        clientSocket = accept(serverSocket, (struct sockaddr*)&client_address, &client_address_len);
        
        std::string client_ip = inet_ntoa(client_address.sin_addr);
        std::cout << "* new connection from " << client_ip << std::endl;

        std::thread t(clientSocketHandler, clientSocket, client_ip);
        t.detach();
    }

}

int main()
{
    unsigned char bytes[] = { 0x01, 0xbb };
    int result = (bytes[0] << 8) | bytes[1];
    std::cout << int(bytes[1]) << std::endl;

    int resultt = 256 | 187;
    std::cout << resultt << std::endl;

    char a[] = { '\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07', '\x08' };
    std::cout << a;

    // Create a socket
    int serverSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (serverSocket < 0)
    {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    std::cout << "curl -x socks5://username:password@127.0.0.1:1337 https://httpbin.org/get";

    // Start listening for connections
    waitForConnections(serverSocket);

    system("pause");

    return 0;
}