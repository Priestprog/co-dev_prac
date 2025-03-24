import socket
import threading

clients = []

def handle_client(client_socket, addr):
    """Обрабатывает входящие сообщения от клиента и рассылает их всем"""
    print(f"Новое соединение: {addr}")
    clients.append(client_socket)
    try:
        while True:
            msg = client_socket.recv(1024)
            if not msg:
                break
            print(f"{addr} сказал: {msg.decode()}")
            for c in clients:
                if c != client_socket:
                    c.sendall(msg)
    except Exception:
        pass
    finally:
        print(f"Отключение {addr}")
        clients.remove(client_socket)
        client_socket.close()

def start_server(host='0.0.0.0', port=12345):
    """Запускает сервер"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Сервер запущен на {host}:{port}")
    
    while True:
        client, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.start()

if __name__ == "__main__":
    start_server()

