import unittest
import multiprocessing
import socket
import time
import asyncio
from time import sleep

from mood.server.__main__ import run_server
HOST = "127.0.0.1"
PORT = 8888

def wait_for_server(host, port, timeout=5):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.1)
    raise TimeoutError("Server did not start in time.")

class TestMudServer(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        cls.server_process = multiprocessing.Process(target=run_server, daemon=True)
        cls.server_process.start()
        wait_for_server(HOST, PORT)

    @classmethod
    def tearDownClass(cls):
        cls.server_process.terminate()
        cls.server_process.join()

    async def asyncSetUp(self):
        self.reader, self.writer = await asyncio.open_connection(HOST, PORT)
        self.writer.write("priest\n".encode())
        await self.writer.drain()
        response = (await self.reader.readline()).decode().rstrip('\n')
        self.assertEqual(response, "SUCCESS")

    async def asyncTearDown(self):
        self.writer.close()
        await self.writer.wait_closed()

    async def read_full_response(self, timeout=1):
        buffer = []
        start = time.time()
        while True:
            if time.time() - start > timeout:
                break
            try:
                line = await asyncio.wait_for(self.reader.readline(), timeout=0.2)
                if not line:
                    break
                buffer.append(line.decode())
            except asyncio.TimeoutError:
                break
        return "".join(buffer)

    async def send_command(self, command):
        self.writer.write(f"{command}\n".encode())
        await self.writer.drain()
        data = await self.read_full_response()
        return data

    async def test_add_move_attack(self):
        response_add = await self.send_command("addmon dragon hello 'Hi' hp 100 coords 0 1")
        self.assertIn("priest added a monster dragon at (0, 1)", response_add)

        response_locale = await self.send_command("locale ru_RU.UTF8")
        self.assertIn("Установлена локаль: ru_RU.UTF8\n", response_locale)

        response_move = await self.send_command("down")
        predicted_response = r"""Переместился на (0, 1)
 ____
( Hi )
 ----
      o                    / \  //\
       o    |\___/|      /   \//  \\
            /0  0  \__  /    //  | \ \
           /     /  \/_/    //   |  \  \
           @_^_@'/   \/_   //    |   \   \
           //_^_/     \/_ //     |    \    \
        ( //) |        \///      |     \     \
      ( / /) _|_ /   )  //       |      \     _\
    ( // /) '/,_ _ _/  ( ; -.    |    _ _\.-~        .-~~~^-.
  (( / / )) ,-{        _      `-.|.-~-.           .~         `.
 (( // / ))  '/\      /                 ~-. _ .-~      .-~^-.  \
 (( /// ))      `.   {            }                   /      \  \
  (( / ))     .----~-.\        \-'                 .~         \  `. \^-.
             ///.----..>        \             _ -~             `.  ^-`  ^-_
               ///-._ _ _ _ _ _ _}^ - - - - ~                     ~-- ,.-~
                                                                  /.-~
"""

        response_lines = response_move.strip().splitlines()
        expected_lines = predicted_response.strip().splitlines()

        for expected, actual in zip(expected_lines, response_lines):
            self.assertEqual(expected.strip(), actual.strip())

        response_attack = await self.send_command("attack dragon with sword")
        self.assertIn("priest атаковал dragon на (0, 1), урон 10 хп\nУ dragon осталось 90 очков здоровья\n", response_attack)
