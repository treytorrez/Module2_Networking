from pathlib import Path
import socket, os, socket_utils as su  # , struct, pickle
from typing import Tuple, Any
from time import sleep

# Debug mode control
DEBUG = False  # Set by script arg or manually for debugging


def debug_log(msg: str):
    if DEBUG:
        print(msg)


type directory = dict[str, None | directory]


class FileServer:
    host: str
    port: int
    sock_timeout: float
    listener: socket.socket
    client_connection: socket.socket | None
    client_addr: tuple[str, int] | None

    def __init__(self, host: str, port: int, sock_timeout: float = 20):
        self.host = host
        self.port = port
        self.sock_timeout = sock_timeout
        self.client_connection = None
        self.client_addr = None

        self.listener = socket.socket()
        self.listener.settimeout(self.sock_timeout)
        self.listener.bind((self.host, self.port))
        self.listener.listen()
        debug_log("[fileserver:__init__] File Server Initialized")

    def init_connection(self) -> Tuple[socket.socket, tuple[str, int]]:
        """
        Block until a client connects (or raises socket.timeout).
        Stores the new socket on self.connection so other methods can use it.
        """
        conn, addr = self.listener.accept()
        self.client_connection = conn
        self.client_addr = addr
        debug_log("[fileserver:init_connection] Client connection initialized")
        return conn, addr

    def close_connection(self) -> None:
        """Tear down the client socket (but leave the listener open)."""
        if self.client_connection:
            self.client_connection.close()
            self.client_connection = None
            self.client_addr = None
            debug_log("[fileserver:close_connection] Client connection closed")

    def shutdown(self) -> None:
        """Tear down both client and listener sockets."""
        debug_log("[fileserver:shutdown] Shutting down in 5 seconds...")
        sleep(5)
        self.close_connection()
        self.listener.close()

    def send(self, payload: bytes | Path, file: bool = False) -> None:
        if self.client_connection is None:
            raise RuntimeError("[fileserver:send] No client connection!")
        if file:
            debug_log(f"[fileserver:send] Sending file: {payload}")
            return su.send_file(
                self.client_connection, Path("./ServerFS") / Path(payload)
            )
        else:
            debug_log(f"[fileserver:send] Sending payload: {payload}")
            return su.send_with_len(self.client_connection, payload)

    def recv(self, file: bool = False) -> Any | Path:
        if self.client_connection is None:
            raise RuntimeError("[fileserver:recv] No client connection!")
        if file:
            debug_log("[fileserver:recv] Receiving file...")
            return su.recv_file(self.client_connection, Path("./ServerFS"))
        else:
            debug_log("[fileserver:recv] Receiving payload...")
            return su.recv_with_len(self.client_connection)

    def get_dir_structure(self, root_path: Path) -> directory:
        """
        Recursively returns a dict representing the folder structure of root_path.
        """
        root_path = Path(root_path)
        structure: directory = {}
        try:
            for entry in os.scandir(root_path):
                if entry.is_dir(follow_symlinks=False):
                    structure[entry.name] = self.get_dir_structure(Path(entry.path))
                else:
                    structure[entry.name] = None
        except PermissionError:
            debug_log(
                f"[fileserver:get_dir_structure] Permission error for {root_path}"
            )
        return structure
