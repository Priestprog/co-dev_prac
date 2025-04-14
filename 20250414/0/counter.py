while True:
    try:
        line = input()
        words = line.split()
        count = len(words)
        print(f"Entered {count} word(s)")
    except KeyboardInterrupt:
        print("\nEXIT")
        break
