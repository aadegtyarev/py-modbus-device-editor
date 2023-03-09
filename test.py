# import asyncio
import time
from pymodbus.client import ModbusSerialClient
import serial

client = ModbusSerialClient(
    port='/dev/ttyACM0',
    baudrate=9600,
    bytesize=8,
    parity='N',
    stopbits=2
)

connect = client.connect()

print('connect {}'.format(connect))


def read_holding(slave_id, reg_address):
    try:
        data = client.read_holding_registers(
            address=reg_address, slave=slave_id)
        value = data.registers
    except Exception as e:
        msg = '%s' % e.args
        if ('ModbusIOException' in msg):
            raise Exception(
                'Не смог подключиться к устройству.')
        if ('ExceptionResponse' in msg):
            raise Exception(
                'Не смог прочитать регистр {}.'.format(reg_address))

    return value


def write_holding(slave_id, reg_address, value):
    try:
        res = client.write_register(
            address=reg_address, slave=slave_id, value=int(value))

        if ('IllegalValue' in '%s' % res):
            raise Exception('Не смог записать регистр {}.'.format(
                reg_address))
        if ('Invalid Message' in '%s' % res):
            raise Exception(
                'Не смог подключиться к устройству.')
    except Exception as e:
        raise Exception(e)

    return ('WriteRegisterResponse' in '%s' % res)


try:
    data = write_holding(6, 65535, 69)
    print('result: {}'.format(data))
except Exception as ex:
    print(ex)
