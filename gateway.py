import json
import time
import threading
from pymodbus import pymodbus_apply_logging_config
from pymodbus.client import (
    ModbusSerialClient,
    ModbusTcpClient,
)
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ExceptionResponse
from pymodbus.transaction import (
    ModbusRtuFramer,
    ModbusSocketFramer,
)
def display_menu(title, options):
    print(title + ":")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    return input(f"Select {title.split(' ')[-1]} (or 'q' to quit): ")

"""def display_data_details(data, protocol, device, task, data_name):
    device_data = data["Protocol"][protocol][device]  # Add this line to access device-level info
    task_data = data["Protocol"][protocol][device]["tasks"][task]
    print(f"UnitID (SlaveID): {device_data.get('unitID')}")  # Access UnitID from device_data
    print(f"Protocol: {protocol}")
    print(f"Function Name: {task}")
    for item in task_data.values():
        if item["Data_Name"] == data_name:
            print(f"StartAddress: {item.get('StartAddress', 'N/A')}")
            print(f"Wordlength: {item.get('WordLength', 'N/A')}")  # Access Wordlength from device_data
            print(f"DataValue: {item.get('DataValue')}")
            print(f"DataType: {item.get('DataType', 'N/A')}")
            print(f"Multiplier: {item.get('Multiplier', 'N/A')}")"""

def modbus_setup(data, protocol, device):
    device_data = data["Protocol"][protocol][device]
    #pymodbus_apply_logging_config("DEBUG")
    if protocol == "Modbus_TCP":
        client = ModbusTcpClient(
            host=device_data.get('Device_IP'),
            port=device_data.get('Device_Port'),
            framer=ModbusSocketFramer,
            timeout=device_data.get('minResponseTimeInSecond'),
        )
    elif protocol == "Modbus_RTU":
        client = ModbusSerialClient(
            port=device_data.get('Device_Port'),
            framer=ModbusRtuFramer,
            timeout=device_data.get('minResponseTimeInSecond'),
            baudrate=device_data.get('Baudrate'),
            bytesize=8,
            parity="N",
            stopbits=1,
        )
    else:
        print(f"Unknown protocol: {protocol}")

    if not client.connect():
        print(f"Failed to connect")
    return client

def processData(StartAddress, DataValue, DataType, Multiplier, data_name, Unit, WordLength):
    if DataType == 'int16':
        for i in range(WordLength):
            value = DataValue[i] * 10 ** Multiplier
            print(f"{data_name}{i}:{value:.2f} {Unit}")
    elif DataType == 'uint16':
        for i in range(WordLength):
            value = DataValue[0] * 10 ** Multiplier
            print(f"{data_name}:{value} {Unit}")
    elif DataType == 'bit':
        for k in range(WordLength):
            total_bits = len(DataValue) * 16  # Tính tổng số bit
            print(f"{data_name} Total: {total_bits} of {k} bit.")
            for i in range(len(DataValue)):
                byte_value = DataValue[i]
                for j in range(8):
                    bit_value = (byte_value >> j) & 0x01
                    print(f"{data_name} Bit {i * 8 + j}: {bit_value}")
    elif DataType == 'bool':
        for i in range(WordLength):
            bool_value = DataValue[i]
            print(f"{data_name}{i}: {bool_value}")
    else:
        print(f"Unsupported DataType: {DataType}")

def execute_task(data, protocol, device, task, data_name):
    device_data = data["Protocol"][protocol][device] 
    task_data = data["Protocol"][protocol][device]["tasks"][task]
    client = modbus_setup(data, protocol, device)
    unitID = device_data.get('unitID')
    for item in task_data.values():
         if item["Data_Name"] == data_name:
            StartAddress = item.get('StartAddress')
            WordLength = item.get('WordLength')
            DataValue = item.get('DataValue')
            DataType = item.get('DataType')
            Multiplier = item.get('Multiplier')
            Unit = item.get('Unit')
    if task == 'read_coils':
        try:
            response = client.read_coils(StartAddress, WordLength, unitID)
        except ModbusException as exc:
            print(f"Received ModbusException({exc}) from library")
            client.close()
            return
        if response.isError():
            print(f"Received Modbus library error({response})")
            client.close()
            return
        if isinstance(response, ExceptionResponse):  # pragma no cover
            print(f"Received Modbus library exception ({response})")
            client.close()
        if not response.isError():
            DataValue = response.bits
            processData(StartAddress, DataValue, DataType, Multiplier, data_name, Unit, WordLength)
            client.close()

    if task == 'read_discrete_inputs':
        try:
            response = client.read_discrete_inputs(StartAddress, WordLength, unitID)
        except ModbusException as exc:
            print(f"Received ModbusException({exc}) from library")
            client.close()
            return
        if response.isError():
            print(f"Received Modbus library error({response})")
            client.close()
            return
        if isinstance(response, ExceptionResponse):  # pragma no cover
            print(f"Received Modbus library exception ({response})")
            client.close()
        if not response.isError():
            DataValue = response.bits
            processData(StartAddress, DataValue, DataType, Multiplier, data_name, Unit, WordLength)
            client.close()

    if task == 'read_holding_registers':
        try:
            response = client.read_holding_registers(StartAddress, WordLength, unitID)
        except ModbusException as exc:
            print(f"Received ModbusException({exc}) from library")
            client.close()
            return
        if response.isError():
            print(f"Received Modbus library error({response})")
            client.close()
            return
        if isinstance(response, ExceptionResponse):  # pragma no cover
            print(f"Received Modbus library exception ({response})")
            client.close()
        if not response.isError():
            DataValue = response.registers
            processData(StartAddress, DataValue, DataType, Multiplier, data_name, Unit, WordLength)
            client.close()
    
    if task == 'read_input_registers':
        try:
            response = client.read_input_registers(StartAddress, WordLength, unitID)
        except ModbusException as exc:
            print(f"Received ModbusException({exc}) from library")
            client.close()
            return
        if response.isError():
            print(f"Received Modbus library error({response})")
            client.close()
            return
        if isinstance(response, ExceptionResponse):  # pragma no cover
            print(f"Received Modbus library exception ({response})")
            client.close()
        if not response.isError():
            DataValue = response.registers
            processData(StartAddress, DataValue, DataType, Multiplier, data_name, Unit, WordLength)
            client.close()

    if task == 'write_single_coil':
        if DataValue == 'input':
            DataValue = bool(input("Nhập giá trị boolean (1 hoặc 0): "))
        try:
            response = client.write_coil(StartAddress, DataValue, unitID)
        except ModbusException as exc:
            print(f"Received ModbusException({exc}) from library")
            client.close()
            return
        if response.isError():
            print(f"Received Modbus library error({response})")
            client.close()
            return
        if isinstance(response, ExceptionResponse):  # pragma no cover
            print(f"Received Modbus library exception ({response})")
            client.close()
        if not response.isError():
            print("Write successful")
            client.close()

    if task == 'write_single_register':
        if DataValue == 'input':
            DataValue == int(input("Nhập giá trị cần ghi: "))
        try:
            response = client.write_register(StartAddress, DataValue, unitID)
        except ModbusException as exc:
            print(f"Received ModbusException({exc}) from library")
            client.close()
            return
        if response.isError():
            print(f"Received Modbus library error({response})")
            client.close()
            return
        if isinstance(response, ExceptionResponse):  # pragma no cover
            print(f"Received Modbus library exception ({response})")
            client.close()
        if not response.isError():
            print("Write successful")
            client.close()

    if task == 'write_multiple_coils':
        if DataValue == 'input':
            coil_num = int(input("Enter quantity of coils: "))
            DataValue = []
            for i in range(coil_num):
                Value = bool(input(f"Enter value for coil {StartAddress + i}: "))
                DataValue.append(Value)
        try:
            response = client.write_coil(StartAddress, DataValue, unitID)
        except ModbusException as exc:
            print(f"Received ModbusException({exc}) from library")
            client.close()
            return
        if response.isError():
            print(f"Received Modbus library error({response})")
            client.close()
            return
        if isinstance(response, ExceptionResponse):  # pragma no cover
            print(f"Received Modbus library exception ({response})")
            client.close()
        if not response.isError():
            print("Write successful")
            client.close()

    if task == 'write_multiple_registers':
        if DataValue == 'input':
            WordLength = int(input("Enter quantity of coils: "))
            DataValue = []
            for i in range(WordLength):
                Value = int(input(f"Enter value for coil {StartAddress + i}: "))
                DataValue.append(Value)
        try:
            response = client.write_coil(StartAddress, DataValue, unitID)
        except ModbusException as exc:
            print(f"Received ModbusException({exc}) from library")
            client.close()
            return
        if response.isError():
            print(f"Received Modbus library error({response})")
            client.close()
            return
        if isinstance(response, ExceptionResponse):  # pragma no cover
            print(f"Received Modbus library exception ({response})")
            client.close()
        if not response.isError():
            print("Write successful")
            client.close()

def continuous_reading_thread(data, protocol, device, task, data_name):
    device_data = data["Protocol"][protocol][device]
    while reading_continuously:
        execute_task(data, protocol, device, task, data_name)
        time.sleep(device_data.get('scanningCycleInSecond'))

def main():
    global reading_continuously
    reading_continuously = False
    with open("config.json", "r") as file:
        data = json.load(file)

    while True:
        protocols = list(data["Protocol"].keys())
        protocol_choice = display_menu("Protocol List", protocols)

        if protocol_choice == 'q':
            break
        if not protocol_choice.isdigit() or int(protocol_choice) > len(protocols):
            print("Invalid selection, please select again.")
            continue
        chosen_protocol = protocols[int(protocol_choice) - 1]

        devices = list(data["Protocol"][chosen_protocol].keys())
        device_choice = display_menu("List of devices in Protocol", devices)

        if device_choice == 'q':
            continue
        if not device_choice.isdigit() or int(device_choice) > len(devices):
            print("Invalid selection, please select again.")
            continue
        chosen_device = devices[int(device_choice) - 1]

        tasks = list(data["Protocol"][chosen_protocol][chosen_device]["tasks"].keys())
        tasks_filtered = [task for task in tasks if data["Protocol"][chosen_protocol][chosen_device]["tasks"][task]]  # Filter out null tasks
        task_choice = display_menu("List of task types for the device", tasks_filtered)

        if task_choice == 'q':
            continue
        if not task_choice.isdigit() or int(task_choice) > len(tasks_filtered):
            print("Invalid selection, please select again.")
            continue
        chosen_task = tasks_filtered[int(task_choice) - 1]

        data_names = [item["Data_Name"] for item in data["Protocol"][chosen_protocol][chosen_device]["tasks"][chosen_task].values()]
        data_name_choice = display_menu("Task list", data_names)

        if data_name_choice == 'q':
            continue
        if not data_name_choice.isdigit() or int(data_name_choice) > len(data_names):
            print("Invalid selection, please select again.")
            continue
        chosen_data_name = data_names[int(data_name_choice) - 1]

        print(f"Your selection: {chosen_protocol} -> {chosen_device} -> {chosen_task} -> {chosen_data_name}")

        if chosen_task == 'read_holding_registers' or chosen_task == 'read_input_registers':
            read_options = ["Read Once", "Read Continuously", "Back"]
            read_choice = display_menu("Choose reading style", read_options)
            if read_choice == 'q':
                continue
            elif read_choice == '1':
                execute_task(data, chosen_protocol, chosen_device, chosen_task, chosen_data_name)
            elif read_choice == '2':
                reading_continuously = True
                read_thread = threading.Thread(target=continuous_reading_thread, args=(data, chosen_protocol, chosen_device, chosen_task, chosen_data_name))
                read_thread.start()

                print("Press Enter to stop continuous reading.")
                input()

                reading_continuously = False
                read_thread.join()
            elif read_choice == '3':
                continue
            else:
                print("Invalid selection, please select again.")
                continue
        else:
            execute_task(data, chosen_protocol, chosen_device, chosen_task, chosen_data_name)
        #display_data_details(data, chosen_protocol, chosen_device, chosen_task, chosen_data_name)

if __name__ == "__main__":
    main()
