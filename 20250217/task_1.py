from pathlib import Path
import sys

def list_branches(repo_path):
    repo = Path(f"{repo_path}/.git/refs/heads")

    if not repo.is_dir():
        print(f"Ошибка: {repo_path} не является каталогом.")
        return

    for item in repo.iterdir():
        print(item.name)

def check_branch(repo_path, branch_name):
    repo = Path(repo_path)
    branch_path = repo / branch_name

    if branch_path.exists():
        print(f"Элемент '{branch_name}' найден в {repo_path}.")
    else:
        print(f"Элемент '{branch_name}' отсутствует в {repo_path}.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: script.py <путь_к_каталогу> [<имя_ветки>]")
        sys.exit(1)

    repo_path = sys.argv[1]

    if len(sys.argv) == 2:
        list_branches(repo_path)
    else:
        branch_name = sys.argv[2]
        check_branch(repo_path, branch_name)
