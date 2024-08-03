import asyncio
import aiohttp
from aiohttp import web
import json

class NetworkCommunication:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.peers = set()
        self.app = web.Application()
        self.app.router.add_post('/message', self.handle_message)
        self.app.router.add_post('/register_peer', self.register_peer)

    async def start(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        print(f"Server started at http://{self.host}:{self.port}")

    async def register_peer(self, request):
        data = await request.json()
        peer_address = data.get('address')
        if peer_address:
            self.peers.add(peer_address)
            return web.Response(text="Peer registered successfully")
        return web.Response(text="Invalid peer data", status=400)

    async def handle_message(self, request):
        data = await request.json()
        message = data.get('message')
        if message:
            print(f"Received message: {message}")
            return web.Response(text="Message received")
        return web.Response(text="Invalid message", status=400)

    async def send_message(self, peer, message):
        async with aiohttp.ClientSession() as session:
            async with session.post(f'http://{peer}/message', json={'message': message}) as response:
                return await response.text()

    async def broadcast_message(self, message):
        tasks = []
        for peer in self.peers:
            tasks.append(self.send_message(peer, message))
        await asyncio.gather(*tasks)

# Example usage
async def main():
    net_comm = NetworkCommunication()
    await net_comm.start()

    # Keep the server running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())