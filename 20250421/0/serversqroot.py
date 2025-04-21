import asyncio

from sqroot import sqroots


async def handle(reader, writer):
    try:
        while data := await reader.readline():
            line = data.decode().strip()
            try:
                result = sqroots(line)
            except Exception:
                result = ""
            writer.write((result + "\n").encode())
            await writer.drain()
    except Exception:
        pass
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle, "0.0.0.0", 1337)
    print("Сервер запущен на порту 1337")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())