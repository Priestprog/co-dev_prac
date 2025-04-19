"""
Сервер Python-MUD с поддержкой локализации.
"""
from cowsay import cowthink
import shlex
import cmd
import asyncio
from ..common import HOST, PORT, FIELD_SIZE, CUSTOM_MONSTERS
import random
import gettext


LOCALE_DIR = "locales"
DEFAULT_LOCALE = "en_US.UTF-8"

monsters = {}
users = dict()
DIRECTIONS = {
    "right": (1, 0),
    "left": (-1, 0),
    "up": (0, -1),
    "down": (0, 1)
}

def get_translator(locale_str):
    try:
        if isinstance(locale_str, list):
            locale_str = locale_str[0]
        translator = gettext.translation('messages', LOCALE_DIR, languages=[locale_str])
        translator.install()
        return translator.gettext, translator.ngettext
    except FileNotFoundError:
        gettext.install('messages')
        return gettext.gettext, gettext.ngettext


class Game(cmd.Cmd):
    def __init__(self, server, writer, nickname):
        super().__init__()
        self.server = server
        self.player_x = 0
        self.player_y = 0
        self.weapons = {
            "sword": 10,
            "spear": 15,
            "axe": 20,
        }
        self.player_weapon = "sword"
        self.writer = writer
        self.nickname = nickname
        self.locale = DEFAULT_LOCALE
        self._, self.ngettext = get_translator(self.locale)

    def say_all(self, msg):
        for client in users.values():
            game = getattr(client, 'game', None)
            if game:
                game._, game.ngettext = get_translator(game.locale)
                client.write(msg)

    def do_sayall(self, message):
        for client in users.values():
            if client != self.writer:
                client.write(self._("{}: {}\n").format(self.nickname, shlex.split(message)[0]).encode())

    def do_exit(self, arg):
        self.writer.write(self._("exit...\n").encode())
        return b"exit\n"

    def do_status(self, arg):
        self.writer.write(self._("Server work.\n").encode())

    def encounter(self, x, y):
        if (x, y) in monsters:
            name, hello, hp = monsters[(x, y)]
            if name in CUSTOM_MONSTERS:
                self.writer.write((cowthink(hello, cowfile=CUSTOM_MONSTERS[name]) + "\n").encode())
            else:
                self.writer.write((cowthink(hello, cow=name) + "\n").encode())

    def move_player(self, dx, dy, arg):
        self.player_x = (self.player_x + dx) % FIELD_SIZE
        self.player_y = (self.player_y + dy) % FIELD_SIZE
        self.writer.write(self._("Moved to ({}, {})\n").format(self.player_x, self.player_y).encode())
        self.encounter(self.player_x, self.player_y)

    def do_up(self, arg):
        self.move_player(0, -1, arg)

    def do_down(self, arg):
        self.move_player(0, 1, arg)

    def do_left(self, arg):
        self.move_player(-1, 0, arg)

    def do_right(self, arg):
        self.move_player(1, 0, arg)

    def do_addmon(self, arg):
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

        replaced = (x, y) in monsters
        monsters[(x, y)] = (name, hello, hp)

        hp_msg = self.ngettext(
            "{} added a monster {} at ({}, {}) saying '{}' with {} health point\n",
            "{} added a monster {} at ({}, {}) saying '{}' with {} health points\n",
            hp
        ).format(self.nickname, name, x, y, hello, hp)

        self.say_all(self._(hp_msg).encode())

        if replaced:
            hp_repl_msg = self.ngettext(
                "{} replaced the old monster in ({}, {}) with a monster {} at ({}, {}) saying '{}' with {} health point\n",
                "{} replaced the old monster in ({}, {}) with a monster {} at ({}, {}) saying '{}' with {} health points\n",
                hp
            ).format(self.nickname, x, y, name, x, y, hello, hp)

            self.say_all(self._(hp_repl_msg).encode())

    def do_attack(self, arg):
        args = shlex.split(arg)
        name_monster = args[0]
        self.player_weapon = args[2]
        damage = self.weapons[self.player_weapon]

        x, y = self.player_x, self.player_y
        if (x, y) not in monsters:
            self.writer.write(self._("No monster here\n").encode())
            return

        if name_monster not in monsters[(x, y)]:
            self.writer.write(self._("No {} here\n").format(name_monster).encode())
            return

        name, hello, hp = monsters[(x, y)]
        new_hp = hp - damage

        if new_hp <= 0:
            del monsters[(x, y)]
            self.say_all(self._("{} attacked {} in ({}, {}), damage {} hp\n{} died\n")
                         .format(self.nickname, name_monster, x, y, damage, name_monster).encode())
        else:
            monsters[(x, y)] = (name_monster, hello, new_hp)
            hp_msg = self.ngettext(
                "{} now has {} health point\n",
                "{} now has {} health points\n",
                new_hp
            ).format(name_monster, new_hp)
            self.say_all(self._("{} attacked {} in ({}, {}), damage {} hp\n")
                         .format(self.nickname, name_monster, x, y, damage).encode() + hp_msg.encode())

    def do_movemonsters(self, arg):
        if arg == "on":
            if self.server.monsters_enabled and self.server.monsters_task and not self.server.monsters_task.done():
                self.writer.write(self._("Moving monsters: on\n").encode())
            else:
                self.server.monsters_enabled = True
                self.server.monsters_task = asyncio.create_task(move_monsters_loop())
                self.say_all(self._("Moving monsters: on\n").encode())
        elif arg == "off":
            if self.server.monsters_task and not self.server.monsters_task.done():
                self.server.monsters_task.cancel()
            self.server.monsters_enabled = False
            self.say_all(self._("Moving monsters: off\n").encode())

    def do_locale(self, arg):
        args = shlex.split(arg)
        if args:
            locale_str = args[0]
        else:
            locale_str = DEFAULT_LOCALE

        self.locale = locale_str
        self._, self.ngettext = get_translator(self.locale)
        self.writer.write(self._("Set up locale: ").encode() + self.locale.encode() + b"\n")


async def move_monsters_loop():
    while True:
        await asyncio.sleep(30)
        success = False
        coords_of_monsters = list(monsters.keys())
        while not success:
            if not coords_of_monsters:
                break
            old_x, old_y = random.choice(coords_of_monsters)
            name, hello, hp = monsters[(old_x, old_y)]
            direction = random.choice(list(DIRECTIONS.keys()))
            dx, dy = DIRECTIONS[direction]
            new_x = (old_x + dx) % FIELD_SIZE
            new_y = (old_y + dy) % FIELD_SIZE
            if (new_x, new_y) in monsters:
                continue
            del monsters[(old_x, old_y)]
            monsters[(new_x, new_y)] = (name, hello, hp)
            for client in users.values():
                game = getattr(client, 'game', None)
                if game:
                    if game:
                        game._, game.ngettext = get_translator(game.locale)
                        monster_moved_massage = game._("{} moved one cell {}\n").format(name, direction).encode()
                        client.write(monster_moved_massage)

                    if game.player_x == new_x and game.player_y == new_y:
                        if name in CUSTOM_MONSTERS:
                            client.write((cowthink(hello, cowfile=CUSTOM_MONSTERS[name]) + "\n").encode())
                        else:
                            client.write((cowthink(hello, cow=name) + "\n").encode())
            success = True


class Server:
    """Сервер."""

    def __init__(self, host=HOST, port=PORT):
        """Инициализация сервера на заданном порте и хосте."""
        self.host = host
        self.port = port
        self.clients = dict()
        self.monsters_task = None
        self.monsters_enabled = True


    async def handle_client(self, reader, writer):
        """При подключении клиента, проверяем ник в системе и запускаем играть."""
        addr = writer.get_extra_info('peername')
        username = (await reader.readline()).decode().strip()

        if username in users:
            writer.write(b"ERROR\n")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            print(f"User {username} try to connected from {addr} but can't")
            return
        else:
            users[username] = writer
            print(f"User {username} connected from {addr}")
            writer.write(b"SUCCESS\n")
            await writer.drain()

        game = Game(self, writer, username)
        writer.game = game
        try:
            while True:
                msg = await reader.readline()
                if not msg:
                    break

                command = msg.decode().strip()
                print(f'{addr} says: {command}')
                game.onecmd(command)

        except Exception as e:
            print(f'Connection error with {addr}: {e}')
        finally:
            print(f'Closing connection from {addr}')
            users.pop(username)
            writer.close()
            await writer.wait_closed()

    async def run(self):
        """Запуск сервера."""
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        print(f'Working on {addr}')

        self.monsters_task = asyncio.create_task(move_monsters_loop())

        async with server:
            await server.serve_forever()


if __name__ == '__main__':

    try:
        asyncio.run(Server().run())
    except KeyboardInterrupt:
        print('Server stopped successfully.')