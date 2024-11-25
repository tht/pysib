import asyncio
import sys
import os

# Add the correct parent directory of the sib package to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from sib import SIBManager, Device, Entity

async def main():
    manager = SIBManager(
        physical_address=('b', 50),
        channel="can0",  # Your CAN channel
        bitrate=500000,  # Your CAN bitrate
        interface="socketcand",
        host="192.168.20.103",
        port="29536",
        receive_own_messages=False
    )

    # Start the manager (this will start the notifier for receiving messages)
    await manager.start()

    # Send a test message (just for demonstration)
    #await manager.send(topic_address=0x1234, priority=1, sender_pa=0x01, data=b'\x01')

    # Keep the event loop running
    while True:
        await asyncio.sleep(1)

# Run the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())