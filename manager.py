import can
import asyncio

from .message import Message

class SIBManager:
    def __init__(self, channel, bitrate, interface="socketcan", host=None, port=None, receive_own_messages=False):
        """
        Initialize the SIB Manager with a CAN bus.
        """
        self.channel = channel
        self.bitrate = bitrate
        self.interface = interface
        self.host = host
        self.port = port
        self.receive_own_messages = receive_own_messages
        self.bus = None
        self.notifier = None

    def _create_bus(self):
        """
        Create and initialize the CAN bus based on the interface.
        """
        try:
            if self.interface == "socketcand":
                if not self.host or not self.port:
                    raise ValueError("Host and port must be specified for socketcand interface.")
                print(f"Attempting to initialize socketcand bus with host: {self.host}, port: {self.port}")
                self.bus = can.Bus(
                    bustype="socketcand",
                    channel=self.channel,
                    host=self.host,
                    port=int(self.port),
                    receive_own_messages=self.receive_own_messages
                )
            else:
                print(f"Attempting to initialize {self.interface} bus with channel: {self.channel}")
                self.bus = can.Bus(
                    channel=self.channel,
                    bustype=self.interface,
                    bitrate=self.bitrate,
                    receive_own_messages=self.receive_own_messages
                )
            if self.bus:
                print("CAN bus initialized successfully.")
            else:
                print("Failed to initialize CAN bus.")
        except Exception as e:
            print(f"Error initializing CAN bus: {e}")
            self.bus = None

    def message_received_callback(self, msg):
        """
        Callback to log received CAN messages.
        """
        #print(f"Received message: {msg}")
        message = Message.from_raw(msg.arbitration_id, msg.data)
        print(message)
        #print(f"Arbitration ID: {msg.arbitration_id}, Data: {msg.data}")

    async def send(self, topic_address, priority, sender_pa, data):
        """
        Send a message over the CAN bus.
        """
        arbitration_id = (priority << 26) | (topic_address << 8) | sender_pa
        message = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=True)
        
        # Send the message
        await self._send_message(message)

    async def _send_message(self, message: can.Message):
        """
        Helper function to send a single message over the bus.
        """
        try:
            # Use `asyncio.to_thread` to send the message in a separate thread
            await asyncio.to_thread(self.bus.send, message)
            print(f"Message sent: {message}")
        except Exception as e:
            print(f"Error sending message: {e}")

    async def start(self):
        """
        Start the SIB manager by initializing the CAN bus and setting up listeners.
        """
        self._create_bus()  # Ensure the bus is created before starting
        if not self.bus:
            raise RuntimeError("CAN bus initialization failed.")

        # Set up the CAN bus notifier (asynchronous listener)
        self.notifier = can.Notifier(self.bus, [self.message_received_callback])

        print("Notifier started. Listening for messages...")