import cmd
import calendar
import shlex

class CalendarCLI(cmd.Cmd):
    prompt = "cal> "
    cal = calendar.TextCalendar()

    def do_prmonth(self, arg):
        "Календарь на заданный год и месяц: prmonth <год> <месяц>"
        try:
            args = shlex.split(arg)
            if len(args) != 2:
                print("Ошибка!\nПравильное использование команды: prmonth <год> <месяц>")
                return
            year = int(args[0])
            month = self.parse_month(args[1])
            if month is None:
                print("Ошибка: неверное название месяца.")
                return
            self.cal.prmonth(year, month)
        except ValueError:
            print("Ошибка: год и месяц должны быть числами.")

    def do_pryear(self, arg):
        "Календарь на весь год: pryear <год>"
        try:
            year = int(arg)
            self.cal.pryear(year)
        except ValueError:
            print("Ошибка: укажите корректный год.")
    
    def complete_prmonth(self, text, line, begidx, endidx):
        "Автодополнение для месяцев"
        month_names = [name.lower() for name in calendar.Month.__members__.keys()]
        return [m for m in month_names if m.startswith(text.lower())]

    def help_prmonth(self):
        print(self.do_prmonth.__doc__)
    
    def help_pryear(self):
        print(self.do_pryear.__doc__)

    def parse_month(self, month_str):
        "Преобразует название месяца в число"
        month_str = month_str.lower()
        for name, value in calendar.Month.__members__.items():
            if name.lower() == month_str:
                return value
        try:
            month = int(month_str)
            if 1 <= month <= 12:
                return month
        except ValueError:
            pass
        return None

    def do_exit(self, arg):
        "Выход из программы"
        print("Выход из CLI-календаря.")
        return True

    def help_exit(self):
        print("Выход из программы: exit")

if __name__ == "__main__":
    CalendarCLI().cmdloop()
