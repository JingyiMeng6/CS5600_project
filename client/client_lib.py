from socket import *
import sys
import os.path

curr_path = os.path.dirname(os.path.realpath(sys.argv[0]))
def create_socket():
    s = socket(AF_INET, SOCK_STREAM)
    return s

def send_directory_service(client_socket, filename, RW, list_files):
    serverName = 'localhost'
    serverPort = 9090   # port of directory service
    client_socket.connect((serverName,serverPort))

    if not list_files:
        msg = filename + '|' + RW
        # send the string requesting file info to directory send_directory_service
        client_socket.send(msg.encode())
        reply = client_socket.recv(1024)
        reply = reply.decode()
    else:
        msg = "LIST"
        # send the string requesting file info to directory service
        client_socket.send(msg.encode())
        reply = client_socket.recv(1024)
        reply = reply.decode()
        client_socket.close()
        print ("Listing files on directory server...")
        print (reply)

    #print (reply)
    return reply

def instructions():
    # instructions to the user
    print ("------------------- INSTRUCTIONS ----------------------")
    print ("<write> [filename] - write file mode")
    print ("<end> - finish writing")
    print ("<read> [filename] - read file mode")
    print ("<list> - lists all existing files")
    print ("<instructions> - check the instructions again")
    print ("<quit> - exits the application")
    print ("-------------------------------------------------------\n")

def print_breaker():
    print ("--------------------------------")

def check_valid_input(input_string):
    # check for correct format for message split
    if len(input_string.split()) < 2:
        print ("Incorrect format")
        instructions()
        return False
    else:
        return True

def handle_read(filename, file_version_map, client_id):
    # create socket to directory service
    client_socket = create_socket()
    # send file name to directory service
    reply_DS = send_directory_service(client_socket, filename, 'r', False)
    client_socket.close()

    if reply_DS == "FILE_DOES_NOT_EXIST":
        print(filename + " does not exist on any fileserver")
    else:
        # parse info received from the directory service
        filename_DS = reply_DS.split('|')[0]
        fileserverIP_DS = reply_DS.split('|')[1]
        fileserverPORT_DS = reply_DS.split('|')[2]

        # print("File name is: " + filename_DS)
        # print("File server IP is: " + fileserverIP_DS)
        # print("File server port is: " + fileserverPORT_DS)
        # create socket to file server
        client_socket = create_socket()
        # send request to file server
        read_cache = send_read(client_socket, fileserverIP_DS, int(fileserverPORT_DS), filename_DS, "r", file_version_map, "READ", filename_DS, client_id)

        if not read_cache:
            reply_FS = client_socket.recv(1024)    # receive reply from file server, this will be the text from the file
            reply_FS = reply_FS.decode()
            client_socket.close()

            if reply_FS != "EMPTY_FILE":
                print_breaker()
                print (reply_FS)
                print_breaker()

                cache(filename_DS, reply_FS, "w", client_id)  # update the cached file with the new version from the file server
                print (filename_DS + " successfully cached...")
            else:
                print(filename_DS + " is empty...")
                del file_version_map[filename_DS]


# return false if the file content is got from file server
# return true if the file content is from cache
def send_read(client_socket, fileserverIP_DS, fileserverPORT_DS, filename , RW, file_version_map, msg, filename_DS, client_id):
    # if there is no cache for this file, directly send read file request to the file server
    if filename not in file_version_map:
        file_version_map[filename] = 0
        print("REQUESTING FILE FROM FILE SERVER - FILE NOT IN CACHE")
        send_msg = filename + "|" + RW + "|" + msg
        client_socket.connect((fileserverIP_DS,fileserverPORT_DS))
        client_socket.send(send_msg.encode())
        return False
    # if there is cache for this file, we will first compare the cache file version and the version on file server
    cache_file = os.path.join(curr_path, "client_cache", client_id, filename_DS)
    if os.path.exists(cache_file) == True:
        # the message to send to file server
        send_msg = "CHECK_VERSION|" + filename
        client_socket1 = create_socket()
        client_socket1.connect((fileserverIP_DS,fileserverPORT_DS))
        # send check version request to the file server
        client_socket1.send(send_msg.encode())
        print("Checking version...")
        version_FS = client_socket1.recv(1024)    # receive file server version number
        version_FS = version_FS.decode()
        client_socket1.close()
    # if the version number on file server is different from local version, we will read file content from file server
    if version_FS != str(file_version_map[filename]):
        print("Versions do not match...")
        print("REQUESTING FILE CONTENT FROM FILE SERVER...")
        # Update local file version
        file_version_map[filename] = int(version_FS)
        # message to request file content
        send_msg = filename + "|" + RW + "|" + msg

        # send the message to request file content from file server
        client_socket.connect((fileserverIP_DS,fileserverPORT_DS))
        client_socket.send(send_msg.encode())
        #print ("SENT MSG: " + send_msg)
        return False
    else:
        # read from cache
        print("Versions match, reading from cache...")
        cache(filename_DS, "READ", "r", client_id)

    return True


def cache(filename_DS, write_client_input, RW, client_id):
    cache_file = os.path.join(curr_path, "client_cache", client_id, filename_DS)

    os.makedirs(os.path.dirname(cache_file), exist_ok=True)

    if RW == "a+" or RW == "w":
        with open(cache_file, RW) as f:  # write to the cached file
            f.write(write_client_input)
    else:
        with open(cache_file, "r") as f:  # read from the cached file
            print_breaker()
            print(f.read())
            print_breaker()