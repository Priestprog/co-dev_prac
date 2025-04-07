import calendar

def restmonth(year, month):
    """
        Генерирует календарь для указанного месяца и года в два файла: .txt и .rst.

        Аргументы:
            year (int): Год для календаря.
            month (int): Месяц для календаря.

        Возвращает:
            tuple: Пути к созданным файлам .txt и .rst.
    """
    filename = f"restcalend-{year}-{month}.rst"
    with open(filename, "w") as f:

        cal = calendar.monthcalendar(year, month)
        month_name = calendar.month_name[month]
        f.write(f"Календарь на  {month_name} {year}\n================================\n\n")
        f.write(f".. table:: {month_name} {year}\n\n")
        f.write("    == == == == == == ==\n")
        f.write("    Mo Tu We Th Fr Sa Su\n")
        f.write("    == == == == == == ==\n")

        for week in cal:
            formatted_week = [str(day) if day != 0 else "  " for day in week]
            f.write("    " + " ".join(f"{day:>2}" for day in formatted_week) + "\n")

        f.write("    == == == == == == ==\n")

    return  filename

