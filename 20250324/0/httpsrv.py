#!/usr/bin/env python3
import sys
import socket
from http.server import SimpleHTTPRequestHandler, HTTPServer, test

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Использование: python httpsrv.py PORT")
        sys.exit(1)
    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Порт должен быть числом.")
        sys.exit(1)

    ip = get_ip()
    print(f"Запуск HTTP-сервера на {ip}:{port} ...")

    # Передаём явно протокол, затем порт и IP в качестве bind-адреса
    test(SimpleHTTPRequestHandler, HTTPServer, "HTTP/1.0", port, ip)

