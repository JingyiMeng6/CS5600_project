from socket import *
# for dictionary list 
from collections import defaultdict		
import sys

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

	filename_locked_map = {}
	filename_clients_map = defaultdict(list)
	waiting_client = False
	client_timeout_map = {}


	while 1:
		connectionSocket, addr = serverSocket.accept()
		recv_msg = connectionSocket.recv(1024)
		recv_msg = recv_msg.decode()

		print("\nRECEIVED: " + recv_msg )

		if "_1_:" in recv_msg:
			client_id = recv_msg.split("_1_:")[0]
			filename = recv_msg.split("_1_:")[1]
			waiting_client = False


			unlocked = check_if_unlocked(filename, filename_locked_map)
			if unlocked == True:
				# a count to check if current client is first in the queue
				count_temp = 0		

				# if no clients currently waiting on the file
				if len(filename_clients_map[filename]) == 0:	
					# lock the file
					filename_locked_map[filename] = "locked"	
					grant_message = "file_granted"
					print("SENT: " + grant_message + " ---- " + client_id)
					# send the grant message
					connectionSocket.send(grant_message.encode())	

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

			# if the file is locked
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

				# if client polled 100 times (10 sec), send timeout
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
					connectionSocket.send(grant_message.encode())	

		# if unlock message (_2_) received 
		elif "_2_:" in recv_msg:		
			client_id = recv_msg.split("_2_:")[0]
			filename = recv_msg.split("_2_:")[1]

			# unlock the current file
			filename_locked_map[filename] = "unlocked"		
			grant_message = "File unlocked..."
			# tell the current client that the file was unlocked
			connectionSocket.send(grant_message.encode())	

		connectionSocket.close()



if __name__ == "__main__":
	main()
