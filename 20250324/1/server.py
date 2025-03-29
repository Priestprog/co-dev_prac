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

    def __init__(self):
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
        args = shlex.split(arg)
        name = args[0]
        params = {}
        param_names = ["hello", "hp", "coords"]
        i = 1

        while i < len(args):
            if args[i] in param_names:
                param = args[i]
                if param == "coords":
                    params[param] = (int(args[i + 1]), int(args[i + 2]))
                    i += 3
                else:
                    params[param] = args[i + 1]
                    i += 2

        hello = params['hello']
        hp = int(params['hp'])
        x, y = params['coords']

        replaced = (x, y) in self.monsters
        self.monsters[(x, y)] = (name, hello, hp)
        self.writer.write(f"Added monster {name} at ({x}, {y}) saying {hello} with {hp} HP\n".encode())
        if replaced:
            self.writer.write(b"Replaced the old monster\n")


    def do_attack(self, arg):
        """Attack the monster in the current cell."""

        args = shlex.split(arg)
        name_monster = args[0]
        self.player_weapon = args[2]
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


class Server:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.clients = set()
        self.game = Game()

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f'New connection from {addr}')
        self.clients.add(writer)

        try:
            while True:
                msg = await reader.readline()
                if not msg:
                    break

                msg = msg.decode().strip()

                print(f'{addr} says: {msg}')

                writer.write(f"{msg}\n".encode())

        except Exception as e:
            print(f'Connection error with {addr}: {e}')
        finally:
            print(f'Closing connection from {addr}')
            self.clients.remove(writer)
            writer.close()
            await writer.wait_closed()

    async def run(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        print(f'Working on {addr}')

        async with server:
            await server.serve_forever()


if __name__ == '__main__':
    try:
        asyncio.run(Server().run())
    except KeyboardInterrupt:
        print('Server stopped successfully.')
