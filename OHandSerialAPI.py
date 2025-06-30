import time
import can_communication as can_comm

MAX_MOTOR_CNT = 6
MAX_THUMB_ROOT_POS = 3
MAX_FORCE_ENTRIES = 5 * 12

# Constants from the C header file
HAND_PROTOCOL_UART = 0
HAND_PROTOCOL_I2C = 1

# Error codes
ERR_PROTOCOL_WRONG_LRC = 0x01
ERR_COMMAND_INVALID = 0x11
ERR_COMMAND_INVALID_BYTE_COUNT = 0x12
ERR_COMMAND_INVALID_DATA = 0x13
ERR_STATUS_INIT = 0x21
ERR_STATUS_CALI = 0x22
ERR_STATUS_STUCK = 0x23
ERR_OP_FAILED = 0x31
ERR_SAVE_FAILED = 0x32


# API return values
HAND_RESP_HAND_ERROR = 0xFF  # device error, error call back will be called with OHand error codes listed above
HAND_RESP_SUCCESS = 0x00
HAND_RESP_TIMER_FUNC_NOT_SET = 0x01  # local error, timer function not set, call HAND_SetTimerFunction(...) first
HAND_RESP_INVALID_CONTEXT = 0x02  # local error, invalid context, NULL or send data function not set
HAND_RESP_TIMEOUT = 0x03  # local error, time out when waiting node response
HAND_RESP_INVALID_OUT_BUFFER_SIZE = 0x04  # local error, out buffer size not matched to returned data
HAND_RESP_UNMATCHED_ADDR = 0x05  # local error, unmatched node id between returned and waiting
HAND_RESP_UNMATCHED_CMD = 0x06  # local error, unmatched command between returned and waiting
HAND_RESP_DATA_SIZE_TOO_BIG = 0x07  # local error, size of data to send exceeds the buffer size
HAND_RESP_DATA_INVALID = 0x08  # local error, data content invalid

# Sub-commands for HAND_CMD_SET_CUSTOM
SUB_CMD_SET_SPEED = 1 << 0
SUB_CMD_SET_POS = 1 << 1
SUB_CMD_SET_ANGLE = 1 << 2
SUB_CMD_GET_POS = 1 << 3
SUB_CMD_GET_ANGLE = 1 << 4
SUB_CMD_GET_CURRENT = 1 << 5
SUB_CMD_GET_FORCE = 1 << 6
SUB_CMD_GET_STATUS = 1 << 7

# Command definitions

# Chief GET commands
HAND_CMD_GET_PROTOCOL_VERSION = 0x00  # Get protocol version, Please don't modify!
HAND_CMD_GET_FW_VERSION = 0x01  # Get firmware version
HAND_CMD_GET_HW_VERSION = 0x02  # Get hardware version, [HW_TYPE, HW_VER, BOOT_VER_MAJOR, BOOT_VER_MINOR]
HAND_CMD_GET_CALI_DATA = 0x03  # Get calibration data
HAND_CMD_GET_FINGER_PID = 0x04  # Get PID of finger
HAND_CMD_GET_FINGER_CURRENT_LIMIT = 0x05  # Get motor current limit of finger
HAND_CMD_GET_FINGER_CURRENT = 0x06  # Get motor current of finger
HAND_CMD_GET_FINGER_FORCE_TARGET = 0x07  # Get force limit of finger
HAND_CMD_GET_FINGER_FORCE = 0x08  # Get force of finger
HAND_CMD_GET_FINGER_POS_LIMIT = 0x09  # Get absolute position limit of finger
HAND_CMD_GET_FINGER_POS_ABS = 0x0A  # Get current absolute position of finger
HAND_CMD_GET_FINGER_POS = 0x0B  # Get current logical position of finger
HAND_CMD_GET_FINGER_ANGLE = 0x0C  # Get first joint angle of finger
HAND_CMD_GET_THUMB_ROOT_POS = 0x0D  # Get preset position of thumb root, [0, 1, 2, 255], 255 as invalid
HAND_CMD_GET_FINGER_POS_ABS_ALL = 0x0E  # Get current absolute position of all fingers
HAND_CMD_GET_FINGER_POS_ALL = 0x0F  # Get current logical position of all fingers
HAND_CMD_GET_FINGER_ANGLE_ALL = 0x10  # Get first joint angle of all fingers
HAND_CMD_GET_FINGER_STOP_PARAMS = 0x11  # Get finger finger stop parametres
HAND_CMD_GET_FINGER_FORCE_PID = 0x12  # Get finger force PID

# Auxiliary GET commands
HAND_CMD_GET_SELF_TEST_LEVEL = 0x20  # Get self-test level state
HAND_CMD_GET_BEEP_SWITCH = 0x21  # Get beep switch state
HAND_CMD_GET_BUTTON_PRESSED_CNT = 0x22  # Get button press count
HAND_CMD_GET_UID = 0x23  # Get 96 bits UID
HAND_CMD_GET_BATTERY_VOLTAGE = 0x24  # Get battery voltage
HAND_CMD_GET_USAGE_STAT = 0x25  # Get usage stat

# Chief SET commands
HAND_CMD_RESET = 0x40  # Please don't modify
HAND_CMD_POWER_OFF = 0x41  # Power off
HAND_CMD_SET_NODE_ID = 0x42  # Set node ID
HAND_CMD_CALIBRATE = 0x43  # Recalibrate hand
HAND_CMD_SET_CALI_DATA = 0x44  # Set finger pos range & thumb pos set
HAND_CMD_SET_FINGER_PID = 0x45  # Set PID of finger
HAND_CMD_SET_FINGER_CURRENT_LIMIT = 0x46  # Set motor current limit of finger
HAND_CMD_SET_FINGER_FORCE_TARGET = 0x47  # Set force limit of finger
HAND_CMD_SET_FINGER_POS_LIMIT = 0x48  # Get current absolute position of finger
HAND_CMD_FINGER_START = 0x49  # Start motor
HAND_CMD_FINGER_STOP = 0x4A  # Stop motor
HAND_CMD_SET_FINGER_POS_ABS = 0x4B  # Move finger to physical position, [0, 65535]
HAND_CMD_SET_FINGER_POS = 0x4C  # Move finger to logical position, [0, 65535]
HAND_CMD_SET_FINGER_ANGLE = 0x4D  # Set first joint angle of finger
HAND_CMD_SET_THUMB_ROOT_POS = 0x4E  # Move thumb root to preset position, {0, 1, 2}
HAND_CMD_SET_FINGER_POS_ABS_ALL = 0x4F  # Set current absolute position of all fingers
HAND_CMD_SET_FINGER_POS_ALL = 0x50  # Set current logical position of all fingers
HAND_CMD_SET_FINGER_ANGLE_ALL = 0x51  # Set first joint angle of all fingers
HAND_CMD_SET_FINGER_STOP_PARAMS = 0x52  # Set finger finger stop parametres
HAND_CMD_SET_FINGER_FORCE_PID = 0x53  # Set finger force PID
HAND_CMD_RESET_FORCE = 0x54  # Reset force

HAND_CMD_SET_CUSTOM = 0x5F  # Custom set command

# Auxiliary SET commands
HAND_CMD_SET_SELF_TEST_LEVEL = 0x60  # Set self-test level, level, 0: wait command, 1: semi self-test, 2: full self-test
HAND_CMD_SET_BEEP_SWITCH = 0x61  # Set beep ON/OFF
HAND_CMD_BEEP = 0x62  # Beep for duration if beep switch is on
HAND_CMD_SET_BUTTON_PRESSED_CNT = 0x63  # Set button press count, for ROH calibration only
HAND_CMD_START_INIT = 0x64  # Start init in case of SELF_TEST_LEVEL=0

CMD_ERROR_MASK = 1 << 7  # bit mask for command error

MAX_PROTOCOL_DATA_SIZE = 64


class OHandSerialAPI:
    def __init__(self, private_data, protocol, address_master, send_data_impl, recv_data_impl=None):
        self.private_data = private_data
        self.protocol = protocol
        self.address_master = address_master
        self.send_data_impl = send_data_impl
        self.recv_data_impl = recv_data_impl
        self.timeout = 255  # Default timeout in ms
        self._get_milli_seconds_impl = None
        self._delay_milli_seconds_impl = None
        self.packet_data = bytearray(MAX_PROTOCOL_DATA_SIZE + 5)
        self.is_whole_packet = False
        self.decode_state = self._initial_state()
        self.byte_count = 0

    def _initial_state(self):
        if self.protocol == HAND_PROTOCOL_UART:
            return "WAIT_ON_HEADER_0"
        elif self.protocol == HAND_PROTOCOL_I2C:
            return "WAIT_ON_ADDRESSED_NODE_ID"

    def HAND_ProtocolLRC(self, lrcBytes):
        lrc = 0
        for byte in lrcBytes:
            lrc ^= byte
        return lrc

    # def HAND_SendCmd(self, addr, cmd, data, nb_data):
    #     if not self.send_data_impl:
    #         return HAND_RESP_INVALID_CONTEXT

    #     if not self._delay_milli_seconds_impl or not self._get_milli_seconds_impl:
    #         return HAND_RESP_TIMER_FUNC_NOT_SET

    #     if nb_data >= MAX_PROTOCOL_DATA_SIZE:
    #         return HAND_RESP_DATA_SIZE_TOO_BIG

    #     send_buf = bytearray(7 + nb_data)
    #     send_buf[0] = 0x55
    #     send_buf[1] = 0xAA
    #     send_buf[2] = addr
    #     send_buf[3] = self.address_master
    #     send_buf[4] = cmd
    #     send_buf[5] = nb_data
    #     send_buf[6 : 6 + nb_data] = data

    #     lrc = self.HAND_ProtocolLRC(send_buf[2:])
    #     send_buf[6 + nb_data] = lrc

    #     self.is_whole_packet = False

    #     if self.protocol == HAND_PROTOCOL_UART:
    #         self.send_data_impl(addr, send_buf, len(send_buf), self.private_data)
    #     elif self.protocol == HAND_PROTOCOL_I2C:
    #         self.send_data_impl(addr, send_buf[2:], len(send_buf) - 2, self.private_data)

    #     return HAND_RESP_SUCCESS
    def HAND_SendCmd(self, addr, cmd, data, nb_data):
        if not self.send_data_impl:
            return HAND_RESP_INVALID_CONTEXT

        if not self._delay_milli_seconds_impl or not self._get_milli_seconds_impl:
            return HAND_RESP_TIMER_FUNC_NOT_SET

        if nb_data >= MAX_PROTOCOL_DATA_SIZE:
            return HAND_RESP_DATA_SIZE_TOO_BIG

        send_buf = bytearray(7 + nb_data)
        send_buf[0] = 0x55
        send_buf[1] = 0xAA
        send_buf[2] = addr
        send_buf[3] = self.address_master
        send_buf[4] = cmd
        send_buf[5] = nb_data
        
        # 处理data为None或空的情况
        if data is not None:
            send_buf[6:6+nb_data] = data  # 确保data是可迭代的字节数据

        # 计算LRC校验（从addr开始到data结束）
        lrc = 0
        for i in range(2, 6 + nb_data):
            lrc ^= send_buf[i]
        send_buf[6 + nb_data] = lrc
        
        # 发送数据并返回结果（假设send_data_impl返回0表示成功）
        if self.send_data_impl(addr, send_buf, len(send_buf), self.private_data) != 0:
            return HAND_RESP_HAND_ERROR
        
        return HAND_RESP_SUCCESS

    def HAND_GetResponse(self, addr, cmd, time_out, resp_bytes, remote_err):
        wait_start = self._get_milli_seconds_impl()
        wait_timeout = wait_start + time_out

        while not self.is_whole_packet:
            time.sleep(0.001)  # Delay 1ms

            if self.recv_data_impl:
                self.recv_data_impl(self.private_data)

            if self._get_milli_seconds_impl() > wait_timeout:
                self.decode_state = self._initial_state()
                return HAND_RESP_TIMEOUT

        # Validate LRC
        lrc = self.HAND_ProtocolLRC(self.packet_data[: self.packet_data[3] + 4])
        if lrc != self.packet_data[self.packet_data[3] + 4]:
            self.is_whole_packet = False
            return ERR_PROTOCOL_WRONG_LRC

        # Check if response is error
        if (self.packet_data[2] & CMD_ERROR_MASK) != 0:
            if remote_err:
                remote_err.append(self.packet_data[5])
            return HAND_RESP_HAND_ERROR

        if self.packet_data[1] != addr and addr != 0xFF:
            self.is_whole_packet = False
            return HAND_RESP_UNMATCHED_ADDR

        if self.packet_data[2] != cmd:
            self.is_whole_packet = False
            return HAND_RESP_UNMATCHED_CMD

        # Copy response data
        if resp_bytes:
            packet_byte_count = self.packet_data[3]
            if packet_byte_count > len(resp_bytes):
                return HAND_RESP_INVALID_OUT_BUFFER_SIZE
            else:
                resp_bytes[:] = self.packet_data[4 : 4 + packet_byte_count]

        self.is_whole_packet = False
        return HAND_RESP_SUCCESS

    def HAND_SetTimerFunction(self, get_milli_seconds_impl, delay_milli_seconds_impl):
        self._get_milli_seconds_impl = get_milli_seconds_impl
        self._delay_milli_seconds_impl = delay_milli_seconds_impl

    def HAND_GetTick(self):
        if self._get_milli_seconds_impl:
            return self._get_milli_seconds_impl()
        else:
            return 0

    def HAND_SetCommandTimeOut(self, timeout):
        self.timeout = timeout

    def HAND_OnData(self, data):
        if self.is_whole_packet:
            return  # Old packet is not processed, ignore

        if self.decode_state == "WAIT_ON_HEADER_0":
            if data == 0x55:
                self.decode_state = "WAIT_ON_HEADER_1"
        elif self.decode_state == "WAIT_ON_HEADER_1":
            if data == 0xAA:
                self.decode_state = "WAIT_ON_ADDRESSED_NODE_ID"
            else:
                self.decode_state = "WAIT_ON_HEADER_0"
        elif self.decode_state == "WAIT_ON_ADDRESSED_NODE_ID":
            self.packet_data[0] = data
            self.decode_state = "WAIT_ON_OWN_NODE_ID"
        elif self.decode_state == "WAIT_ON_OWN_NODE_ID":
            self.packet_data[1] = data
            self.decode_state = "WAIT_ON_COMMAND_ID"
        elif self.decode_state == "WAIT_ON_COMMAND_ID":
            self.packet_data[2] = data
            self.decode_state = "WAIT_ON_BYTECOUNT"
        elif self.decode_state == "WAIT_ON_BYTECOUNT":
            self.packet_data[3] = data
            self.byte_count = data
            if self.byte_count > MAX_PROTOCOL_DATA_SIZE:
                self.decode_state = self._initial_state()
            elif self.byte_count > 0:
                self.decode_state = "WAIT_ON_DATA"
            else:
                self.decode_state = "WAIT_ON_LRC"
        elif self.decode_state == "WAIT_ON_DATA":
            index = 4 + self.packet_data[3] - self.byte_count
            self.packet_data[index] = data
            self.byte_count -= 1
            if self.byte_count == 0:
                self.decode_state = "WAIT_ON_LRC"
        elif self.decode_state == "WAIT_ON_LRC":
            index = 4 + self.packet_data[3]
            self.packet_data[index] = data
            if self.packet_data[0] == self.address_master:
                self.is_whole_packet = True
            self.decode_state = self._initial_state()

    def HAND_GetProtocolVersion(self, hand_id, major, minor, remote_err):
        out = bytearray(2)
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_PROTOCOL_VERSION, None, 0)
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_PROTOCOL_VERSION, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS:
                minor[0] = out[0]
                major[0] = out[1]
        return err

    def HAND_GetFirmwareVersion(self, hand_id, major, minor, revision, remote_err):
        out = bytearray(4)  # Assuming revision is 2 bytes, and major/minor are 1 byte each
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_FW_VERSION, None, 0)
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_FW_VERSION, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS:
                revision[0] = out[0] | (out[1] << 8)
                minor[0] = out[2]
                major[0] = out[3]
        return err

    def HAND_GetHardwareVersion(self, hand_id, hw_type, hw_ver, boot_version, remote_err):
        out = bytearray(4)  # Assuming boot_version is 2 bytes, and hw_type/hw_ver are 1 byte each
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_HW_VERSION, None, 0)
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_HW_VERSION, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS:
                hw_type[0] = out[0]
                hw_ver[0] = out[1]
                boot_version[0] = (out[2] << 8) | out[3]
        return err

    def HAND_GetCaliData(self, hand_id, end_pos, start_pos, motor_cnt, thumb_root_pos, thumb_root_pos_cnt, remote_err):
        out = bytearray(2 + 2 * MAX_MOTOR_CNT + 2 * MAX_MOTOR_CNT + 1 + 2 * MAX_THUMB_ROOT_POS)
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_CALI_DATA, None, 0)
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_CALI_DATA, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS:
                p_data = iter(out)
                motor_cnt_ret = next(p_data)
                thumb_root_pos_cnt_ret = next(p_data)
                if motor_cnt[0] < motor_cnt_ret or thumb_root_pos_cnt[0] < thumb_root_pos_cnt_ret:
                    return HAND_RESP_DATA_SIZE_TOO_BIG
                motor_cnt[0] = motor_cnt_ret
                thumb_root_pos_cnt[0] = thumb_root_pos_cnt_ret

                end_pos_size = 2 * motor_cnt_ret
                start_pos_size = 2 * motor_cnt_ret
                thumb_root_pos_size = 2 * thumb_root_pos_cnt_ret

                if end_pos:
                    for i in range(motor_cnt_ret):
                        end_pos[i] = next(p_data) | (next(p_data) << 8)

                if start_pos:
                    for i in range(motor_cnt_ret):
                        start_pos[i] = next(p_data) | (next(p_data) << 8)

                if thumb_root_pos:
                    for i in range(thumb_root_pos_cnt_ret):
                        thumb_root_pos[i] = next(p_data) | (next(p_data) << 8)

        return err

    def HAND_GetFingerPID(self, hand_id, finger_id, p, i, d, g, remote_err):
        data = bytearray(1)
        data[0] = finger_id
        out = bytearray(1 + 4 + 4 + 4 + 4)  # Assuming float is 4 bytes
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_FINGER_PID, data, len(data))
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_FINGER_PID, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS and out[0] == finger_id:
                p[0] = int.from_bytes(out[1:5], byteorder="little")
                i[0] = int.from_bytes(out[5:9], byteorder="little")
                d[0] = int.from_bytes(out[9:13], byteorder="little")
                g[0] = int.from_bytes(out[13:17], byteorder="little")
            else:
                err = HAND_RESP_DATA_INVALID
        return err

    def HAND_GetFingerCurrentLimit(self, hand_id, finger_id, current_limit, remote_err):
        data = bytearray(1)
        data[0] = finger_id
        out = bytearray(3)
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_FINGER_CURRENT_LIMIT, data, len(data))
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_FINGER_CURRENT_LIMIT, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS and out[0] == finger_id:
                current_limit[0] = out[1] | (out[2] << 8)
            else:
                err = HAND_RESP_DATA_INVALID
        return err

    def HAND_GetFingerCurrent(self, hand_id, finger_id, current, remote_err):
        data = bytearray(1)
        data[0] = finger_id
        out = bytearray(3)
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_FINGER_CURRENT, data, len(data))
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_FINGER_CURRENT, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS and out[0] == finger_id:
                current[0] = out[1] | (out[2] << 8)
            else:
                err = HAND_RESP_DATA_INVALID
        return err

    def HAND_GetFingerForceTarget(self, hand_id, finger_id, force_target, remote_err):
        data = bytearray(1)
        data[0] = finger_id
        out = bytearray(3)
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_FINGER_FORCE_TARGET, data, len(data))
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_FINGER_FORCE_TARGET, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS and out[0] == finger_id:
                force_target[0] = out[1] | (out[2] << 8)
            else:
                err = HAND_RESP_DATA_INVALID
        return err

    def HAND_GetFingerForce(self, hand_id, finger_id, force_entry_cnt, force, remote_err):
        data = bytearray(1)
        data[0] = finger_id
        out = bytearray(1 + MAX_FORCE_ENTRIES * 2)  # Assuming each entry is 2 bytes
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_FINGER_FORCE, data, len(data))
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_FINGER_FORCE, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS:
                if finger_id != out[0]:
                    err = HAND_RESP_DATA_INVALID
                else:
                    force_entry_cnt[0] = out[1]
                    for i in range(force_entry_cnt[0]):
                        if i < len(force):
                            force[i] = out[2 + i]
        return err

    def HAND_GetFingerPosLimit(self, hand_id, finger_id, low_limit, high_limit, remote_err):
        data = bytearray(1)
        data[0] = finger_id
        out = bytearray(5)
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_FINGER_POS_LIMIT, data, len(data))
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_FINGER_POS_LIMIT, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS and out[0] == finger_id:
                low_limit[0] = out[1] | (out[2] << 8)
                high_limit[0] = out[3] | (out[4] << 8)
            else:
                err = HAND_RESP_DATA_INVALID
        return err

    def HAND_GetFingerPosAbs(self, hand_id, finger_id, target_pos, current_pos, remote_err):
        data = bytearray(1)
        data[0] = finger_id
        out = bytearray(5)
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_FINGER_POS_ABS, data, len(data))
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_FINGER_POS_ABS, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS and out[0] == finger_id:
                if target_pos:
                    target_pos[0] = out[1] | (out[2] << 8)
                if current_pos:
                    current_pos[0] = out[3] | (out[4] << 8)
            else:
                err = HAND_RESP_DATA_INVALID
        return err

    def HAND_GetFingerPos(self, hand_id, finger_id, target_pos, current_pos, remote_err):
        data = bytearray(1)
        data[0] = finger_id
        out = bytearray(5)
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_FINGER_POS, data, len(data))
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_FINGER_POS, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS and out[0] == finger_id:
                if target_pos:
                    target_pos[0] = out[1] | (out[2] << 8)
                if current_pos:
                    current_pos[0] = out[3] | (out[4] << 8)
            else:
                err = HAND_RESP_DATA_INVALID
        return err

    def HAND_GetFingerAngle(self, hand_id, finger_id, target_angle, current_angle, remote_err):
        data = bytearray(1)
        data[0] = finger_id
        out = bytearray(5)
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_FINGER_ANGLE, data, len(data))
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_FINGER_ANGLE, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS and out[0] == finger_id:
                if target_angle:
                    target_angle[0] = int.from_bytes(out[1:3], byteorder="little", signed=True)
                if current_angle:
                    current_angle[0] = int.from_bytes(out[3:5], byteorder="little", signed=True)
            else:
                err = HAND_RESP_DATA_INVALID
        return err

    def HAND_GetThumbRootPos(self, hand_id, raw_encoder, pos, remote_err):
        out = bytearray(3)
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_THUMB_ROOT_POS, None, 0)
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_THUMB_ROOT_POS, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS:
                raw_encoder[0] = out[0] | (out[1] << 8)
                pos[0] = out[2]
        return err

    def HAND_GetFingerPosAbsAll(self, hand_id, target_pos, current_pos, motor_cnt, remote_err):
        out = bytearray(2 * MAX_MOTOR_CNT * 2)
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_FINGER_POS_ABS_ALL, None, 0)
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_FINGER_POS_ABS_ALL, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS:
                motor_cnt_ret = byte_count // (2 + 2)
                if motor_cnt[0] < motor_cnt_ret:
                    return HAND_RESP_DATA_SIZE_TOO_BIG
                motor_cnt[0] = motor_cnt_ret
                if target_pos:
                    for i in range(motor_cnt_ret):
                        target_pos[i] = out[2 * i] | (out[2 * i + 1] << 8)
                if current_pos:
                    for i in range(motor_cnt_ret):
                        current_pos[i] = out[2 * motor_cnt_ret + 2 * i] | (out[2 * motor_cnt_ret + 2 * i + 1] << 8)
        return err

    def HAND_GetFingerPosAll(self, hand_id, target_pos, current_pos, motor_cnt, remote_err):
        out = bytearray(2 * MAX_MOTOR_CNT * 2)
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_FINGER_POS_ALL, None, 0)
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_FINGER_POS_ALL, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS:
                motor_cnt_ret = byte_count // (2 + 2)
                if motor_cnt[0] < motor_cnt_ret:
                    return HAND_RESP_DATA_SIZE_TOO_BIG
                motor_cnt[0] = motor_cnt_ret
                if target_pos:
                    for i in range(motor_cnt_ret):
                        target_pos[i] = out[2 * i] | (out[2 * i + 1] << 8)
                if current_pos:
                    for i in range(motor_cnt_ret):
                        current_pos[i] = out[2 * motor_cnt_ret + 2 * i] | (out[2 * motor_cnt_ret + 2 * i + 1] << 8)
        return err

    def HAND_GetFingerAngleAll(self, hand_id, target_angle, current_angle, motor_cnt, remote_err):
        out = bytearray(2 * MAX_MOTOR_CNT * 2)
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_FINGER_ANGLE_ALL, None, 0)
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_FINGER_ANGLE_ALL, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS:
                motor_cnt_ret = byte_count // (2 + 2)
                if motor_cnt[0] < motor_cnt_ret:
                    return HAND_RESP_DATA_SIZE_TOO_BIG
                motor_cnt[0] = motor_cnt_ret
                if target_angle:
                    for i in range(motor_cnt_ret):
                        target_angle[i] = int.from_bytes(out[2 * i : 2 * i + 2], byteorder="little", signed=True)
                if current_angle:
                    for i in range(motor_cnt_ret):
                        current_angle[i] = int.from_bytes(
                            out[2 * motor_cnt_ret + 2 * i : 2 * motor_cnt_ret + 2 * i + 2], byteorder="little", signed=True
                        )
        return err

    def HAND_GetFingerStopParams(self, hand_id, finger_id, speed, stop_current, stop_after_period, retry_interval, remote_err):
        data = bytearray(1)
        data[0] = finger_id
        out = bytearray(5)  # Assuming 4 bytes of stop params
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_FINGER_STOP_PARAMS, data, len(data))
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_FINGER_STOP_PARAMS, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS and out[0] == finger_id:
                speed[0] = out[1] | (out[2] << 8)
                stop_current[0] = out[3] | (out[4] << 8)
                stop_after_period[0] = out[5] | (out[6] << 8)
                retry_interval[0] = out[7] | (out[8] << 8)
            else:
                err = HAND_RESP_DATA_INVALID
        return err

    def HAND_GetFingerForcePID(self, hand_id, finger_id, p, i, d, g, remote_err):
        data = bytearray(1)
        data[0] = finger_id
        out = bytearray(1 + 4 + 4 + 4 + 4)  # Assuming float is 4 bytes
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_FINGER_FORCE_PID, data, len(data))
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_FINGER_FORCE_PID, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS and out[0] == finger_id:
                p[0] = int.from_bytes(out[1:5], byteorder="little")
                i[0] = int.from_bytes(out[5:9], byteorder="little")
                d[0] = int.from_bytes(out[9:13], byteorder="little")
                g[0] = int.from_bytes(out[13:17], byteorder="little")
            else:
                err = HAND_RESP_DATA_INVALID
        return err

    def HAND_GetSelfTestLevel(self, hand_id, self_test_level, remote_err):
        out = bytearray(1)
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_SELF_TEST_LEVEL, None, 0)
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_SELF_TEST_LEVEL, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS:
                self_test_level[0] = out[0]
        return err

    def HAND_GetBeepSwitch(self, hand_id, beep_switch, remote_err):
        out = bytearray(1)
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_BEEP_SWITCH, None, 0)
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_BEEP_SWITCH, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS:
                beep_switch[0] = out[0]
        return err

    def HAND_GetButtonPressedCnt(self, hand_id, pressed_cnt, remote_err):
        out = bytearray(1)
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_BUTTON_PRESSED_CNT, None, 0)
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_BUTTON_PRESSED_CNT, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS:
                pressed_cnt[0] = out[0]
        return err

    def HAND_GetUID(self, hand_id, uid_w0, uid_w1, uid_w2, remote_err):
        out = bytearray(12)  # 96 bits UID
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_UID, None, 0)
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_UID, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS:
                uid_w0[0] = out[0] | (out[1] << 8) | (out[2] << 16) | (out[3] << 24)
                uid_w1[0] = out[4] | (out[5] << 8) | (out[6] << 16) | (out[7] << 24)
                uid_w2[0] = out[8] | (out[9] << 8) | (out[10] << 16) | (out[11] << 24)
        return err

    def HAND_GetBatteryVoltage(self, hand_id, voltage, remote_err):
        out = bytearray(2)
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_BATTERY_VOLTAGE, None, 0)
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_BATTERY_VOLTAGE, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS:
                voltage[0] = out[0] | (out[1] << 8)
        return err

    def HAND_GetUsageStat(self, hand_id, total_use_time, total_open_times, motor_cnt, remote_err):
        data = bytearray(1)
        data[0] = motor_cnt
        out = bytearray(4 + 4 * MAX_MOTOR_CNT)
        err = self.HAND_SendCmd(hand_id, HAND_CMD_GET_USAGE_STAT, data, len(data))
        if err == HAND_RESP_SUCCESS:
            byte_count = len(out)
            err = self.HAND_GetResponse(hand_id, HAND_CMD_GET_USAGE_STAT, self.timeout, out, remote_err)
            if err == HAND_RESP_SUCCESS:
                total_use_time[0] = out[0] | (out[1] << 8) | (out[2] << 16) | (out[3] << 24)
                for i in range(MAX_MOTOR_CNT):
                    index = 4 + i * 4
                    total_open_times[i] = out[index] | (out[index + 1] << 8) | (out[index + 2] << 16) | (out[index + 3] << 24)
        return err

    def HAND_Reset(self, hand_id, mode, remote_err):
        data = bytearray(1)
        data[0] = mode
        err = self.HAND_SendCmd(hand_id, HAND_CMD_RESET, data, len(data))
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_RESET, self.timeout, None, remote_err)
        return err

    def HAND_PowerOff(self, hand_id, remote_err):
        err = self.HAND_SendCmd(hand_id, HAND_CMD_POWER_OFF, None, 0)
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_POWER_OFF, self.timeout, None, remote_err)
        return err

    def HAND_SetID(self, hand_id, new_id, remote_err):
        data = bytearray(1)
        data[0] = new_id
        err = self.HAND_SendCmd(hand_id, HAND_CMD_SET_NODE_ID, data, len(data))
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_SET_NODE_ID, self.timeout, None, remote_err)
        return err

    def HAND_Calibrate(self, hand_id, key, remote_err):
        data = bytearray(2)
        data[0] = key & 0xFF
        data[1] = (key >> 8) & 0xFF
        err = self.HAND_SendCmd(hand_id, HAND_CMD_CALIBRATE, data, len(data))
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_CALIBRATE, self.timeout, None, remote_err)
        return err

    def HAND_SetCaliData(self, hand_id, end_pos, start_pos, motor_cnt, thumb_root_pos, thumb_root_pos_cnt, remote_err):
        data = bytearray(1 + 2 * MAX_MOTOR_CNT + 2 * MAX_MOTOR_CNT + 1 + 2 * MAX_THUMB_ROOT_POS)
        p_data = 0
        data[p_data] = motor_cnt
        p_data += 1

        for i in range(motor_cnt):
            data[p_data] = end_pos[i] & 0xFF
            data[p_data + 1] = (end_pos[i] >> 8) & 0xFF
            p_data += 2

        for i in range(motor_cnt):
            data[p_data] = start_pos[i] & 0xFF
            data[p_data + 1] = (start_pos[i] >> 8) & 0xFF
            p_data += 2

        data[p_data] = thumb_root_pos_cnt
        p_data += 1

        for i in range(thumb_root_pos_cnt):
            data[p_data] = thumb_root_pos[i] & 0xFF
            data[p_data + 1] = (thumb_root_pos[i] >> 8) & 0xFF
            p_data += 2

        err = self.HAND_SendCmd(hand_id, HAND_CMD_SET_CALI_DATA, data, p_data)
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_SET_CALI_DATA, self.timeout, None, remote_err)
        return err

    def HAND_SetFingerPID(self, hand_id, finger_id, p, i, d, g, remote_err):
        data = bytearray(1 + 4 + 4 + 4 + 4)
        data[0] = finger_id
        data[1:5] = p.to_bytes(4, byteorder="little")
        data[5:9] = i.to_bytes(4, byteorder="little")
        data[9:13] = d.to_bytes(4, byteorder="little")
        data[13:17] = g.to_bytes(4, byteorder="little")

        err = self.HAND_SendCmd(hand_id, HAND_CMD_SET_FINGER_PID, data, len(data))
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_SET_FINGER_PID, self.timeout, None, remote_err)
        return err

    def HAND_SetFingerCurrentLimit(self, hand_id, finger_id, current_limit, remote_err):
        data = bytearray(3)
        data[0] = finger_id
        data[1] = current_limit & 0xFF
        data[2] = (current_limit >> 8) & 0xFF

        err = self.HAND_SendCmd(hand_id, HAND_CMD_SET_FINGER_CURRENT_LIMIT, data, len(data))
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_SET_FINGER_CURRENT_LIMIT, self.timeout, None, remote_err)
        return err

    def HAND_SetFingerForceTarget(self, hand_id, finger_id, force_limit, remote_err):
        data = bytearray(3)
        data[0] = finger_id
        data[1] = force_limit & 0xFF
        data[2] = (force_limit >> 8) & 0xFF

        err = self.HAND_SendCmd(hand_id, HAND_CMD_SET_FINGER_FORCE_TARGET, data, len(data))
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_SET_FINGER_FORCE_TARGET, self.timeout, None, remote_err)
        return err

    def HAND_SetFingerPosLimit(self, hand_id, finger_id, pos_limit_low, pos_limit_high, remote_err):
        data = bytearray(3)
        data[0] = finger_id
        data[1] = pos_limit_low & 0xFF
        data[2] = (pos_limit_low >> 8) & 0xFF
        data[1] = pos_limit_high & 0xFF
        data[2] = (pos_limit_high >> 8) & 0xFF

        err = self.HAND_SendCmd(hand_id, HAND_CMD_SET_FINGER_POS_LIMIT, data, len(data))
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_SET_FINGER_POS_LIMIT, self.timeout, None, remote_err)
        return err

    def HAND_FingerStart(self, hand_id, finger_id_bits, remote_err):
        data = bytearray(1)
        data[0] = finger_id_bits

        err = self.HAND_SendCmd(hand_id, HAND_CMD_FINGER_START, data, len(data))
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_FINGER_START, self.timeout, None, remote_err)
        return err

    def HAND_FingerStop(self, hand_id, finger_id_bits, remote_err):
        data = bytearray(1)
        data[0] = finger_id_bits

        err = self.HAND_SendCmd(hand_id, HAND_CMD_FINGER_STOP, data, len(data))
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_FINGER_STOP, self.timeout, None, remote_err)
        return err

    def HAND_SetFingerPosAbs(self, hand_id, finger_id, raw_pos, speed, remote_err):
        data = bytearray(4)
        data[0] = finger_id
        data[1] = raw_pos & 0xFF
        data[2] = (raw_pos >> 8) & 0xFF
        data[3] = speed

        err = self.HAND_SendCmd(hand_id, HAND_CMD_SET_FINGER_POS_ABS, data, len(data))
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_SET_FINGER_POS_ABS, self.timeout, None, remote_err)
        return err

    def HAND_SetFingerPos(self, hand_id, finger_id, pos, speed, remote_err):
        data = bytearray(4)
        data[0] = finger_id
        data[1] = pos & 0xFF
        data[2] = (pos >> 8) & 0xFF
        data[3] = speed

        err = self.HAND_SendCmd(hand_id, HAND_CMD_SET_FINGER_POS, data, len(data))
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_SET_FINGER_POS, self.timeout, None, remote_err)
        return err

    def HAND_SetFingerAngle(self, hand_id, finger_id, angle, speed, remote_err):
        data = bytearray(4)
        data[0] = finger_id
        data[1] = angle & 0xFF
        data[2] = (angle >> 8) & 0xFF
        data[3] = speed

        err = self.HAND_SendCmd(hand_id, HAND_CMD_SET_FINGER_ANGLE, data, len(data))
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_SET_FINGER_ANGLE, self.timeout, None, remote_err)
        return err

    def HAND_SetThumbRootPos(self, hand_id, pos, speed, remote_err):
        data = bytearray(2)
        data[0] = pos
        data[1] = speed

        err = self.HAND_SendCmd(hand_id, HAND_CMD_SET_THUMB_ROOT_POS, data, len(data))
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_SET_THUMB_ROOT_POS, self.timeout, None, remote_err)
        return err

    def HAND_SetFingerPosAbsAll(self, hand_id, raw_pos, speed, motor_cnt, remote_err):
        if motor_cnt > MAX_MOTOR_CNT:
            return HAND_RESP_DATA_INVALID

        data = bytearray(3 * motor_cnt)
        p_data = 0
        for i in range(motor_cnt):
            data[p_data] = raw_pos[i] & 0xFF
            data[p_data + 1] = (raw_pos[i] >> 8) & 0xFF
            data[p_data + 2] = speed[i]
            p_data += 3

        err = self.HAND_SendCmd(hand_id, HAND_CMD_SET_FINGER_POS_ABS_ALL, data, p_data)
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_SET_FINGER_POS_ABS_ALL, self.timeout, None, remote_err)
        return err

    def HAND_SetFingerPosAll(self, hand_id, pos, speed, motor_cnt, remote_err):
        if motor_cnt > MAX_MOTOR_CNT:
            return HAND_RESP_DATA_INVALID

        data = bytearray(3 * motor_cnt)
        p_data = 0
        for i in range(motor_cnt):
            data[p_data] = pos[i] & 0xFF
            data[p_data + 1] = (pos[i] >> 8) & 0xFF
            data[p_data + 2] = speed[i]
            p_data += 3

        err = self.HAND_SendCmd(hand_id, HAND_CMD_SET_FINGER_POS_ALL, data, p_data)
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_SET_FINGER_POS_ALL, self.timeout, None, remote_err)
        return err

    def HAND_SetFingerAngleAll(self, hand_id, angle, speed, motor_cnt, remote_err):
        if motor_cnt > MAX_MOTOR_CNT:
            return HAND_RESP_DATA_INVALID

        data = bytearray(3 * motor_cnt)
        p_data = 0
        for i in range(motor_cnt):
            data[p_data] = angle[i] & 0xFF
            data[p_data + 1] = (angle[i] >> 8) & 0xFF
            data[p_data + 2] = speed[i]
            p_data += 3

        err = self.HAND_SendCmd(hand_id, HAND_CMD_SET_FINGER_ANGLE_ALL, data, p_data)
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_SET_FINGER_ANGLE_ALL, self.timeout, None, remote_err)
        return err

    def HAND_SetFingerStopParams(self, hand_id, finger_id, speed, stop_current, stop_after_period, retry_interval, remote_err):
        data = bytearray(1 + 4 + 4 + 4 + 4)
        data[0] = finger_id
        data[1] = speed & 0xFF
        data[2] = (speed >> 8) & 0xFF
        data[3] = stop_current & 0xFF
        data[4] = (stop_current >> 8) & 0xFF
        data[5] = stop_after_period & 0xFF
        data[6] = (stop_after_period >> 8) & 0xFF
        data[7] = retry_interval & 0xFF
        data[8] = (retry_interval >> 8) & 0xFF

        err = self.HAND_SendCmd(hand_id, HAND_CMD_SET_FINGER_STOP_PARAMS, data, len(data))
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_SET_FINGER_STOP_PARAMS, self.timeout, None, remote_err)
        return err

    def HAND_SetFingerForcePID(self, hand_id, finger_id, p, i, d, g, remote_err):
        data = bytearray(1 + 4 + 4 + 4 + 4)
        data[0] = finger_id
        data[1:5] = p.to_bytes(4, byteorder="little")
        data[5:9] = i.to_bytes(4, byteorder="little")
        data[9:13] = d.to_bytes(4, byteorder="little")
        data[13:17] = g.to_bytes(4, byteorder="little")

        err = self.HAND_SendCmd(hand_id, HAND_CMD_SET_FINGER_FORCE_PID, data, len(data))
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_SET_FINGER_FORCE_PID, self.timeout, None, remote_err)
        return err

    def HAND_ResetForce(self, hand_id, remote_err):
        err = self.HAND_SendCmd(hand_id, HAND_CMD_RESET_FORCE, None, 0)
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_RESET_FORCE, self.timeout, None, remote_err)
        return err

    def HAND_SetCustom(self, hand_id, data, send_data_size, recv_data_size, remote_err):
        err = self.HAND_SendCmd(hand_id, HAND_CMD_SET_CUSTOM, data, send_data_size)
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_SET_CUSTOM, self.timeout, data, recv_data_size, remote_err)
        return err

    def HAND_SetSelfTestLevel(self, hand_id, self_test_level, remote_err):
        data = bytearray(1)
        data[0] = self_test_level

        err = self.HAND_SendCmd(hand_id, HAND_CMD_SET_SELF_TEST_LEVEL, data, len(data))
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_SET_SELF_TEST_LEVEL, self.timeout, None, remote_err)
        return err

    def HAND_SetBeepSwitch(self, hand_id, beep_on, remote_err):
        data = bytearray(1)
        data[0] = beep_on

        err = self.HAND_SendCmd(hand_id, HAND_CMD_SET_BEEP_SWITCH, data, len(data))
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_SET_BEEP_SWITCH, self.timeout, None, remote_err)
        return err

    def HAND_Beep(self, hand_id, duration, remote_err):
        data = bytearray(2)
        data[0] = duration & 0xFF
        data[1] = (duration >> 8) & 0xFF

        err = self.HAND_SendCmd(hand_id, HAND_CMD_BEEP, data, len(data))
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_BEEP, self.timeout, None, remote_err)
        return err

    def HAND_SetButtonPressedCnt(self, hand_id, pressed_cnt, remote_err):
        data = bytearray(1)
        data[0] = pressed_cnt

        err = self.HAND_SendCmd(hand_id, HAND_CMD_SET_BUTTON_PRESSED_CNT, data, len(data))
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_SET_BUTTON_PRESSED_CNT, self.timeout, None, remote_err)
        return err

    def HAND_StartInit(self, hand_id, remote_err):
        err = self.HAND_SendCmd(hand_id, HAND_CMD_START_INIT, None, 0)
        if err == HAND_RESP_SUCCESS:
            err = self.HAND_GetResponse(hand_id, HAND_CMD_START_INIT, self.timeout, None, remote_err)
        return err

def main():
    """主函数：初始化CAN连接并获取协议版本"""
    private_data = None
    try:
        # 初始化CAN总线
        private_data = can_comm.CAN_Init(port_name="1", baudrate=1000000)
        if private_data is None:
            print("CAN初始化失败，程序退出")
            return

        protocol = 0  # HAND_PROTOCOL_UART
        address_master = 0x01
        
        # 创建API实例，传入CAN模块的发送/接收函数
        api = OHandSerialAPI(
            private_data=private_data,
            protocol=protocol,
            address_master=address_master,
            send_data_impl=can_comm.send_data_impl,
            recv_data_impl=can_comm.recv_data_impl
        )
        
        # 设置CAN模块的API处理器
        can_comm.set_api_handler(api)

        # 设置定时器函数
        api.HAND_SetTimerFunction(can_comm.get_milli_seconds_impl, can_comm.delay_milli_seconds_impl)

        # 设置命令超时时间（毫秒）
        api.HAND_SetCommandTimeOut(500)

        # 准备参数
        hand_id = 0x02  # 目标手的ID
        major = [0]     # 用于存储主版本号
        minor = [0]     # 用于存储次版本号
        remote_err = [] # 用于存储远程错误码

        # 调用HAND_GetProtocolVersion接口
        print(f"请求协议版本，目标ID: 0x{hand_id:02X}")
        err = api.HAND_GetProtocolVersion(hand_id, major, minor, remote_err)

        if err == HAND_RESP_SUCCESS:
            print(f"成功获取协议版本: {major[0]}.{minor[0]}")
        else:
            print(f"获取协议版本失败，错误码: 0x{err:02X}")
            if remote_err:
                print(f"远程错误码: 0x{remote_err[0]:02X}")

    except Exception as e:
        print(f"发生意外错误: {e}")
    finally:
        # 释放CAN资源
        if private_data:
            can_comm.CAN_Shutdown(private_data)
            print("资源已释放")

if __name__ == "__main__":
    main()