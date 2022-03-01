from typing import Optional, Tuple, Union
import serial

from .device import ArduinoSerialDevice

class Sonicator(ArduinoSerialDevice):
    def __init__(
            self,
            name : str,
            port : str,
            baudrate : int,
            timeout : Optional[float] = 1.0,
            operation_timeout : float = 30.0):

        super().__init__(name, port, baudrate, timeout)
        self._operation_timeout = operation_timeout
        self._powered = False

    def initialize(self):
        if not self.ser.is_open:
            return(False, "Serial port " + self._port + "is not open. ")

        self._powered, comment = self.check_power()
        if not self._powered:
            return (self._powered, comment)

        command = ">turnoff\n"
        self.ser.write(command.encode('ascii'))
        turned_off, comment2 = self.check_sonicator('status', response_best='SAF', response_ok='STF', response_notok='ERR')
        if not turned_off:
            return (turned_off, comment2)

        self._is_initialized = True
        return (True, "Sonicator is on and is ready. ")

    def deinitialize(self) -> Tuple[bool, str]:
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + "is not open. ")

        power_on, comment = self.check_power()
        if not power_on:
            return (power_on, comment)

        turned_off, comment2 = self.stop_sonicating()
        if not turned_off:
            return (turned_off, comment2)

        self._is_initialized = False
        return (True, "Sonicator is successfully deinitialized. ")


    def check_power(self) -> Tuple[bool, str]:
        if not self.ser.is_open:
            return(False, "Serial port " + self._port + "is not open. ")

        command = ">power\n"
        self.ser.write(command.encode('ascii'))
        self._powered, comment = self.check_sonicator('power', response_best = 'PIO', response_ok='PIO', response_notok = 'PNO')
        return (self._powered, comment)

    def check_status(self) -> Tuple[bool, str]:
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + "is not open. ")
        elif not self._powered:
            return (False, "Sonicator is not connected to the power supply.")
        elif not self._is_initialized:
            return (False, "Sonicator is not initiated. ")

        command = ">status\n"
        self.ser.write(command.encode('ascii'))
        return self.check_sonicator('status', response_best = 'SIW', response_ok = 'SNW', response_notok= 'ERR')

    def start_sonicating(self) -> Tuple[bool, str]:
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + "is not open. ")
        elif not self._powered:
            return (False, "Sonicator is not connected to the power supply.")
        elif not self._is_initialized:
            return (False, "Sonicator is not initiated. ")

        command = ">turnon\n"
        self.ser.write(command.encode('ascii'))
        return self.check_sonicator('turnon', response_best='SAN', response_ok='STN', response_notok= 'ERR')

    def stop_sonicating(self) -> Tuple[bool, str]:
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + "is not open. ")
        elif not self._powered:
            return (False, "Sonicator is not connected to the power supply.")
        elif not self._is_initialized:
            return (False, "Sonicator is not initiated. ")

        command = ">turnoff\n"
        self.ser.write(command.encode('ascii'))
        return self.check_sonicator('turnoff', response_best='SAF', response_ok='STF', response_notok='ERR')

    def pressbutton(self) -> Tuple[bool, str]:
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + "is not open. ")
        elif not self._powered:
            return (False, "Sonicator is not connected to the power supply.")
        elif not self._is_initialized:
            return (False, "Sonicator is not initiated. ")

        command = ">button\n"
        self.ser.write(command.encode('ascii'))
        return self.check_sonicator('status', response_best='BIP')

    def check_sonicator(self, command: str, response_best: str, response_ok: str,
                        response_notok: str, response_timeout: float = 1.0) -> Tuple[bool, str]:
        if not self.ser.is_open:
            return(False, "Serial port " + self._port + "is not open. ")

        retry_count = 0
        partial_retries = self.partial_timeout // self.timeout
        response_retries = response_timeout // self.timeout

        if response_retries < 1 :
            response_retries = 1

        # using integer retries of period self.timeout, this is because changing ser.timeout directly causes problems
        response_result = b''
        while response_result.decode('ascii') == "" and retry_count < response_retries:
            response_result = self.ser.readline()
            retry_count += 1

        # https://stackoverflow.com/questions/61166544/readline-in-pyserial-sometimes-captures-incomplete-values-being-streamed-from
        # in case readline times out in the middle of a message before \n
        retry_count = 0
        while response_result.decode('ascii') == "" and "\\n" not in str(response_result) and retry_count < partial_retries:
            temp_result = self.ser.readline()
            retry_count += 1
            if not not temp_result.decode('ascii'):
                response_result = (response_result.decode('ascii') + temp_result.decode('ascii')).encode('ascii')

        if retry_count == partial_retries and "\\n" not in str(response_result):
            return (False, "Timed out. Partial message received from control command " + command + ".")

        response_result = response_result.strip().decode('ascii')

        if response_result == "":
            return (False, "Timed out. Did not receive any response from command " + command + ".")
        elif response_result == response_best:
            return (True, "Successfully received message : " + self.msgdict[response_best] + "from command " + command + ".")
        elif response_result == response_ok:
            return (True, "Successfully received message : " + self.msgdict[response_ok] + "from command " + command + ".")
        elif response_result == response_notok:
            return (False, "Sonicator failure. Received message : " + self.msgdict[response_notok] + "from command " + command + ".")
        elif response_result in self.msgdict:
            return (False, "Did not receive the predicted response " + response_best + ". Instead received : " + response_result + " with message : " + self.msgdict[response_result] + "from command " + command + ".")
        else :
            return (False, "Received message code : " + response_result + "from command" + command + ".")





    msgdict = { 'SIW' : 'Sonicator is currently sonicating. ',
                'SNW' : 'Sonicator is currently not sonicating. ',
                'BIP' : 'Pressed Sonicator button.',
                'PIO' : 'Sonicator is connected to the power supply. ',
                'PNO' : 'Sonicator is not connected to the power supply. ',
                'SAN' : 'Turned on the sonicator. It was already in motion. ',
                'STN' : 'Turned on the sonicator. ',
                'SAF' : 'Turned off the sonicator. It was already not in motion. ',
                'STF' : 'Turned off the sonicator. ',
                'INV' : 'Invalid command. Please check the command. ',
                'ERR' : 'Response Error. Please check. '
               }