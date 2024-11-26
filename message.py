from enum import Enum

class Mode:
    # Define the different modes available for the messages
    HIGH_TA = 0b00  # High priority TA mode
    MEDIUM_TA = 0b01  # Medium priority TA mode
    PA = 0b10  # PA mode (Physical Address)
    LOW_TA = 0b11  # Low priority TA mode

    # Mapping of mode values to human-readable strings
    _mode_mapping = {
        HIGH_TA: "TA(High)",
        MEDIUM_TA: "TA(Med)",
        PA: "PA",
        LOW_TA: "TA(Low)",
    }

    @classmethod
    def from_value(cls, value):
        # Get the mode from a given value
        if value in cls._mode_mapping:
            return value
        else:
            raise ValueError(f"Invalid mode value: {value}")

    @classmethod
    def to_string(cls, value):
        # Convert the mode value to its string representation
        return cls._mode_mapping.get(value, "Unknown")

    @classmethod
    def from_string(cls, string):
        # Get the mode value from its string representation
        for key, val in cls._mode_mapping.items():
            if val == string:
                return key
        raise ValueError(f"Invalid mode string: {string}")

class Message:
    def __init__(self, mode: int, addr1, addr2, sender_pa: int, data=b''):
        # Initialize a Message object with mode, addresses, sender PA, and data
        self.mode = Mode.from_value(mode)
        self.addr1 = addr1
        self.addr2 = addr2
        self.sender_pa = sender_pa
        self.data = data

    @classmethod
    def for_ta(cls, prio="Medium", ta=None, data=None, sender_pa=None):
        # Create a TA mode message with specified priority, TA, data, and sender PA
        addr1, addr2 = ta
        mode = {
            "High": Mode.HIGH_TA,
            "Medium": Mode.MEDIUM_TA,
            "Low": Mode.LOW_TA,
        }.get(prio, Mode.MEDIUM_TA)
        
        return cls(
            mode=mode,
            addr1=addr1,
            addr2=addr2,
            sender_pa=sender_pa,
            data=data
        )

    @classmethod
    def for_pa(cls, command=0, pa=None, data=None, sender_pa=None):
        # Create a PA mode message with specified command, PA, data, and sender PA
        return cls(
            mode=Mode.PA,
            addr1=command,
            addr2=pa,
            sender_pa=sender_pa,
            data=data
        )

    @classmethod
    def from_raw(cls, extended_id: int, data: bytes):
        # Parse a raw CAN message into a Message object
        mode = Mode.from_value((extended_id >> 27) & 0b11)
        sender_pa = extended_id & 0xFF

        if mode in (Mode.HIGH_TA, Mode.MEDIUM_TA, Mode.LOW_TA):
            addr1 = (extended_id >> 24) & 0b111  # Main TA
            addr2 = (extended_id >> 16) & 0xFF  # Sub TA
        elif mode == Mode.PA:
            addr1 = (extended_id >> 24) & 0b111  # Command
            addr2 = (extended_id >> 16) & 0xFF  # PA

        return cls(mode, addr1, addr2, sender_pa, data)

    def to_raw(self) -> (int, bytes):
        # Encode the Message object as raw CAN data
        extended_id = (self.mode << 27)

        if self.mode in (Mode.HIGH_TA, Mode.MEDIUM_TA, Mode.LOW_TA):
            extended_id |= (self.addr1 << 24) | (self.addr2 << 16)
        elif self.mode == Mode.PA:
            extended_id |= (self.addr1 << 24) | (self.addr2 << 16)

        extended_id |= self.sender_pa
        return extended_id, self.data

    def _get_sender_pa(self):
        # Get the sender PA in a specific string format
        return f"{chr((self.sender_pa >> 6) + ord('a'))}{self.sender_pa & 0x3F:02}"

    def __repr__(self):
        # Return a string representation of the Message object
        mode_str = Mode.to_string(self.mode)
        addr_repr = f"command={self.addr1}, target_pa={self.addr2}" if self.mode == Mode.PA else f"{self.addr1}:{self.addr2}"
        return (
            f"Message(mode={mode_str}, target={addr_repr}, sender={self._get_sender_pa()}, data={self.data})"
        )
