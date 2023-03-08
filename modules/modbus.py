import traceback
import logging
from pymodbus.client import ModbusSerialClient
from . import ui_manager


class ModbusRTUClient ():
    client = None
    errors_count = 0
    max_errors = 5
    ui = None

    def init(self, mb_params):

        self.client = ModbusSerialClient(
            port=mb_params['port'],
            baudrate=mb_params['baudrate'],
            bytesize=mb_params['bytesize'],
            parity=mb_params['parity'],
            stopbits=mb_params['stopbits']
        )

    def connect(self):
        self.client.connect()
        if self.client.connected:
            return True
        else:
            return False

    def disconnect(self):
        self.client.close()

    def read_holding(self, slave_id, reg_address):
        # print('Читаю: {}, {}'.format(slave_id, reg_address))
        try:
            data = self.client.read_holding_registers(
                address=reg_address, slave=slave_id)
        except Exception as e:
            logging.error(traceback.format_exc())

        try:
            value = data.registers
            self.errors_count = 0
        except:
            value = 'error'
            self.ui.write_log(
                'Не смог прочитать регистр: {}, {}'.format(slave_id, reg_address))
            self.errors_count += 1
            if (self.errors_count == self.max_errors):
                self.ui.write_log(
                    'Не смог прочитать {} регистров подряд и остановил работу.'.format(self.errors_count))
                self.errors_count = 0
                value = 'fatal_error'
                return value

        # print('Результат: {}'.format(value))
        return value

    def write_holding(self, slave_id, reg_address, value):
        try:
            print('Пишу: {}, {} = value: {}'.format(
                slave_id, reg_address, value))
            self.client.write_register(
                address=reg_address, slave=slave_id, value=int(value))
            res = 'ok'
        except Exception as e:
            logging.error(traceback.format_exc())
            res = 'error'
            self.ui.write_log('Не смог записать регистр: {}, {}.'.format(
                slave_id, reg_address))

        return res
