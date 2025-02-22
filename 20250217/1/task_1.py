from pathlib import Path
import sys
import zlib
from glob import iglob
from os.path import basename, dirname

# функция при вызове без второго аргумента
def list_branches(repo_path):
    repo = Path(f"{repo_path}/.git/refs/heads")

    if not repo.is_dir():
        print(f"Ошибка: {repo_path} не является каталогом.")
        exit(0)

    for item in repo.iterdir():
        print(item.name)

# Функция при вызове с вторым аргументом
def check_branch(repo_path, branch_name):
    with open(f"{repo_path}/.git/refs/heads/{branch_name}", "r") as f:
        commit = f.read()

    with open(f"{repo_path}/.git/objects/{commit[:2]}/{commit[2:-1]}", "rb") as f2:
        message = f2.read()

    decompressed_message = zlib.decompress(message)
    obj_type, _, content = decompressed_message.partition(b"\x00")

    print(content.decode())
    #Печать последенего коммита


    tree = content.decode().split("\n")[0].split(" ")[1]
    with open(f"{repo_path}/.git/objects/{tree[:2]}/{tree[2:]}", "rb") as f3:
        tree_content = f3.read()

    branches = zlib.decompress(tree_content)
    obj_type, _, data = branches.partition(b"\x00")

    index = 0
    result = []
    git_modes = {
        "100644": "blob",
        "40000": "tree"
    }

    while index < len(data):
        mode_end = data.find(b" ", index)
        mode = data[index:mode_end].decode()
        index = mode_end + 1

        name_end = data.find(b"\x00", index)
        name = data[index:name_end].decode()
        index = name_end + 1

        sha1 = data[index:index + 20]
        index += 20

        sha1_hex = sha1.hex()

        result.append(f"{git_modes.get(mode, "Неизвестный тип")} {sha1_hex}    {name} ")

    print("\n".join(result))
    # Печать содержимого tree на который указывает последний коммит

    


if len(sys.argv) < 2:
    print("Использование: script.py <путь_к_каталогу> [<имя_ветки>]")
    sys.exit(1)

repo_path = sys.argv[1]

if len(sys.argv) == 2:
    list_branches(repo_path)
else:
    branch_name = sys.argv[2]
    check_branch(repo_path, branch_name)
