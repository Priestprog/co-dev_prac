import shlex

#fio = input("ФИО: ")
#place = input("Место рождения: ")
fio = "Иванов Иван Иванович"
place = 'гостиница "Рояль"'


command_line = shlex.join(["register", fio, place])

print("Этот ужас:")
print(command_line)
print(shlex.split(command_line), "\n\n")


cmd_join = shlex.join(["register", fio, place])
print("shlex.join():")
print(cmd_join)


simple_cmd = 'register "Иванов Иван Иванович" "гостиница \\"Рояль\\""'
print("ALT:")
print(simple_cmd)

tokens_join = shlex.split(cmd_join)
tokens_simple = shlex.split(simple_cmd)

print("shlex.join():")
print(tokens_join)
print("ALT:")
print(tokens_simple)


