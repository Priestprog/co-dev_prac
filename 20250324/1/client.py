import sys
from io import StringIO
from cowsay import read_dot_cow, cowthink, list_cows
import shlex
import cmd
import readline
import asyncio
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.patch_stdout import patch_stdout


history = InMemoryHistory()

commands = ["exit", "addmon", "attack",
            "up", "down", "left", "right",
            "status"]
completer = WordCompleter(commands, ignore_case=True)


class Game(cmd.Cmd):
    prompt = ">> "
    intro = "<<< Welcome to Python-MUD 0.1 >>>"
    field_size = 10
    custom_monsters = {
        "jgsbat": read_dot_cow(StringIO(r"""
        $the_cow = <<EOC;
            ,_                    _,
            ) '-._  ,_    _,  _.-' (
            )  _.-'.|\\\\--//|.'-._  (
             )'   .'\/o\/o\/'.   `(
              ) .' . \====/ . '. (
               )  / <<    >> \  (
                '-._/``  ``\_.-'
          jgs     __\\\\'--'//__
                 (((""`  `"")))
        EOC
        """))
    }

    def complete_attack(self, text, line, begidx, endidx):
        words = (line[:endidx] + ".").split()
        args_command = []
        match len(words):
            case 2:
                    args_command = self.custom_monsters.keys() | list_cows()
            case 3:
                args_command = [ "with"]
            case 4:
                    args_command = self.weapons
        return [c for c in args_command if c.startswith(text)]

class Client:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

    async def send_messages(self):
        loop = asyncio.get_running_loop()
        try:
            with (patch_stdout()):
                while True:
                    command = await loop.run_in_executor(None,
                                                         lambda: prompt(">> ", history=history, completer=completer))
                    if not command:
                        continue

                    test_command = shlex.split(command)
                    namecommand = test_command[0]
                    field_size = 10

                    if namecommand not in commands:
                        print("Unknown command")
                        continue

                    if command == 'exit':
                        break

                    if namecommand in ["up", "down", "left", "right"]:
                        if len(test_command) != 1:
                            print("Invalid arguments")
                            continue

                    if namecommand == "addmon":
                        usage = "Usage: addmon <NAME> hello <MESSAGE> hp <HP> coords <X> <Y>"
                        args = test_command[1:]
                        if not args:
                            print(f"Invalid arguments\n{usage}")
                            continue

                        name = args[0]
                        if name not in list_cows() | Game.custom_monsters.keys():
                            print(f"Unknown monster {name}")
                            continue

                        params = {}
                        param_names = ["hello", "hp", "coords"]
                        expected_params = 3
                        i = 1

                        try:
                            while i < len(args):
                                if args[i] in param_names:
                                    param = args[i]
                                    if param == "coords":
                                        params[param] = (int(args[i + 1]), int(args[i + 2]))
                                        i += 3
                                    else:
                                        params[param] = args[i + 1]
                                        i += 2
                                else:
                                    print(f"Invalid argument: {args[i]}\n{usage}")
                                    continue

                            if len(params) != expected_params:
                                print(f"Invalid number of arguments\n{usage}")
                                continue
                            x, y = params['coords']

                            if not (0 <= x < field_size and 0 <= y < field_size):
                                print(f"Invalid coordinates"
                                      f"\nField size is {field_size}x{field_size}")
                                continue

                        except (ValueError, IndexError):
                            print(f"Invalid arguments\n{usage}")
                            continue

                    if test_command[0] == "attack":
                        args = test_command[1:]
                        weapons = {"sword", "spear", "axe"}

                        try:
                            if "with" == args[2]:
                                if args[3] not in weapons:
                                    print("Unknown weapon")
                                    continue

                        except IndexError:
                            print("Invalid argument")
                            continue

                    self.writer.write(f"{command}\n".encode())
                    await self.writer.drain()

        except (KeyboardInterrupt, EOFError):
            print("\nClient is shutting down...")

        finally:
            self.writer.close()
            await self.writer.wait_closed()
            print("Disconnected.")

    async def receive_messages(self):
        while True:
            try:
                msg = await self.reader.readline()
                if not msg:
                    break
                print(msg.decode().rstrip('\n'))
            except (KeyboardInterrupt, EOFError):
                print("\nClient is shutting down...")

    async def run(self):
        await self.connect()
        await asyncio.gather(self.receive_messages(), self.send_messages())


if __name__ == '__main__':
    try:
        asyncio.run(Client().run())
    except KeyboardInterrupt:
        print('Client stopped manually.')
