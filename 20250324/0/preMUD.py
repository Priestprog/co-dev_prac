#!/usr/bin/env python3
import cmd
import socket
import threading
import sys

class ChatClient(cmd.Cmd):
    prompt = '> '

    def __init__(self, sock):
        super().__init__()
        self.sock = sock
        # Запускаем поток для приёма сообщений
        self.receiver_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receiver_thread.start()

    def receive_messages(self):
        """Поток для приёма и вывода сообщений из сокета."""
        while True:
            try:
                data = self.sock.recv(1024)
                if not data:
                    print("\nСоединение закрыто сервером.")
                    break
                # Печатаем полученное сообщение, не нарушая приглашение командной строки.
                print("\nПолучено: " + data.decode())
                print(self.prompt, end="", flush=True)
            except Exception as e:
                print(f"\nОшибка приёма: {e}")
                break

    def do_hi(self, arg):
        """Отправляет сообщение 'Hello everybody'."""
        try:
            self.sock.sendall("Hello everybody".encode())
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")

    def do_say(self, arg):
        """Отправляет введённое сообщение. Использование: say <сообщение>"""
        if not arg:
            print("Использование: say <сообщение>")
            return
        try:
            self.sock.sendall(arg.encode())
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")

    def do_exit(self, arg):
        """Завершает работу клиента."""
        print("Выход из чата.")
        self.sock.close()
        return True

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Использование: python chat_client.py HOST PORT")
        sys.exit(1)

    host = sys.argv[1]
    try:
        port = int(sys.argv[2])
    except ValueError:
        print("Порт должен быть числом.")
        sys.exit(1)

    # Создаем и подключаем сокет к серверу
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
    except Exception as e:
        print(f"Не удалось подключиться к {host}:{port} - {e}")
        sys.exit(1)

    print(f"Подключено к {host}:{port}. Введите команды: hi или say <сообщение>. Для выхода введите exit.")

    # Запускаем цикл обработки команд
    client = ChatClient(sock)
    client.cmdloop()

