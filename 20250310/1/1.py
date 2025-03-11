import sys
from io import StringIO
from cowsay import read_dot_cow, cowthink
import shlex
import cmd


FIELD_SIZE = 10


class Game(cmd.Cmd):
    prompt = ">> "
    intro = "<<< Welcome to Python-MUD 0.1 >>>"
    field_size = FIELD_SIZE
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

    def encounter(self, x, y):
        if (x, y) in self.monsters:
            name, hello, hp = self.monsters[(x, y)]
            if name in self.custom_monsters:
                print(cowthink(hello, cowfile=self.custom_monsters[name]))
            else:
                print(cowthink(hello, cow=name))

    def move_player(self, dx, dy, arg):
        """Обобщенная функция для перемещения игрока."""
        if arg:
            print("Invalid arguments")
            return
        self.player_x = (self.player_x + dx) % self.field_size
        self.player_y = (self.player_y + dy) % self.field_size
        print(f"Moved to ({self.player_x}, {self.player_y})")
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

if __name__ == "__main__":
    Game().cmdloop()