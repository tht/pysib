import asyncio
import sys
import os

# Add the correct parent directory of the sib package to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from sib import SIBManager, DeviceType, Device, Entity

async def main():
    manager = SIBManager(
        physical_address=('b', 50),
        device_type=DeviceType.DEBUGGING,  # Specify the device type
        hw_revision="1.0",         # Hardware revision
        sw_revision="1.1",         # Software revision
        short_identifier="ABCDE",  # 5-byte short identifier
        channel="can0",            # Your CAN channel
        bitrate=500000,             # Your CAN bitrate
        interface="socketcand",
        host="192.168.20.103",
        port="29536",
        receive_own_messages=False
    )

    # Start the manager (this will start the notifier for receiving messages)
    await manager.start()

    # Send a test message (just for demonstration)
    await manager.send(ta=(1, 2), data=b'\x01', prio=1)

    # Keep the event loop running
    while True:
        await asyncio.sleep(1)

# Run the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
