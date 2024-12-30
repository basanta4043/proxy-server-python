import os
import socket
import threading

# Configuration
PROXY_HOST = '127.0.0.1'  # Host for the proxy server
PROXY_PORT = 8000       # Port for the proxy server
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")           # Port of the actual database server

def handle_client(client_socket, db_host, db_port):
    """Handles communication between a client and the database server."""
    try:
        # Connect to the actual database server
        db_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        db_socket.connect((db_host, db_port))

        # Thread to send data from client to the database server
        def forward_to_db():
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                db_socket.sendall(data)

        # Thread to send data from the database server to the client
        def forward_to_client():
            while True:
                data = db_socket.recv(4096)
                if not data:
                    break
                client_socket.sendall(data)

        # Start forwarding threads
        client_to_db = threading.Thread(target=forward_to_db)
        db_to_client = threading.Thread(target=forward_to_client)

        client_to_db.start()
        db_to_client.start()

        # Wait for both threads to finish
        client_to_db.join()
        db_to_client.join()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        db_socket.close()

def start_proxy(proxy_host, proxy_port, db_host, db_port):
    """Starts the proxy server."""
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind((proxy_host, proxy_port))
    proxy_socket.listen(5)
    print(f"Proxy server listening on {proxy_host}:{proxy_port}")

    try:
        while True:
            client_socket, addr = proxy_socket.accept()
            print(f"Connection received from {addr}")
            # Start a new thread to handle the client connection
            client_handler = threading.Thread(
                target=handle_client,
                args=(client_socket, db_host, db_port)
            )
            client_handler.start()
    except KeyboardInterrupt:
        print("\nShutting down proxy server.")
    finally:
        proxy_socket.close()

if __name__ == "__main__":
    start_proxy(PROXY_HOST, PROXY_PORT, DB_HOST, DB_PORT)