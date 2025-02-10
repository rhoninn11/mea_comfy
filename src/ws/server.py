

import asyncio

from websockets.asyncio.server import serve

async def logic(websockets):
    async for message in websockets:
        # is this echo
        print(f'+++ recived message: {message}')
        await websockets.send(message)


async def main():
    async with serve(logic, "0.0.0.0", 8765) as server:
        print("+++ websocket server started")
        await server.serve_forever()


asyncio.run(main())