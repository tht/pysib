class Message:
    def __init__(self, extended_id: int, data: bytes):
        self.priority = (extended_id >> 24) & 0xFF
        self.topic_address = (extended_id >> 8) & 0xFFFF
        self.sender_pa = extended_id & 0xFF
        self.data = data

    @classmethod
    def from_raw(cls, extended_id: int, data: bytes):
        """Create a Message from raw CAN data."""
        return cls(extended_id, data)

    def to_raw(self) -> (int, bytes):
        """Convert the Message to raw CAN data."""
        extended_id = (self.priority << 24) | (self.topic_address << 8) | self.sender_pa
        return extended_id, self.data

    def __repr__(self):
        return (
            f"Message(priority={self.priority}, "
            f"topic_address={hex(self.topic_address)}, "
            f"sender_pa={hex(self.sender_pa)}, data={self.data})"
        )