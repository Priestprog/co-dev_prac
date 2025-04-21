import math
import shlex
import socket

def sqroots(coeffs: str) -> str:
    try:
        parts = shlex.split(coeffs)
        if len(parts) != 3:
            raise ValueError("Неверное количество коэффициентов")

        a, b, c = map(float, parts)

        if a == 0:
            raise ValueError("Коэффициент a не должен быть равен нулю")

        D = b ** 2 - 4 * a * c

        if D < 0:
            return ""
        elif D == 0:
            x = -b / (2 * a)
            return f"{x}"
        else:
            sqrt_D = math.sqrt(D)
            x1 = (-b - sqrt_D) / (2 * a)
            x2 = (-b + sqrt_D) / (2 * a)
            return f"{min(x1, x2)} {max(x1, x2)}"

    except Exception as e:
        raise ValueError(f"Ошибка при обработке входных данных: {e}")

def sqrootnet(coeffs: str, s: socket.socket) -> str:
    s.sendall((coeffs + "\n").encode())
    return s.recv(128).decode().strip()