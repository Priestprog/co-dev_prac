import asyncio

async def echo(reader, writer):
    addr = writer.get_extra_info('peername')
    while data := await reader.readline():
        message = data.decode().strip()
        if message.startswith("print "):
            response = message[6:]
            writer.write(response.encode() + b'\n')
        
        elif message.startswith("info "):  
            command = message.split()[1] 
            if command == "host":
                response = f"Host: {addr[0]}"
            elif command == "port":
                response = f"Port: {addr[1]}"
            else:
                response = "Invalid parameter for info. Use 'host' or 'port'."
            writer.write(response.encode() + b'\n')
        
        else:
            writer.write(data.swapcase())

        await writer.drain()  
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(echo, '0.0.0.0', 1337)
    async with server:
        print("Server started on 0.0.0.0:1337")
        await server.serve_forever()

asyncio.run(main())
