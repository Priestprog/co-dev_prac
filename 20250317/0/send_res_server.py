#!/usr/bin/env python3
import asyncio
import cmd
import threading
import sys

clients = {}

async def chat(reader, writer):
    me = "{}:{}".format(*writer.get_extra_info('peername'))
    print(f"Подключился: {me}")
    clients[writer] = writer
    try:
        while not reader.at_eof():
            data = await reader.readline()
            if not data:
                break
            message = data.decode().strip()
            broadcast_msg = f"{me}: {message}"
            print(f"Получено: {broadcast_msg}")
            for w in clients.values():
                try:
                    w.write(f"{broadcast_msg}\n".encode())
                    await w.drain()
                except Exception as e:
                    print("Ошибка отправки:", e)
    except Exception as e:
        print("Ошибка в chat:", e)
    finally:
        print(f"Отключился: {me}")
        writer.close()
        await writer.wait_closed()
        del clients[writer]

async def start_server():
    server = await asyncio.start_server(chat, '0.0.0.0', 1337)
    print("Сервер запущен на 0.0.0.0:1337")
    async with server:
        await server.serve_forever()

async def send_message(msg, writer):
    writer.write(f"{msg}\n".encode())
    await writer.drain()

async def client_receive(reader):
    try:
        while not reader.at_eof():
            data = await reader.readline()
            if not data:
                break
            print("\n" + data.decode().strip())
    except asyncio.CancelledError:
        pass

class ChatClientCmd(cmd.Cmd):
    prompt = '> '

    def __init__(self, writer, loop):
        super().__init__()
        self.writer = writer
        self.loop = loop

    def do_print(self, arg):
        if not arg:
            print("Использование: print <сообщение>")
            return
        asyncio.run_coroutine_threadsafe(send_message(arg, self.writer), self.loop)

    def do_info(self, arg):
        peer = self.writer.get_extra_info('peername')
        if not arg:
            info_str = f"Host: {peer[0]}, Port: {peer[1]}"
        else:
            param = arg.strip().lower()
            if param.startswith('h'):
                info_str = f"Host: {peer[0]}"
            elif param.startswith('p'):
                info_str = f"Port: {peer[1]}"
            else:
                info_str = "Неизвестный параметр. Используйте 'host' или 'port'."
        asyncio.run_coroutine_threadsafe(send_message(info_str, self.writer), self.loop)

    def do_exit(self, arg):
        print("Выход из чата...")
        self.writer.close()
        return True

async def start_client():
    try:
        reader, writer = await asyncio.open_connection('127.0.0.1', 1337)
    except Exception as e:
        print("Ошибка подключения к серверу:", e)
        return

    print("Подключено к серверу.")

    asyncio.create_task(client_receive(reader))

    loop = asyncio.get_running_loop()
    client_cmd = ChatClientCmd(writer, loop)
    thread = threading.Thread(target=client_cmd.cmdloop, daemon=True)
    thread.start()

    await writer.wait_closed()
    print("Соединение закрыто.")

async def main():
    server_task = asyncio.create_task(start_server())
    await asyncio.sleep(0.5)
    await start_client()
    server_task.cancel()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Программа завершена.")
