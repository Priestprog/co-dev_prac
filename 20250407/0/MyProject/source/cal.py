import sys
import calendar

def generate_rest_calendar(year, month):
    with open(f"restcalend-{year}-{month}.rst", "w") as f:

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


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: python restcalend.py ГОД МЕСЯЦ")
        sys.exit(1)
    
    year, month = int(sys.argv[1]), int(sys.argv[2])
    generate_rest_calendar(year, month)

