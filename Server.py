from pathlib import Path
import FileServer as fs
import socket_utils as su
from typing import Any
import argparse

# Debug mode control
DEBUG = False  # Overwritten by script args below

def debug_log(msg: str):
    if DEBUG:
        print(msg)

# Optionally allow debug flag from CLI (only if run as __main__)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()
    globals()["DEBUG"] = args.debug

HOST, PORT = "127.0.0.1", 65432

server = fs.FileServer(HOST, PORT)
while True:
    server.init_connection()
    data: Any = None
    if server.client_connection is not None:  # appease the type checker
        while True:
            data = server.recv()
            # Handle client commands:
            match data:
                case "LIST":
                    # LIST: Send directory tree to client
                    list_data = server.get_dir_structure(Path("./ServerFS"))
                    su.send_with_len(server.client_connection, list_data)
                case "GET":
                    # GET: Wait for filename, then send the requested file
                    filename = server.recv()
                    server.send(filename, file=True)
                case "SET":
                    # SET: Receive a file from the client and save it to the server
                    server.recv(file=True)
                case _:
                    # Ignore unrecognized commands
                    pass
