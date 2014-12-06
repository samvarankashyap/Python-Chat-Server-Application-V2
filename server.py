# chat_server.py
import sys
import socket
import select
from user import User
import pdb

HOST = '' 
SOCKET_LIST = []
RECV_BUFFER = 4096 
PORT = 9009
USER_LIST = []

OPTIONS="The Commands list are : \n1.login\n2.list\n3.sendto\n4.help\n5.exit\n"

def chat_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
 
    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)
 
    print "Chat server started on port " + str(PORT)
 
    while 1:

        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0 : poll and never block
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)
        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket: 
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
                print "Client (%s, %s) connected" % addr
                #broadcast(server_socket, sockfd, "[%s:%s] entered our chatting room\n" % addr)
             
            # a message from a client, not a new connection
            else:
                # process data recieved from client, 
                try:
                    # receiving data from the socket.
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        # there is something in the socket
                        print data
                        process_command(server_socket,data,sock)
                        #broadcast(server_socket, sock, "\r" + '[' + str(sock.getpeername()) + '] ' + data)  
                    else:
                        # remove the socket that's broken    
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)

                        # at this stage, no data means probably the connection has been broken
                        #broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr)
                        process_command(server_socket,"removeuser",sock)

                # exception 
                except:
                    broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr)
                    process_command(server_socket,"removeuser",sock)
                    continue

    server_socket.close()
    
# broadcast chat messages to all connected clients
def broadcast (server_socket, sock, message):
    #pdb.set_trace()
    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except :
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)

def unicast_reply(sock,message):
    try :
        sock.send(message)
    except :
        # broken socket connection
        sock.close()
        # broken socket, remove it

def get_socket_by_name(name):
    for obj in USER_LIST:
        if obj.user_name == name:
            return obj.socket

def get_name_by_socket(socket):
    for obj in USER_LIST:
        if obj.socket == socket:
            return obj.user_name

def is_user_exists(name):
    for obj in USER_LIST:
        if obj.user_name == name:
            return True
    return False


def process_command(server_sock,data,sock):
    #pdb.set_trace()
    if "login" in data:
        msg = register_user(data,sock)
        unicast_reply(sock,msg)
    if "removeuser" in data:
        deregister_user(data,sock)
    if "list" in data:
        msg = list_users(data)
        unicast_reply(sock,msg)
    if "sendto" in data:
        send_message(data,sock)
    if "help" in data:
        unicast_reply(sock,OPTIONS)

def send_message(data,sender_sock):
    data = data.split(" ")
    msg = data[2:]
    msg = " ".join(msg)
    sender_name = get_name_by_socket(sender_sock)
    msg = sender_name+":"+msg 
    reciver_sock = get_socket_by_name(data[1])
    unicast_reply(reciver_sock,msg)

def register_user(data,sock):
    user_name = data.split(" ")[1].strip("\n")
    if not is_user_exists(user_name):
        user_obj = User(user_name, sock)
        USER_LIST.append(user_obj)
        return "User Added Successfully\n"
    return "User Already exists please select another username\n"
    
def deregister_user(data,sock):
    for user in USER_LIST:
        if user.socket == sock:
            USER_LIST.remove(user)

def list_users(data):
    users = ""
    for obj in USER_LIST:
        users += obj.user_name +"\n" 
    return users
  
if __name__ == "__main__":
    sys.exit(chat_server())
