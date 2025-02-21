from pathlib import Path
import sys
import zlib


def list_branches(repo_path):
    repo = Path(f"{repo_path}/.git/refs/heads")

    if not repo.is_dir():
        print(f"Ошибка: {repo_path} не является каталогом.")
        exit(0)

    for item in repo.iterdir():
        print(item.name)


def check_branch(repo_path, branch_name):
    with open(f"{repo_path}/.git/refs/heads/{branch_name}", "r") as f:
        commit = f.read()

    with open(f"{repo_path}/.git/objects/{commit[:2]}/{commit[2:-1]}", "rb") as f2:
        message = f2.read()

    decompressed_message = zlib.decompress(message)
    obj_type, _, content = decompressed_message.partition(b"\x00")
    print(content.decode())



if len(sys.argv) < 2:
    print("Использование: script.py <путь_к_каталогу> [<имя_ветки>]")
    sys.exit(1)

repo_path = sys.argv[1]

if len(sys.argv) == 2:
    list_branches(repo_path)
else:
    branch_name = sys.argv[2]
    check_branch(repo_path, branch_name)
