import sys
from .restcalend import restmonth
def main():
    """
    Главная функция для запуска из командной строки.

    Используется для генерации календаря через командную строку:
    
        python3 -m restcalend ГОД МЕСЯЦ
    """
    if len(sys.argv) != 3:
        print("Использование: python3 -m restcalend ГОД МЕСЯЦ")
        sys.exit(1)
    
    year, month = int(sys.argv[1]), int(sys.argv[2])
    text_file = restmonth(year, month)

if __name__ == "__main__":
    main()