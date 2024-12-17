import socket
import threading

class ModbusServer:
    def __init__(self, engine):
        self.engine = engine
        self.node = None
        self.server_socket = None
        self.running = True

    def run(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(('0.0.0.0', 8899))
            self.server_socket.listen(1)
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    self.node = client_socket
                    print(f"Client connected from {address}")
                    
                    # Handle client in a separate thread
                    client_thread = threading.Thread(target=self.handle_client, 
                                                  args=(client_socket,))
                    client_thread.daemon = True
                    client_thread.start()
                except Exception as e:
                    print(f"Error accepting connection: {e}")
                    
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def handle_client(self, client_socket):
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                self.engine.last_data = data
                # Process the received data here
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()
            if self.node == client_socket:
                self.node = None

    def send_data(self, data):
        if self.node is None:
            return -1
        try:
            self.node.send(data)
            return 0
        except Exception as e:
            print(f"Error sending data: {e}")
            return -1

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
