from .device import Device

class Dispatcher:
    def __init__(self):
        self.devices = {}

    def register_device(self, device: Device):
        """Register a device for handling messages."""
        self.devices[device.physical_address] = device

    def dispatch(self, message: dict):
        """Dispatch messages to devices or entities."""
        sender_pa = message["sender_pa"]
        if sender_pa in self.devices:
            self.devices[sender_pa].handle_message(message)