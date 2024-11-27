import can
import asyncio
from enum import Enum

from .message import Message, MessageMode

class DeviceType(Enum):
    SENSOR = 0
    ACTUATOR = 1
    CONTROLLER = 2
    OTHER = 3
    DEBUGGING = 4
    HA_INTERFACE = 5
    KNX_INTERFACE = 6
    PROTOTYPE_BOARD = 7

    @classmethod
    def from_number(cls, number):
        for member in cls:
            if member.value == number:
                return member
        raise ValueError(f"Invalid device type number: {number}")

    @classmethod
    def to_number(cls, device_type):
        return device_type.value

class SIBManager:
    def __init__(self, *, channel:str, bitrate:int, physical_address, device_type:DeviceType, hw_revision:int, sw_revision:int, short_identifier, interface="socketcan", host=None, port=None, receive_own_messages=False):
        # Initialization code (unchanged)
        self.channel = channel
        self.bitrate = bitrate
        self.interface = interface
        self.host = host
        self.port = port
        self.receive_own_messages = receive_own_messages

        self.line, self.device = physical_address
        if not ('a' <= self.line <= 'd' and 0 <= self.device < 64):
            raise ValueError("Invalid physical address. Line must be a-d and device must be 0-63.")

        # Device information
        self.device_type = device_type
        self.hw_revision = hw_revision
        self.sw_revision = sw_revision
        self.short_identifier = short_identifier
        if len(self.short_identifier) != 5:
            raise ValueError("Short identifier must be a 5-byte string.")

        self.bus = None
        self.notifier = None

    def message_received_callback(self, msg):
        """
        Callback to handle received CAN messages.
        """
        message = Message.from_raw(msg.arbitration_id, msg.data)
        print(f"Received message: {message}")

        # Check if the message is directed to this device's physical address
        if self._is_message_for_this_device(message):
            self._handle_pa_command(message)

    def _is_message_for_this_device(self, message):
        """
        Determine if the message is intended for this device's physical address.
        """
        return message.addr2 == self._get_sender_pa()

    def _handle_pa_command(self, message):
        """
        Handle commands directed to the physical address (PA) of this device.
        """
        # Extract the command type from the message
        command_type = message.data[0] >> 6  # Assuming command type is in the first two bits

        if command_type == 0b00:  # Device info query
            self._send_device_info(message.sender_pa)

    async def _send_device_info(self, requester_pa = 0, just_booted=False):
        """
        Send device information as a response to a "device info" query.
        """
        response_data = bytearray(8)
        response_data[0] = (self.device_type.value & 0xFF)
        response_data[1] = (self.hw_revision & 0xFF)
        response_data[2] = (self.sw_revision & 0xFF)
        response_data[3:8] = self.short_identifier.encode()

        await self.send_msg(Message.for_pa(
            command=0x00,
            pa=requester_pa,
            data = response_data,
            sender_pa=self._get_sender_pa()
        ))

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
        await self.send_msg(message=Message(prio, addr1, addr2, self._get_sender_pa(), data))

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
        print(f"Sending message: {message}")

        # Send the message
        await self._send_message(message=can_message)

    async def _send_message(self, *, message: can.Message):
        """
        Helper function to send a single message over the bus.
        """
        try:
            await asyncio.to_thread(self.bus.send, message)
#            print(f"Message sent: {message}")
        except Exception as e:
            print(f"Error sending message: {e}")

    async def _announce_myself(self):
        while True:
            await asyncio.sleep(10)
            await self._send_device_info()

    async def start(self):
        """
        Start the SIB manager by initializing the CAN bus and setting up listeners.
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

        # Set up the CAN bus notifier (asynchronous listener)
        self.notifier = can.Notifier(self.bus, [self.message_received_callback])

        # Announce myself on the bus
        await self._send_device_info(just_booted=True)

        asyncio.create_task(self._announce_myself())

        print("Notifier started. Listening for messages...")