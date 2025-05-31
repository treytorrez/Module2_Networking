from pathlib import Path
import socket as s, struct, pickle
from typing import Any

# Debug mode control
DEBUG = True  # Set this to True to enable debug output, or set via script argument

def debug_log(msg: str):
    if DEBUG:
        print(msg)

# Protocol schema: Length header (8 bytes) + Name header (256 bytes) + File data
#
# Byte offsets         | Field              | Description                        | Example (hex)
# ---------------------|--------------------|------------------------------------|----------------------------------------------
# 0x00 – 0x07          | Length             | Unsigned big-endian integer        | 00 00 00 00 00 00 04 B0         # 1200 bytes
# 0x08 – 0x107         | Name               | UTF-8 filename, null-padded at end | 66 6F 6F 2E 74 78 74 00 … 00    # "foo.txt"
# 0x108 – 0x108+Length | Data               | Raw file bytes                     | FF D8 FF E0 …                   # JPEG start
#
# Flattened hex stream (example):
# 00 00 00 00 00 00 04 B0   66 6F 6F 2E 74 78 74 00 … 00   FF D8 FF E0 …


def send_with_len(sock: s.socket, payload: Any) -> None:
    """
    Serializes and sends any Python object with an 8-byte length-prefixed header.
    Args:
        sock: The socket to send on.
        payload: The Python object to send (will be pickled).
    """
    data_bytes: bytes = pickle.dumps(payload)
    debug_log(f"[socket_utils:send_with_len] Data to send (bytes): {len(data_bytes)}")
    header: bytes = struct.pack("!Q", len(data_bytes))
    debug_log(f"[socket_utils:send_with_len] Header (8 bytes): {header.hex()}")
    sock.sendall(header + data_bytes)
    debug_log("[socket_utils:send_with_len] Payload sent successfully.")


def send_file(sock: s.socket, path: Path) -> None:
    path = Path(path)  # Ensure Path object
    print(f"{path} is type {type(path)}")
    if path.is_file():
        print("did we get past this?")
        with path.open("rb") as file:
            data_bytes: bytes = file.read()
            name_bytes: bytes = path.name.encode("utf-8")
            headers: bytes = struct.pack("!Q256s", len(data_bytes), name_bytes)
            debug_log(f"[socket_utils:send_file] Headers (8 + 256 bytes): {headers.hex()[:110]}...")
            sock.sendall(headers + data_bytes)
            debug_log("[socket_utils:send_file] File sent successfully.")


def recv_file(sock: s.socket, dir: Path) -> Path:
    dir = Path(dir)
    debug_log("[socket_utils:recv_file] Receiving header (8 bytes + 256 bytes)...")
    headers: bytes = recv_exact_bytes(sock, 264)
    data_len: int   = int(struct.unpack("!Q256s", headers)[0])
    data_name: str = struct.unpack("!Q256s", headers)[1].decode("utf-8", errors="replace").strip("\x00")
    debug_log(f"[socket_utils:recv_file] Data length to receive: {data_len} bytes.")
    debug_log(f"[socket_utils:recv_file] Data name to receive: {data_name}.")
    data_bytes: bytes = recv_exact_bytes(sock, data_len)
    debug_log(f"[socket_utils:recv_file] Received {len(data_bytes)} data bytes.")
    newpath: Path = dir / data_name
    with newpath.open("xb") as newfile:
        file_len: int = newfile.write(data_bytes)
        if data_len == len(data_bytes) == file_len:
            debug_log("[socket_utils:recv_file] File received and decoded successfully (lengths match).")
        else:
            debug_log(f"[socket_utils:recv_file] LENGTHS DO NOT MATCH: data_len={data_len}, data_bytes={len(data_bytes)}, file_len={file_len}")
    return newpath


def recv_exact_bytes(sock: s.socket, length: int) -> bytes:
    """
    Receive exactly 'length' bytes from the socket.
    Args:
        sock: The socket to receive from.
        length: The number of bytes to receive.
    """
    buf = b""
    debug_log(f"[socket_utils:recv_exact_bytes] Expecting {length} bytes.")
    while len(buf) < length:
        chunk = sock.recv(length - len(buf))
        debug_log(f"[socket_utils:recv_exact_bytes] Received chunk of {len(chunk)} bytes.")
        if not chunk:
            debug_log("[socket_utils:recv_exact_bytes] ERROR: Socket closed before expected bytes received!")
            raise ConnectionError("Socket closed early")
        buf += chunk
    debug_log(f"[socket_utils:recv_exact_bytes] All {len(buf)} bytes received.")
    return buf

def recv_with_len(sock: s.socket) -> Any:
    """
    Receives a length-prefixed pickled Python object.
    Args:
        sock: The socket to receive from.
    """
    debug_log("[socket_utils:recv_with_len] Receiving header (8 bytes)...")
    header: bytes = recv_exact_bytes(sock, 8)
    data_len: int = int(struct.unpack("!Q", header)[0])
    debug_log(f"[socket_utils:recv_with_len] Data length to receive: {data_len} bytes.")
    data_bytes: bytes = recv_exact_bytes(sock, data_len)
    debug_log(f"[socket_utils:recv_with_len] Received {len(data_bytes)} data bytes.")
    data: Any = pickle.loads(data_bytes)
    debug_log("[socket_utils:recv_with_len] Data unpickled successfully.")
    return data
