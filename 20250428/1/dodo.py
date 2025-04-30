import glob
import shutil
from zipfile import ZipFile

DOIT_CONFIG = {"default_tasks": ["html"]}


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
    rst_files = glob.glob('source/*.rst')
    return {
        'actions': ['sphinx-build -b html source build/html'],
        'file_dep': ['source/conf.py'] + rst_files,
        'targets': ['build/html/index.html'],
        'task_dep': ['i18n'],
        'clean': [(shutil.rmtree, ['build/html'], {'ignore_errors': True})],
    }

def task_docs():
    """Генерация text-документации Sphinx (без перевода)"""
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
    }


