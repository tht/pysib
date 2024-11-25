class Message:
    def __init__(self, mode: int, addr1, addr2, sender_pa: int, data=b''):
        """
        Initialize a Message object.
        :param mode: 2-bit mode (TA or PA modes).
        :param addr1: 3 bits - Main TA in TA-Mode or Command in PA-Mode.
        :param addr2: 8 bits - Sub TA in TA-Mode or PA in PA-Mode.
        :param sender_pa: Sender physical address (8-bit value).
        :param data: Message payload (bytes).
        """
        self.mode = mode
        self.addr1 = addr1
        self.addr2 = addr2
        self.sender_pa = sender_pa
        self.data = data

    @classmethod
    def for_ta(cls, prio=1, ta=None, data=None, sender_pa=None):
        addr1, addr2 = ta
        return cls(
            mode=prio,
            addr1=addr1,
            addr2=addr2,
            sender_pa=sender_pa
        )

    @classmethod
    def for_pa(cls, prio=1, command=0, pa=None, data=None, sender=None):
        addr1, addr2 = ta
        return cls(
            mode=b10,
            addr1=command,
            addr2=pa,
            sender_pa=sender_pa
        )

    @classmethod
    def from_raw(cls, extended_id: int, data: bytes):
        """Parse a raw CAN message."""
        mode = (extended_id >> 27) & 0b11
        sender_pa = extended_id & 0xFF
        main_ta = sub_ta = command = target_pa = None

        if mode in (0b00, 0b01, 0b11):  # TA modes
            addr1 = (extended_id >> 24) & 0b111 # Main TA
            addr2 = (extended_id >> 16) & 0xFF  # Sub TA
        elif mode == 0b10:  # PA mode
            addr1 = (extended_id >> 24) & 0b111 # Command
            addr2 = (extended_id >> 16) & 0xFF  # PA

        return cls(mode, addr1, addr2, sender_pa, data)

    def to_raw(self) -> (int, bytes):
        """Encode the Message object as raw CAN data."""
        extended_id = (self.mode << 27)

        if self.mode in (0b00, 0b01, 0b11):  # TA modes
            if self.main_ta is None or self.sub_ta is None:
                raise ValueError("main_ta and sub_ta must be provided in TA modes.")
            extended_id |= (self.main_ta << 24) | (self.sub_ta << 16)
        elif self.mode == 0b10:  # PA mode
            if self.command is None or self.target_pa is None:
                raise ValueError("command and target_pa must be provided in PA mode.")
            extended_id |= (self.command << 24) | (self.target_pa << 16)

        extended_id |= self.sender_pa
        return extended_id, self.data

    def _get_sender_pa(self):
        return f"{chr((self.sender_pa >> 6) + ord('a'))}{self.sender_pa & 0x3F:02}"

    def __repr__(self):
        if self.mode in (0b00, 0b01, 0b11):  # TA modes
            return (
                f"Message(mode=TA, priority={bin(self.mode)}, "
                f"ta={self.addr1}:{self.addr2}, "
                f"sender_pa={self._get_sender_pa()}, data={self.data})"
            )
        elif self.mode == 0b10:  # PA mode
            return (
                f"Message(mode=PA, priority={bin(self.mode)}, "
                f"command={self.addr1}, target_pa={self.addr2}, "
                f"sender_pa={self._get_sender_pa()}, data={self.data})" #TODO: Rewrite sender_pa in x01 format
            )
        else:
            return f"Message(mode=Unknown, extended_id={self.extended_id}, data={self.data})"