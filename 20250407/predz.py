import cmd
import sys

class CommandInterpreter(cmd.Cmd):
    def __init__(self, input_source=None):
        super().__init__()
        if input_source:
            self.stdin = input_source
        self.prompt = ''
        self.use_rawinput = False

    def do_bless(self, line):
        print(f"Be blessed, {line}!")

    def do_sendto(self, line):
        print(f"Go to {line}!")

    def do_EOF(self, args):
        return True

def run_interpreter(input_source=None):
    interpreter = CommandInterpreter(input_source)
    interpreter.cmdloop()

def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        try:
            with open(filename, 'r') as file:
                run_interpreter(input_source=file)
        except FileNotFoundError:
            print(f"Файл {filename} не найден.")
    else:
        run_interpreter()

if __name__ == "__main__":
    main()

