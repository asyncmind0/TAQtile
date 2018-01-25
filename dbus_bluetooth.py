from __future__ import absolute_import, print_function, unicode_literals
import dbus
from pprint import pprint

def extract_objects(object_list):
    list = ""
    for object in object_list:
        val = str(object)
        list = list + val[val.rfind("/") + 1:] + " "
    return list

def extract_uuids(uuid_list):
    list = ""
    for uuid in uuid_list:
        if (uuid.endswith("-0000-1000-8000-00805f9b34fb")):
            if (uuid.startswith("0000")):
                val = "0x" + uuid[4:8]
            else:
                val = "0x" + uuid[0:8]
        else:
            val = str(uuid)
        list = list + val + " "
    return list


def get_devices():
    bus = dbus.SystemBus()

    manager = dbus.Interface(bus.get_object("org.bluez", "/"),
                                "org.freedesktop.DBus.ObjectManager")
    objects = manager.GetManagedObjects()
    all_devices = (str(path) for path, interfaces in objects.items() if
                    "org.bluez.Device1" in interfaces.keys())
    DEVICES = {}
    for path, interfaces in objects.items():
        if "org.bluez.Adapter1" not in interfaces.keys():
            continue
        device = DEVICES.setdefault(str(path), {})
        properties = interfaces["org.bluez.Adapter1"]
        for key in properties.keys():
            value = properties[str(key)]
            if (key == "UUIDs"):
                list = extract_uuids(value)
                device[str(key)] = list
            else:
                device[str(key)] = value

        device_list = [d for d in all_devices if d.startswith(path + "/")]

        for dev_path in device_list:
            paired = device.setdefault('devices', {})
            pair = paired.setdefault(dev_path, {})
            dev = objects[dev_path]
            properties = dev["org.bluez.Device1"]
            for key in properties.keys():
                value = properties[str(key)]
                if (key == "UUIDs"):
                    list = extract_uuids(value)
                    pair[str(key)] = list
                else:
                    pair[str(key)] = value
    return DEVICES
