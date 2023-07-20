from socket import *
from collections import defaultdict		# for dictionary list 
import sys

def check_if_unlocked(filename, filename_locked_map):
  if filename_locked_map[filename] == "unlocked":
			return True
  else:
			return False

def main():

	filename_locked_map = {}
	filename_clients_map = defaultdict(list)
	waiting_client = False
	client_timeout_map = {}

  unlocked = check_if_unlocked(filename, filename_locked_map)
  if unlocked == True:
  else:

if __name__ == "__main__":
	main()
