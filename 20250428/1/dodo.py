import glob
import shutil
from zipfile import ZipFile

DOIT_CONFIG = {"default_tasks": ["html"]}


def task_docs():
    """Генерация документации Sphinx (html + text)"""
    rst_files = glob.glob('docs/*.rst')
    return {
        'actions': [
            "sphinx-build -b html docs docs/_build/html",
            "sphinx-build -b text docs docs/_build/text",
        ],
        'file_dep': ['docs/conf.py'] + rst_files,
        'targets': ['docs/_build/html/index.html', 'docs/_build/text/index.txt'],
        'clean': True,
    }


def task_erase():
    """Удаление всех сборок (вручную сделай коммит перед этим!)"""
    def erase():
        shutil.rmtree('docs/_build', ignore_errors=True)
        try:
            os.remove('docs.zip')
            os.remove('docs.list')
        except FileNotFoundError:
            pass
    return {
        'actions': [erase],
        'verbosity': 2,
    }


def task_zip():
    """Создание архива документации"""
    return {
        'actions': ['cd docs/_build/html && zip -r ../../../docs.zip .'],
        'file_dep': ['docs/_build/html/index.html'],
        'targets': ['docs.zip'],
        'clean': True,
    }


def task_stat():
    """Создание списка содержимого zip-архива"""
    def generate_list():
        with ZipFile('docs.zip') as zf:
            with open('docs.list', 'w') as f:
                f.write('\n'.join(zf.namelist()))
    return {
        'actions': [generate_list],
        'file_dep': ['docs.zip'],
        'targets': ['docs.list'],
        'clean': True,
    }


def task_pot():
    """Генерация .pot шаблона"""
    return {
        'actions': ['sphinx-build -b gettext docs locale'],
        'targets': ['locale/index.pot'],
        'clean': True,
    }


def task_po():
    """Обновление .po переводов"""
    return {
        'actions': ['sphinx-intl update -p locale -l ru'],
        'file_dep': ['locale/index.pot'],
        'targets': ['locale/ru/LC_MESSAGES/index.po'],
        'clean': True,
    }


def task_mo():
    """Компиляция переводов"""
    return {
        'actions': ['sphinx-intl build'],
        'file_dep': ['locale/ru/LC_MESSAGES/index.po'],
        'targets': ['locale/ru/LC_MESSAGES/index.mo'],
        'clean': True,
    }


def task_i18n():
    """Полная генерация переводов"""
    return {
        'actions': None,
        'task_dep': ['pot', 'po', 'mo'],
    }


def task_html():
    """Генерация HTML-документации с учётом перевода"""
    return {
        'actions': ['sphinx-build -b html docs docs/_build/html'],
        'file_dep': ['docs/conf.py'] + glob.glob('docs/*.rst'),
        'targets': ['docs/_build/html/index.html'],
        'task_dep': ['i18n'],
        'clean': [(shutil.rmtree, ['docs/_build/html'], {'ignore_errors': True})],
    }


def task_test():
    """Прогон тестов клиента и сервера"""
    return {
        'actions': ['pytest tests/'],
        'task_dep': ['i18n'],
        'clean': True,
    }

