import sys
from io import StringIO
from cowsay import read_dot_cow, cowthink, list_cows
import shlex
import cmd
import readline
import asyncio


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

    def __init__(self, writer):
        super().__init__()
        self.player_x = 0
        self.player_y = 0
        self.monsters = {}
        self.weapons = {
            "sword": 10,
            "spear": 15,
            "axe": 20,
        }
        self.player_weapon = "sword"
        self.writer = writer

    def do_exit(self, arg):
        self.writer.write(b"exit...\n")
        return b"exit\n"

    def do_status(self, arg):
        self.writer.write(b"Server work.\n")

    def encounter(self, x, y):
        if (x, y) in self.monsters:
            name, hello, hp = self.monsters[(x, y)]
            if name in self.custom_monsters:
                self.writer.write((cowthink(hello, cowfile=self.custom_monsters[name])+"\n").encode())
            else:
                self.writer.write((cowthink(hello, cow=name)+"\n").encode())

    def move_player(self, dx, dy, arg):
        """Generalized player movement function"""
        self.player_x = (self.player_x + dx) % self.field_size
        self.player_y = (self.player_y + dy) % self.field_size
        self.writer.write(f"Moved to ({self.player_x}, {self.player_y})\n".encode())
        self.encounter(self.player_x, self.player_y)

    def do_up(self, arg):
        """Move the player up."""
        self.move_player(0, -1, arg)

    def do_down(self, arg):
        """Move the player down."""
        self.move_player(0, 1, arg)

    def do_left(self, arg):
        """Move the player left."""
        self.move_player(-1, 0, arg)

    def do_right(self, arg):
        """Move the player right."""
        self.move_player(1, 0, arg)

    def do_addmon(self, arg):
        "Add a monster to the game."
        usage = "Usage: addmon <NAME> hello <MESSAGE> hp <HP> coords <X> <Y>"
        args = shlex.split(arg)
        if not args:
            self.writer.write(f"Invalid arguments\n{usage}\n".encode())
            return

        name = args[0]
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
                    self.writer.write(f"Invalid argument: {args[i]}\n{usage}\n".encode())
                    return

            if len(params) != expected_params:
                self.writer.write(f"Invalid number of arguments\n{usage}\n".encode())
                return

            hello = params['hello']
            hp = int(params['hp'])
            x, y = params['coords']

            if not (0 <= x < self.field_size and 0 <= y < self.field_size):
                self.writer.write(f"Invalid coordinates\nField size is {self.field_size}x{self.field_size}\n".encode())
                return

            replaced = (x, y) in self.monsters
            self.monsters[(x, y)] = (name, hello, hp)
            self.writer.write(f"Added monster {name} at ({x}, {y}) saying {hello} with {hp} HP\n".encode())
            if replaced:
                self.writer.write(b"Replaced the old monster\n")

        except (ValueError, IndexError):
            self.writer.write(f"Invalid arguments\n{usage}\n".encode())
            return

    def do_attack(self, arg):
        """Attack the monster in the current cell."""
        args = shlex.split(arg)

        name_monster = args[0]

        try:
            if "with" in args:
                if args[2] in self.weapons:
                    self.player_weapon = args[2]
                else:
                    self.writer.write(b"Unknown weapon\n")
                    return
        except IndexError:
            self.writer.write(b"Invalid argument\n")
            return

        damage = self.weapons[self.player_weapon]

        x, y = self.player_x, self.player_y
        if (x, y) not in self.monsters:
            self.writer.write(b"No monster here\n")
            return
        if name_monster not in self.monsters[(x,y)]:
            self.writer.write(f"No {name_monster} here\n".encode())
            return

        name, hello, hp = self.monsters[(x, y)]
        new_hp = hp - damage

        self.writer.write(f"Attacked {name_monster}, damage {damage} hp\n".encode())
        if new_hp <= 0:
            del self.monsters[(x, y)]
            self.writer.write(f"{name_monster} died\n".encode())
        else:
            self.monsters[(x, y)] = (name_monster, hello, new_hp)
            self.writer.write(f"{name_monster} now has {new_hp}\n".encode())

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


async def handle_client(reader, writer):
    writer.write(b"<<< Welcome to Python-MUD 0.1 >>>\n")
    writer.write(b">> ")
    await writer.drain()

    game = Game(writer)
    while data := await reader.readline():
        if data == b'exit\n':
            break
        command = data.decode()

        test_command = shlex.split(command)
        allowed_commands = {"addmon", "attack",
        "up", "down", "left", "right", "exit", "status"}
        field_size = 10

        if test_command[0] not in allowed_commands:
            writer.write(b"Unknown command\n")
            continue

        if test_command[0] == ["up", "down", "left", "right"]:
            if len(test_command) != 1:
                writer.write(b"Invalid arguments\n")
                continue

        if test_command[0] == "addmon":
            usage = "Usage: addmon <NAME> hello <MESSAGE> hp <HP> coords <X> <Y>"
            args = test_command[1:]
            if not args:
                writer.write(f"Invalid arguments\n{usage}\n".encode())
                continue

            name = args[0]
            if name not in list_cows() | game.custom_monsters.keys():
                writer.write(f"Unknown monster {name}\n".encode())
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
                        writer.write(f"Invalid argument: {args[i]}\n{usage}\n".encode())
                        continue

                if len(params) != expected_params:
                    writer.write(f"Invalid number of arguments\n{usage}\n".encode())
                    continue
                x, y = params['coords']

                if not (0 <= x < field_size and 0 <= y < field_size):
                    writer.write(
                        f"Invalid coordinates\nField size is {field_size}x{field_size}\n".encode())
                    continue

            except (ValueError, IndexError):
                writer.write(f"Invalid arguments\n{usage}\n".encode())
                continue

        if test_command[0] == "attack":
            args = test_command[1:]
            weapons = {"sword","spear", "axe"}

            try:
                if "with" == args[1]:
                    if args[2] not in weapons:
                        writer.write(b"Unknown weapon\n")
                        continue

            except IndexError:
                writer.write(b"Invalid argument\n")
                continue


        game.onecmd(command)
        writer.write(b">> ")
        await writer.drain()

    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle_client, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()


asyncio.run(main())