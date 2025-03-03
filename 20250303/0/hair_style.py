import shlex

line = input(">")
tokens = shlex.split(line)
normalized_line = shlex.join(tokens)

print("Причесанная строка:", normalized_line)