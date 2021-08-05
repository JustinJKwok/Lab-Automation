from typing import Optional, Tuple, Union
import serial

from .device import ArduinoSerialDevice


class HeatingStage(ArduinoSerialDevice):
    def __init__(
            self, 
            name: str,  
            port: str, 
            baudrate: int, 
            timeout: Optional[float] = 1.0, 
            heating_timeout: float = 600.0):

        super().__init__(name, port, baudrate, timeout)
        self._heating_timeout = heating_timeout

    def initialize(self) -> Tuple[bool, str]:
        self._is_initialized = True
        was_set, comment = self.set_settemp(26.0)

        if not was_set:
            self._is_initialized = False
            return (was_set, comment)

        was_turned_on, comment = self.pid_on()

        if not was_turned_on:
            self._is_initialized = False
            return (was_turned_on, comment)

        return (True, "Heating stage successfully initialized by setting to 26 C and turning PID ON.")

    def deinitialize(self, reset_init_flag: bool = True) -> Tuple[bool, str]:
        self._is_initialized = True
        was_set, comment = self.set_settemp(24.0)

        if not was_set:
            self._is_initialized = False
            return (was_set, comment)

        was_turned_off, comment = self.pid_off()

        if not was_turned_off:
            self._is_initialized = False
            return (was_turned_off, comment)

        if reset_init_flag:
            self._is_initialized = False

        return (True, "Heating stage successfully deinitialized by setting to 24 C and turning PID OFF.")

    def set_settemp(self, temp: float) -> Tuple[bool, str]:
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + " is not open. ")
        elif not self._is_initialized:
            return (False, "Heating stage is not initialized.")
        else:
            command = ">set Ts " + str(temp) +"\n"
            self.ser.write(command.encode('ascii'))
            return self.check_ack_succ()


    def set_temp(self, temp: float) -> Tuple[bool, str]:
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + " is not open. ")
        elif not self._is_initialized:
            return (False, "Heating stage is not initialized.")
        else:
            command = ">set T " + str(temp) +"\n"
            self.ser.write(command.encode('ascii'))
            return self.check_ack_succ(ack_timeout=1.0, succ_timeout=self._heating_timeout)

    def pid_on(self) -> Tuple[bool, str]:
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + " is not open. ")
        elif not self._is_initialized:
            return (False, "Heating stage is not initialized.")
        else:
            command = ">pidon\n"
            self.ser.write(command.encode('ascii'))
            return self.check_ack_succ()

    def pid_off(self) -> Tuple[bool, str]:
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + " is not open. ")
        else:
            command = ">pidoff\n"
            self.ser.write(command.encode('ascii'))
            return self.check_ack_succ()
    
    def is_pid_on(self) -> Tuple[bool, Union[bool, str]]:
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + " is not open. ")
        else:
            command = ">pr pid\n"
            self.ser.write(command.encode('ascii'))
            was_successful, comment = self.check_ack_succ()

            if not was_successful:
                return (was_successful, comment)

            has_on_off, pid_state = super().parse_equal_sign(comment)

            if not has_on_off:
                return (has_on_off, "Message from device did not contain PID state.")

            if pid_state == "ON":
                is_on = True
            else:
                is_on = False

            return (True, is_on)

    def temperature(self) -> Tuple[bool, Union[float, str]]:
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + " is not open. ")
        else:
            command = ">pr T\n"
            self.ser.write(command.encode('ascii'))
            was_successful, comment = self.check_ack_succ()

            if not was_successful:
                return (was_successful, comment)

            has_temperature, temperature_str = super().parse_equal_sign(comment)

            if not has_temperature:
                return (has_temperature, "Message from device did not contain temperature.")
            
            return (True, float(temperature_str))



    
