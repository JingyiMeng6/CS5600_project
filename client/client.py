import sys
import client_lib
from datetime import datetime
from time import gmtime, strftime


def main():
    print("\n")
    client_lib.instructions()
    client_id = strftime("%Y%m%d%H%M%S", gmtime())
    file_version_map = {}

    while True:

        client_input = sys.stdin.readline()

        if "<write>" in client_input:
            print("Entering <write> mode...\n")
            print("Exiting <write> mode...\n")

        if "<read>" in client_input:
            print("Entering <read> mode...\n")
            print("Exiting <read> mode...\n")

        if "<list>" in client_input:
            print("List all files\n")

        if "<instructions>" in client_input:
            client_lib.instructions()

        if "<quit>" in client_input:
            print("Exiting application...")
            sys.exit()


if __name__ == "__main__":
    main()