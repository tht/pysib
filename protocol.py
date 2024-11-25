#import can
#
#class SIBProtocol:
#    @staticmethod
#    def encode_topic(topic_address: int, priority: int, sender_pa: int, data: bytes) -> (int, bytes):
#        """Encode a message with TA addressing."""
#        extended_id = (priority << 24) | (topic_address << 8) | sender_pa
#        return extended_id, data
#
#    @staticmethod
#    def decode_message(message: can.Message) -> dict:
#        """Decode a received CAN message."""
#        extended_id = message.arbitration_id
#        priority = (extended_id >> 24) & 0xFF
#        topic_address = (extended_id >> 8) & 0xFFFF
#        sender_pa = extended_id & 0xFF
#        return {
#            "priority": priority,
#            "topic_address": topic_address,
#            "sender_pa": sender_pa,
#            "data": message.data
#        }