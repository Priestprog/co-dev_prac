import glob
import shutil
from zipfile import ZipFile

DOIT_CONFIG = {"default_tasks": ["html"]}


def task_pot():
    """[Babel] Генерация POT-шаблона"""
    return {
        'actions': ['pybabel extract -F babel.cfg -o locales/messages.pot .'],
        'targets': ['locales/messages.pot'],
        'clean': True,
    }

def task_po():
    """[Babel] Обновление PO-файлов из POT-шаблона"""
    return {
        'actions': ['pybabel update -D messages -d locales -l ru_RU -i locales/messages.pot'],
        'file_dep': ['locales/messages.pot'],
        'targets': ['locales/ru_RU/LC_MESSAGES/messages.po'],
        'clean': True,
    }

def task_mo():
    """[Babel] Компиляция переводов (.po -> .mo)"""
    return {
        'actions': ['pybabel compile -D messages -d locales'],
        'file_dep': ['locales/ru_RU/LC_MESSAGES/messages.po'],
        'targets': ['locales/ru_RU/LC_MESSAGES/messages.mo'],
        'clean': True,
    }

def task_i18n():
    """Полная генерация переводов"""
    return {
        'actions': None,
        'task_dep': ['pot', 'po', 'mo'],
    }

def task_html():
    """Генерация html-документации Sphinx"""
    rst_files = glob.glob('source/*.rst')
    return {
        'actions': ["sphinx-build -b html source build/html"],
        'file_dep': ['source/conf.py'] + rst_files,
        'targets': ['build/html/index.html'],
        'clean': [(shutil.rmtree, ['build/html'], {'ignore_errors': True})],
    }

def task_test():
    """Прогон тестов клиента и сервера"""
    return {
        'actions': [
            'python3 -m unittest server_test.py',
            'python3 -m unittest client_test.py',
        ],
        'task_dep': ['i18n']
    }


