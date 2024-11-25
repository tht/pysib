class Entity:
    def __init__(self, name: str, topic_addresses: list[int]):
        self.name = name
        self.topic_addresses = topic_addresses
        self.state = None

    def update_state(self, data: bytes):
        """Update the state of the entity."""
        self.state = data

class Device:
    def __init__(self, physical_address: int):
        self.physical_address = physical_address
        self.entities = {}

    def add_entity(self, entity: Entity):
        """Add an entity to the device."""
        self.entities[entity.name] = entity

    def handle_message(self, message: dict):
        """Route a message to the appropriate entity."""
        for entity in self.entities.values():
            if message['topic_address'] in entity.topic_addresses:
                entity.update_state(message['data'])