# locking service
from socket import *
from collections import defaultdict		
import sys

# 1. Server Initialization: The server is set up to listen on localhost at port 4040.
serverAddr = "localhost"
serverPort = 4040
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind((serverAddr, serverPort))
serverSocket.listen(10)
print ('LOCKING SERVICE is ready to receive...')

def check_if_unlocked(filename, filename_locked_map):

	# check for existance of filename as a key in the dictionary
	if filename in filename_locked_map:		
		if filename_locked_map[filename] == "unlocked":
			return True
		else:
			return False
	else:
		filename_locked_map[filename] = "unlocked"
		return True

def main():

	# 2. Dictionaries:
	# filename_locked_map: Maps filenames to their current status (either "locked" or "unlocked").
	# filename_clients_map: A defaultdict that keeps a list of clients waiting for each file.
	# client_timeout_map: Maps a client ID to the number of times it has polled/waited for a file.
	filename_locked_map = {}
	filename_clients_map = defaultdict(list)
	waiting_client = False
	client_timeout_map = {}

	# 6. main loop
	# The server continuously listens for incoming connections and processes the received messages as described.
	while 1:
		connectionSocket, addr = serverSocket.accept()
		recv_msg = connectionSocket.recv(1024)
		recv_msg = recv_msg.decode()

		print("\nRECEIVED: " + recv_msg )

		# 3. Message Types:
		# _1_: indicates a lock request.
		# _2_: indicates an unlock request.

		# 4. Lock Request Handling:
		# case 1. If the requested file is unlocked or not in the map,
		# 	the server checks the queue of clients waiting for the file.
		# case 2. If no clients are waiting or the current client is the first in line,
		# 	the server locks the file and grants access to the client.
		# case 3. If the file is locked, the server increments the client's timeout counter or initializes it.
		# 	3a. If the timeout counter reaches 100,
		# 	a "TIMEOUT" message is sent to the client and the client is removed from the waiting list.
		# 	3b. If not, the server checks if the client is already waiting for the file.
		# 		If the client is not waiting, it's added to the list.
		# 		A "file_not_granted" message is then sent to the client.
		if "_1_:" in recv_msg:
			client_id = recv_msg.split("_1_:")[0]
			filename = recv_msg.split("_1_:")[1]
			waiting_client = False

			unlocked = check_if_unlocked(filename, filename_locked_map)
			if unlocked == True:
				# a count to check if current client is first in the queue
				count_temp = 0		

				# case 1
				# if no clients currently waiting on the file
				if len(filename_clients_map[filename]) == 0:	
					# lock the file
					filename_locked_map[filename] = "locked"	
					grant_message = "file_granted"
					print("SENT: " + grant_message + " ---- " + client_id)
					# send the grant message
					connectionSocket.send(grant_message.encode())

				# case 2
				elif filename in filename_clients_map:			
					# find the current file in the map
					for filename,values in filename_clients_map.items():	
						# iterate though the clients waiting on this file
						for v in values:									
							# if the client is the first client waiting
							if v == client_id and count_temp == 0:			
								# remove it from the waiting list
								filename_clients_map[filename].remove(v)	
								# lock the file
								filename_locked_map[filename] = "locked"	
								grant_message = "file_granted"			
								print("SENT: " + grant_message +" ---- " + client_id)	
								# send the grant message
								connectionSocket.send(grant_message.encode())	
							count_temp += 1

			# case 3. If the file is locked, the server increments the client's timeout counter or initializes it.
			# 	3a.If the timeout counter reaches 100,
			# 	a "TIMEOUT" message is sent to the client and the client is removed from the waiting list.
			# 	3b.If not, the server checks if the client is already waiting for the file.
			# 		If the client is not waiting, it's added to the list.
			# 		A "file_not_granted" message is then sent to the client.
			else:				
				grant_message = "file_not_granted"

				# check if first time requesting file
				if client_id in client_timeout_map:		
					# if first time, set timeout value to 0
					client_timeout_map[client_id] = client_timeout_map[client_id] + 1		
					print("TIME: " + str(client_timeout_map[client_id]))
				else:
					# if not first time, increment timeout value of client
					client_timeout_map[client_id] = 0	

				# case 3a: if client polled 100 times (10 sec), send timeout
				if client_timeout_map[client_id] == 100:	
					timeout_msg = "TIMEOUT"
					# find the current file in the map
					for filename,values in filename_clients_map.items():	
						# iterate though the clients waiting on this file 
						for v in values:									
							# if the client is the first client waiting
							if v == client_id:		
								# remove it from the waiting list
								filename_clients_map[filename].remove(v)	
					# remove client from timeout map
					del client_timeout_map[client_id]			
					# send timeout msg
					connectionSocket.send(timeout_msg.encode())

				# case 3b:
				# 	If not, the server checks if the client is already waiting for the file.
				# 		If the client is not waiting, it's added to the list.
				# 		A "file_not_granted" message is then sent to the client.
				else:
					if filename in filename_clients_map:						
						# find the current file in the map
						for filename,values in filename_clients_map.items():	
							# iterate though the clients waiting on this file 
							for v in values:							
								# check if client is already waiting on the file
								if v == client_id:					
									# if already waiting, set flag - so client is not added to waiting list multiple times for the file 
									waiting_client = True			
					
					# if not already waiting
					if waiting_client == False:			
						# append client to lists of clients waiting for the file
						filename_clients_map[filename].append(client_id)	

					print("SENT: " + grant_message + client_id)
					# send file not granted message
					# The server sends the message back to the client after converting it to bytes.
					connectionSocket.send(grant_message.encode())	

		# 5. Unlock Request Handling:
		# If an unlock request is received, the file is set to "unlocked" and a confirmation is sent to the client.
		elif "_2_:" in recv_msg:		
			client_id = recv_msg.split("_2_:")[0]
			filename = recv_msg.split("_2_:")[1]

			# unlock the current file
			filename_locked_map[filename] = "unlocked"		
			grant_message = "File unlocked..."

			# tell the current client that the file was unlocked
			# The server sends the message back to the client after converting it to bytes.
			connectionSocket.send(grant_message.encode())

		# The server closes the connection with the current client after handling its request.
		connectionSocket.close()


if __name__ == "__main__":
	main()
