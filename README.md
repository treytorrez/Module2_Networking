# Overview

This project is a simple Python-based file transfer system using a client/server architecture. It allows users to browse, upload, and download files from a server using a command-line or Textual TUI client. The system is designed to demonstrate core networking, file transfer, and serialization techniques in Python.

## How to Use

1. **Start the Server**:

   - Navigate to the project directory and run:

     ```bash
     python Server.py
     ```

   - By default, the server listens on `127.0.0.1:65432`.

2. **Start the Client**:

   - In a separate terminal, run:

     ```bash
     python clientApp.py
     ```

   - The client provides a Textual-based terminal UI to browse local/server files, upload to server, and download from server.

## Purpose

This software was written to provide a hands-on demonstration of Python network programming and file transfer, as well as experience working with socket communication, serialization, and terminal UI development. It is intended as both a portfolio project and a practical learning exercise.

## Demo Video

[Software Demo Video](http://youtube.link.goes.here)

# Network Communication

- **Architecture**: Client/Server
- **Protocol**: TCP
- **Port**: 65432 (default)
- **Message Format**:

  - General commands and directory structures are sent using Python's `pickle` serialization, length-prefixed with an 8-byte header.
  - File transfers use a custom protocol: `[8-byte big-endian length][256-byte filename][raw file bytes]`.
  - See `socket_utils.py` for protocol details.

# Development Environment

- **Language**: Python 3.10+
- **Libraries**:

  - Standard Library: `socket`, `pickle`, `struct`, `argparse`, `pathlib`
  - [Textual](https://textual.textualize.io/) (for TUI client)

- **Tools**: VS Code, Git

# Useful Websites

- [Python socket — Low-level networking interface](https://docs.python.org/3/library/socket.html)
- [Textual TUI Framework](https://textual.textualize.io/)
- [Python pathlib — Object-oriented filesystem paths](https://docs.python.org/3/library/pathlib.html)
- [Python struct — Interpret bytes as packed binary data](https://docs.python.org/3/library/struct.html)

# Future Work

- Add user authentication and access control
- Support file/folder deletion and renaming
- Add progress indicators and error handling in the TUI client
- Make server multi-client (concurrent connections)
- Provide more robust configuration for host/port
