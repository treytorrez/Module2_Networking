from pathlib import Path
import socket
import socket_utils as su
from typing import Any

type directory = dict[str, None | directory]

class Client:
    """
    Network client for communicating with the file server.
    Attributes:
        connection: The socket used for communication.
        server_addr: Tuple of (host, port) for the server.
    """
    connection: socket.socket
    server_addr: tuple[str, int] | None

    def __init__(self, host: str = "127.0.0.1", port: int = 65432):
        self.connection = socket.socket()
        self.server_addr = (host, port)
        try:
            self.connection.connect(self.server_addr)
            print(f"[Client.__init__] Connected to {self.server_addr}")
        except Exception as e:
            print(f"[Client.__init__] Connection failed: {e}")
            raise

    def RetrieveDirectory(self) -> directory:
        """
        Requests the server directory structure and returns it as a nested Dict.
        """
        try:
            print("[RetrieveDirectory] Sending LIST command...")
            self.send_with_len("LIST")
            print("[RetrieveDirectory] LIST command sent.")
            print("[RetrieveDirectory] Waiting for directory bytes...")
            directory_obj: directory = self.recv_with_len()
            print(f"[RetrieveDirectory] Directory object received (type: {type(directory_obj)})")
            return directory_obj
        except Exception as e:
            print(f"[RetrieveDirectory] ERROR: {e}")
            raise

    def send_with_len(self, payload: Any) -> None:
        su.send_with_len(self.connection, payload)

    def recv_with_len(self) -> Any:
        return su.recv_with_len(self.connection)

    def recv(self, file: bool = False) -> Any | Path:
        
        
        if file:
            # Always use Path for dir argument
            return su.recv_file(self.connection, Path(__file__).parent / "ClientFS")
        else:
            return su.recv_with_len(self.connection)

    def send(self, payload: Any, file: bool = False) -> None:
        if file:
            # Always use Path for file argument
            return su.send_file(self.connection, payload)
        else:
            return su.send_with_len(self.connection, payload)

##############
# TESTING CODE
##############
if __name__ == "__main__":
    client = Client(host="127.0.0.1", port=65432)
    try:
        # Test send and receive basic communication
        while True:
            print("1 LIST")
            print("2 GET")
            print("3 SET")
            choice: int = int(input("choose test"))
            match choice:
                case 1:
                    files = client.RetrieveDirectory()
                    print(f"[main] Files from server (type: {type(files)}):")
                    print(files)
                case 2:
                    print("[main] Sending GET command...")
                    client.send_with_len("GET")
                    print("[main] GET command sent. requesting file 1.txt")
                    client.send("1.txt")
                    client.recv(True)
                    print("[main] Sending second GET command...")
                    client.send_with_len("GET")
                    print("[main] second GET command sent. requesting file 2.txt")
                    client.send("2.txt")
                    client.recv(True)
                case 3:
                    print("[main] Sending SET command...")
                    client.send_with_len("SET")
                    print("[main] SET command sent. Sending file.")
                    client.send("3.txt", file=True)
                    print("[main] Sending second SET command...")
                    client.send_with_len("SET")
                    print("[main] second SET command sent. Sending file.")
                    client.send("4.txt", file=True)
                case 4:
                    print("[main] Closing connection.")
                    client.connection.close()
                    break
                case _:
                    pass
    except Exception as e:
        print(f"[main] ERROR: {e}")
