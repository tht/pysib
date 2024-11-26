import can
import asyncio

from .message import Message

class SIBManager:
    def __init__(self, channel, bitrate, physical_address, interface="socketcan", host=None, port=None, receive_own_messages=False):
        """
        Initialize the SIB Manager with a CAN bus.
        """
        self.channel = channel
        self.bitrate = bitrate
        self.interface = interface
        self.host = host
        self.port = port
        self.receive_own_messages = receive_own_messages

        # Store the physical address
        self.line, self.device = physical_address
        if not ('a' <= self.line <= 'd' and 0 <= self.device < 64):  # Validate PA values
            raise ValueError("Invalid physical address. Line must be a-d and device must be 0-63.")

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

    def _get_sender_pa(self):
        """
        Calculate the 8-bit sender physical address (PA) from line and device.
        :return: An 8-bit integer representing the PA.
        """
        line_num = ord(self.line) - ord('a')
        return (line_num << 6) | self.device

    async def send(self, ta, data, prio=1):
        """
        Simple method for sending some data
        """
        addr1, addr2 = ta
        await self.send_msg(Message(prio, addr1, addr2, self._get_sender_pa(), data))

    async def send_msg(self, message: Message):
        """
        Send a Message object on the CAN bus.
        """
        if not self.bus:
            print("Error: CAN bus is not initialized.")
            return

        extended_id, msg = message.to_raw()

        # Create and send the CAN message
        can_message = can.Message(arbitration_id=extended_id, data=msg, is_extended_id=True)
        print(f"Sending message: {can_message}")

        # Send the message
        await self._send_message(can_message)

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