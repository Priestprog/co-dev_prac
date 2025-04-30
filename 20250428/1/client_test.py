import unittest
from unittest.mock import Mock, AsyncMock, patch
from io import StringIO
import sys
from mood.client.__main__ import Client


class TestClientCommands(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.writer = Mock()
        self.writer.drain = AsyncMock()
        self.client = Client("tester", None)
        self.client.writer = self.writer

    async def test_addmon_valid(self):
        await self.client.process_command("addmon dragon hello 'boo' hp 30 coords 1 1")
        self.writer.write.assert_called_with(b"addmon dragon hello 'boo' hp 30 coords 1 1\n")

    async def test_addmon_invalid(self):
        await self.client.process_command("addmon dragon hp 30")
        self.writer.write.assert_not_called()

    async def test_attack_valid(self):
        await self.client.process_command("attack dragon with sword")
        self.writer.write.assert_called_with(b"attack dragon with sword\n")

    async def test_attack_invalid_weapon(self):
        command = "attack dragon with stick"
        captured_output = StringIO()
        sys.stdout = captured_output
        await self.client.process_command(command)
        sys.stdout = sys.__stdout__
        self.writer.write.assert_not_called()
        self.assertIn("Unknown weapon", captured_output.getvalue())

    async def test_movement_commands(self):
        for direction in ["left", "right", "up", "down"]:
            with self.subTest(direction=direction):
                self.writer.reset_mock()
                await self.client.process_command(direction)
                self.writer.write.assert_called_with(f"{direction}\n".encode())
