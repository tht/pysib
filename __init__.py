"""
Smart Integration Bus (SIB) Python Library
==========================================

A library for interacting with SIB protocol over a CAN bus. Provides tools for
message encoding/decoding, device and entity management, and asynchronous communication.
"""

# Import key components
from .manager import SIBManager
from .can_interface import CANInterface
#from .protocol import SIBProtocol
from .device import Device, Entity
from .dispatcher import Dispatcher
from .message import Message

# Version of the library
__version__ = "0.1.0"

# Define the public API
__all__ = [
    "SIBManager",
    "CANInterface",
    "SIBProtocol",
    "Device",
    "Entity",
    "Dispatcher",
    "Message"
]