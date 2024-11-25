import can
import asyncio

class CANInterface:
    def __init__(self, channel: str, bitrate: int):
        self.bus = can.Bus(channel=channel, bustype='socketcan', bitrate=bitrate)
        self.listeners = []
        self.notifier = None

    async def start(self):
        """Start listening on the CAN bus."""
        loop = asyncio.get_running_loop()
        self.notifier = can.Notifier(self.bus, [self._handle_message], loop=loop)

    async def stop(self):
        """Stop listening and cleanup."""
        if self.notifier:
            self.notifier.stop()
        self.bus.shutdown()

    def add_listener(self, listener):
        """Add a listener callback for incoming messages."""
        self.listeners.append(listener)

    def _handle_message(self, msg: can.Message):
        """Internal callback for handling received messages."""
        for listener in self.listeners:
            listener(msg)

    async def send(self, extended_id: int, data: bytes):
        """Send a CAN message."""
        msg = can.Message(arbitration_id=extended_id, data=data, is_extended_id=True)
        await asyncio.to_thread(self.bus.send, msg)