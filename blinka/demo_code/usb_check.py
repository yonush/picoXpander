import hid

print("List the current USB devices")
for device_dict in hid.enumerate():
    keys = list(device_dict.keys())
    keys.sort()
    for key in keys:
        print(f"{key}, {device_dict[key]}")
    print()

"""
Example output for the Pico with the xpander version of the firmware installed
    bus_type, 1
    interface_number, 2
    manufacturer_string, Pico
    path, b'\\\\?\\HID#VID_CAFE&PID_4005&MI_02#a&2277f00f&0&0000#{4d1e55b2-f16f-11cf-88cb-001111000030}'
    product_id, 16389
    product_string, picoXpander
    release_number, 256
    serial_number, 0xE660C0D1C73D5E39
    usage, 1
    usage_page, 65280
    vendor_id, 51966
"""

print("-" * 40)  # spacer

print("Opening a connection to the Raspberry Pico")
dev = hid.device()
try:
    dev.open(0xCAFE, 0x4005)  # Raspberry Pico devices
    print(f"Manufacturer: {dev.get_manufacturer_string()}")
    print(f"Product: {dev.get_product_string()}")
    print(f"Serial No: {dev.get_serial_number_string()}")
except:
    print("-- Unable to open the Raspberry Pico device - exiting")
    exit()
finally:
    print("Closing the Raspberry Pico device device")
    dev.close()
