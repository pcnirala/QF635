import zmq.asyncio

from MarketDataSource import *


class MessageBroker:
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

        # ZeroMQ sockets
        context = zmq.asyncio.Context()
        self._xsub_socket = context.socket(zmq.XSUB)
        self._xsub_socket.bind(Config.MessageBroker.XSubSocketAddr)  # PUBs connect here

        self._xpub_socket = context.socket(zmq.XPUB)
        self._xpub_socket.bind(Config.MessageBroker.XPubSocketAddr)  # SUBs connect here

    async def run(self):

        poller = zmq.asyncio.Poller()
        poller.register(self._xsub_socket, zmq.POLLIN)
        poller.register(self._xpub_socket, zmq.POLLIN)

        while True:
            events = dict(await poller.poll())
            if self._xsub_socket in events:
                msg = await self._xsub_socket.recv_multipart()
                await self._xpub_socket.send_multipart(msg)
            if self._xpub_socket in events:
                msg = await self._xpub_socket.recv_multipart()
                await self._xsub_socket.send_multipart(msg)
