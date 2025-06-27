import logging
import pytest
from OHandSerialAPI import HAND_RESP_SUCCESS, MAX_MOTOR_CNT,MAX_THUMB_ROOT_POS,MAX_FORCE_ENTRIES,OHandSerialAPI
from can_communication import *

# 设置日志级别为INFO，获取日志记录器实例
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()

# 设置处理程序的日志级别为 INFO
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

# 初始化 API 实例（pytest夹具）
@pytest.fixture
def api():
    private_data = None
    api = None
    
    try:
        # 初始化CAN总线
        private_data = CAN_Init(port_name="1", baudrate=1000000)
        if private_data is None:
            pytest.skip("Could not connect to CAN bus. Skipping tests.")
            
        protocol = 0  # HAND_PROTOCOL_UART
        address_master = 0x01

        # 创建API实例
        api = OHandSerialAPI(
            private_data=private_data,
            protocol=protocol,
            address_master=address_master,
            send_data_impl=send_data_impl,
            recv_data_impl=recv_data_impl
        )

        # 设置CAN模块的API处理器
        set_api_handler(api)

        # 设置定时器函数
        api.HAND_SetTimerFunction(get_milli_seconds_impl, delay_milli_seconds_impl)

        # 设置命令超时时间
        api.HAND_SetCommandTimeOut(255)
        
        # logger.info("CAN bus initialized successfully")
        yield api
        
    except Exception as e:
        # logger.error(f"Failed to initialize API: {e}")
        pytest.skip(f"Setup failed: {e}")
        
    finally:
        # 确保资源被正确释放
        if api and hasattr(api, 'shutdown'):  # 检查是否有自定义关闭方法
            try:
                api.shutdown()
                # logger.info("API shutdown successfully")
            except Exception as e:
                logger.error(f"Error during API shutdown: {e}")
        
        if private_data:
            try:
                CAN_Shutdown(private_data)
                # logger.info("CAN bus connection closed")
            except Exception as e:
                logger.error(f"Error closing CAN bus: {e}")

# --------------------------- GET 命令测试 ---------------------------
def test_HAND_GetProtocolVersion(api):
    hand_id = 0x02
    major, minor = [0], [0]
    err = api.HAND_GetProtocolVersion(hand_id, major, minor, [])
    assert err == HAND_RESP_SUCCESS, f"获取协议版本失败: {err}"
    logger.info(f"成功获取协议版本: V{major[0]}.{minor[0]}")

def test_HAND_GetFirmwareVersion(api):
    hand_id = 0x02
    major, minor, revision = [0], [0], [0]
    err = api.HAND_GetFirmwareVersion(hand_id, major, minor, revision, [])
    assert err == HAND_RESP_SUCCESS, f"获取固件版本失败: {err}"
    logger.info(f"成功获固件版本: V{major[0]}.{minor[0]}.{revision[0]}")

def test_HAND_GetHardwareVersion(api):
    hand_id = 0x02
    hw_type, hw_ver, boot_version = [0], [0],[0]
    err = api.HAND_GetHardwareVersion(hand_id, hw_type, hw_ver, boot_version, [])
    assert err == HAND_RESP_SUCCESS, f"获取硬件版本失败: {err}"
    logger.info(f"成功获取硬件版本: V{hw_type[0]}.{hw_ver[0]}.{boot_version[0]}")


def test_HAND_GetFingerPID(api):
    hand_id = 0x02
    finger_id = 0x00
    p = [0]
    i = [0]
    d = [0]
    g = [0]
    for j in range(6):
        err = api.HAND_GetFingerPID(hand_id, finger_id+j, p, i, d, g, [])
        assert err == HAND_RESP_SUCCESS, f"获取手指p, i, d, g值失败: {err}"
        logger.info(f"成功获取手指{finger_id+j} p, i, d, g值: {p[0]},{i[0]},{d[0]},{g[0]}")


def test_HAND_GetFingerCurrentLimit(api):
    hand_id = 0x02
    finger_id = 0x00
    current_limit = [0]
    for i in range(6):
        err = api.HAND_GetFingerCurrentLimit(hand_id, finger_id+i, current_limit, [])
        assert err == HAND_RESP_SUCCESS, f"获取手指电流限制值失败: {err}"
        logger.info(f"成功获取手指{finger_id+i} 电流限制值: {current_limit[0]}")

def test_HAND_GetFingerCurrent(api):
    hand_id = 0x02
    finger_id = 0x00
    current = [0]
    for i in range(6):
        err = api.HAND_GetFingerCurrent(hand_id, finger_id+i, current, [])
        assert err == HAND_RESP_SUCCESS,f"获取手指电流值失败: {err}"
        logger.info(f"成功获取手指{finger_id+i} 电流值: {current[0]}")

def test_HAND_GetFingerForceTarget(api):
    hand_id = 0x02
    finger_id = 0x00
    force_target = [0]
    for i in range(6):
        err = api.HAND_GetFingerForceTarget(hand_id, finger_id, force_target, [])
        assert err == HAND_RESP_SUCCESS,f"获取手指力量目标值失败: {err}"
        logger.info(f"成功获取手指{finger_id+i} 力量目标值: {force_target[0]}")

def test_HAND_GetFingerForce(api):
    hand_id = 0x02
    finger_id = 0x00
    force_entry_cnt = [0]
    force = [0] * MAX_FORCE_ENTRIES
    for i in range(6):
        err = api.HAND_GetFingerForce(hand_id, finger_id+i, force_entry_cnt, force, [])
        assert err == HAND_RESP_SUCCESS,f"获取手指当前力量值失败: {err}"
        logger.info(f"成功获取手指{finger_id+i} 力量目标值: {force}")

def test_HAND_GetFingerPosLimit(api):
    hand_id = 0x02
    finger_id = 0x00
    low_limit = [0]
    high_limit = [0]
    for i in range(6):
        err = api.HAND_GetFingerPosLimit(hand_id, finger_id+i, low_limit, high_limit, [])
        assert err == HAND_RESP_SUCCESS,f"获取手指绝对位置限制值失败: {err}"
        logger.info(f"成功获取手指{finger_id+i} 绝对位置限制值: {low_limit[0]}, {high_limit[0]}")

def test_HAND_GetFingerPosAbs(api):
    hand_id = 0x02
    finger_id = 0x00
    target_pos = [0]
    current_pos = [0]
    for i in range(6):
        err = api.HAND_GetFingerPosAbs(hand_id, finger_id+i, target_pos, current_pos, [])
        assert err == HAND_RESP_SUCCESS,f"获取手指绝当前绝对位置值失败: {err}"
        logger.info(f"成功获取手指{finger_id+i} 当前绝对位置值: {target_pos[0]}, {current_pos[0]}")


def test_HAND_GetFingerPos(api):
    hand_id = 0x02
    finger_id = 0x00
    target_pos = [0]
    current_pos = [0]
    for i in range(6):
        err = api.HAND_GetFingerPos(hand_id, finger_id+i, target_pos, current_pos, [])
        assert err == HAND_RESP_SUCCESS,f"获取手指绝当前逻辑位置值失败: {err}"
        logger.info(f"成功获取手指{finger_id+i} 当前逻辑位置值: {target_pos[0]}, {current_pos[0]}")

def test_HAND_GetFingerAngle(api):
    hand_id = 0x02
    finger_id = 0x00
    target_angle = [0]
    current_angle = [0]
    for i in range(6):
        err = api.HAND_GetFingerAngle(hand_id, finger_id+i, target_angle, current_angle, [])
        assert err == HAND_RESP_SUCCESS,f"获取手指第一关节角度值失败: {err}"
        logger.info(f"成功获取手指{finger_id+i} 第一关节角度值: {target_angle[0]}, {current_angle[0]}")

def test_HAND_GetThumbRootPos(api):
    hand_id = 0x02
    raw_encoder = [0]
    pos = [0]
    err = api.HAND_GetThumbRootPos(hand_id, raw_encoder, pos, [])
    assert err == HAND_RESP_SUCCESS,f"获取大拇指旋转预设位置值失败: {err}"
    logger.info(f"成功获取大拇指旋转预设位置值: {raw_encoder[0]}, {pos[0]}")

def test_HAND_GetFingerPosAbsAll(api):
    hand_id = 0x02
    target_pos = [0] * MAX_MOTOR_CNT
    current_pos = [0] * MAX_MOTOR_CNT
    motor_cnt = [MAX_MOTOR_CNT]
    err = api.HAND_GetFingerPosAbsAll(hand_id, target_pos, current_pos, motor_cnt, [])
    assert err == HAND_RESP_SUCCESS,f"获取所有手指当前的绝对位置值失败: {err}"
    logger.info(f"成功获取所有手指当前的绝对位置值: {target_pos}, {current_pos},{motor_cnt}")


def test_HAND_GetFingerPosAll(api):
    hand_id = 0x02
    target_pos = [0] * MAX_MOTOR_CNT
    current_pos = [0] * MAX_MOTOR_CNT
    motor_cnt = [MAX_MOTOR_CNT]
    remote_err = []
    err = api.HAND_GetFingerPosAll(hand_id, target_pos, current_pos, motor_cnt, remote_err)
    assert err == HAND_RESP_SUCCESS,f"获取所有手指当前的逻辑位置值失败: {err}"
    logger.info(f"成功获取所有手指当前的逻辑位置值: {target_pos}, {current_pos},{motor_cnt}")

def test_HAND_GetFingerAngleAll(api):
    hand_id = 0x02
    target_angle = [0] * MAX_MOTOR_CNT
    current_angle = [0] * MAX_MOTOR_CNT
    motor_cnt = [MAX_MOTOR_CNT]
    err = api.HAND_GetFingerAngleAll(hand_id, target_angle, current_angle, motor_cnt, [])
    assert err == HAND_RESP_SUCCESS,f"获取所有手指值失败: {err}"
    logger.info(f"成功获取所有手指当前的逻辑位置值: {target_angle}, {current_angle},{motor_cnt}")
    
def test_HAND_GetFingerForcePID(api):
    hand_id = 0x02
    finger_id = 0x00
    p = [0]
    i = [0]
    d = [0]
    g = [0]
    for j in range(5): #拇指旋转没带
        err = api.HAND_GetFingerForcePID(hand_id, finger_id+j, p, i, d, g, [])
        assert err == HAND_RESP_SUCCESS,f"获取手指力量p, i, d, g值失败: {err}"
        logger.info(f"成功获取手指{finger_id+j} 力量p, i, d, g值: {p[0]}, {i[0]},{d[0]},{g[0]}")

def test_HAND_GetSelfTestLevel(api):
    hand_id = 0x02
    self_test_level = [0]
    err = api.HAND_GetSelfTestLevel(hand_id, self_test_level, [])
    assert err == HAND_RESP_SUCCESS,f"获取手自检开关状态失败: {err}"
    logger.info(f"成功获取手自检开关状态: {self_test_level[0]}")

def test_HAND_GetBeepSwitch(api):
    hand_id = 0x02
    beep_switch = [0]
    err = api.HAND_GetBeepSwitch(hand_id, beep_switch, [])
    assert err == HAND_RESP_SUCCESS,f"获取手蜂鸣器开关状态失败: {err}"
    logger.info(f"成功获取手蜂鸣器开关状态: {beep_switch[0]}")

def test_HAND_GetButtonPressedCnt(api):
    hand_id = 0x02
    pressed_cnt = [0]
    err = api.HAND_GetButtonPressedCnt(hand_id, pressed_cnt, [])
    assert err == HAND_RESP_SUCCESS,f"获取手按钮按下次数值失败: {err}"
    logger.info(f"成功获取手按钮按下次数值: {pressed_cnt[0]}")

def test_HAND_GetUID(api):
    hand_id = 0x02
    uid_w0 = [0]
    uid_w1 = [0]
    uid_w2 = [0]
    err = api.HAND_GetUID(hand_id, uid_w0, uid_w1, uid_w2, [])
    assert err == HAND_RESP_SUCCESS,f"获取手UID值失败: {err}"
    logger.info(f"成功获取手UID值: {uid_w0[0]},{uid_w1[0]},{uid_w2[0]}")

def test_HAND_GetBatteryVoltage(api):
    hand_id = 0x02
    voltage = [0]
    err = api.HAND_GetBatteryVoltage(hand_id, voltage, [])
    assert err == HAND_RESP_SUCCESS,f"获取手电池电压值失败: {err}"
    logger.info(f"成功获取手电池电压值: {voltage[0]}")

def test_HAND_GetUsageStat(api):
    hand_id = 0x02
    total_use_time = [0]
    total_open_times = [0] * MAX_MOTOR_CNT
    motor_cnt = MAX_MOTOR_CNT
    err = api.HAND_GetUsageStat(hand_id, total_use_time, total_open_times, motor_cnt, [])
    assert err == HAND_RESP_SUCCESS,f"获取手使用数据值失败: {err}"
    logger.info(f"成功获取手使用数据值: {total_use_time[0]},{total_open_times},{motor_cnt}")

# --------------------------- SET 命令测试 ---------------------------
# def test_HAND_Reset(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     mode = 0
#     remote_err = []

#     err = api.HAND_Reset(hand_id, mode, remote_err)
#     assert err == HAND_RESP_SUCCESS


# def test_HAND_PowerOff(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     remote_err = []

#     err = api.HAND_PowerOff(hand_id, remote_err)
#     assert err == HAND_RESP_SUCCESS

# @pytest.mark.skip('先跳过设备ID的修改')
# def test_HAND_SetID(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     new_id = 0x03
#     remote_err = []

#     err = api.HAND_SetID(hand_id, new_id, remote_err)
#     assert err == HAND_RESP_SUCCESS


# def test_HAND_SetFingerPID(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     finger_id = 0x01
#     p = 10
#     i = 20
#     d = 30
#     g = 40
#     remote_err = []

#     err = api.HAND_SetFingerPID(hand_id, finger_id, p, i, d, g, remote_err)
#     assert err == HAND_RESP_SUCCESS


# def test_HAND_SetFingerCurrentLimit(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     finger_id = 0x01
#     current_limit = 100
#     remote_err = []

#     err = api.HAND_SetFingerCurrentLimit(hand_id, finger_id, current_limit, remote_err)
#     assert err == HAND_RESP_SUCCESS


# def test_HAND_SetFingerForceTarget(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     finger_id = 0x01
#     force_limit = 200
#     remote_err = []

#     err = api.HAND_SetFingerForceTarget(hand_id, finger_id, force_limit, remote_err)
#     assert err == HAND_RESP_SUCCESS


# def test_HAND_SetFingerPosLimit(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     finger_id = 0x01
#     pos_limit_low = 10
#     pos_limit_high = 100
#     remote_err = []

#     err = api.HAND_SetFingerPosLimit(hand_id, finger_id, pos_limit_low, pos_limit_high, remote_err)
#     assert err == HAND_RESP_SUCCESS


# def test_HAND_FingerStart(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     finger_id_bits = 0x01
#     remote_err = []

#     err = api.HAND_FingerStart(hand_id, finger_id_bits, remote_err)
#     assert err == HAND_RESP_SUCCESS


# def test_HAND_FingerStop(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     finger_id_bits = 0x01
#     remote_err = []

#     err = api.HAND_FingerStop(hand_id, finger_id_bits, remote_err)
#     assert err == HAND_RESP_SUCCESS


# def test_HAND_SetFingerPosAbs(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     finger_id = 0x01
#     raw_pos = 100
#     speed = 50
#     remote_err = []

#     err = api.HAND_SetFingerPosAbs(hand_id, finger_id, raw_pos, speed, remote_err)
#     assert err == HAND_RESP_SUCCESS


# def test_HAND_SetFingerPos(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     finger_id = 0x01
#     pos = 100
#     speed = 50
#     remote_err = []

#     err = api.HAND_SetFingerPos(hand_id, finger_id, pos, speed, remote_err)
#     assert err == HAND_RESP_SUCCESS


# def test_HAND_SetFingerAngle(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     finger_id = 0x01
#     angle = 45
#     speed = 50
#     remote_err = []

#     err = api.HAND_SetFingerAngle(hand_id, finger_id, angle, speed, remote_err)
#     assert err == HAND_RESP_SUCCESS


# def test_HAND_SetThumbRootPos(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     pos = 50
#     speed = 20
#     remote_err = []

#     err = api.HAND_SetThumbRootPos(hand_id, pos, speed, remote_err)
#     assert err == HAND_RESP_SUCCESS


# def test_HAND_SetFingerPosAbsAll(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     raw_pos = [100] * MAX_MOTOR_CNT
#     speed = [50] * MAX_MOTOR_CNT
#     motor_cnt = MAX_MOTOR_CNT
#     remote_err = []

#     err = api.HAND_SetFingerPosAbsAll(hand_id, raw_pos, speed, motor_cnt, remote_err)
#     assert err == HAND_RESP_SUCCESS


# def test_HAND_SetFingerPosAll(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     pos = [100] * MAX_MOTOR_CNT
#     speed = [50] * MAX_MOTOR_CNT
#     motor_cnt = MAX_MOTOR_CNT
#     remote_err = []

#     err = api.HAND_SetFingerPosAll(hand_id, pos, speed, motor_cnt, remote_err)
#     assert err == HAND_RESP_SUCCESS


# def test_HAND_SetFingerAngleAll(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     angle = [45] * MAX_MOTOR_CNT
#     speed = [50] * MAX_MOTOR_CNT
#     motor_cnt = MAX_MOTOR_CNT
#     remote_err = []

#     err = api.HAND_SetFingerAngleAll(hand_id, angle, speed, motor_cnt, remote_err)
#     assert err == HAND_RESP_SUCCESS

# def test_HAND_SetFingerForcePID(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     finger_id = 0x01
#     p = 10
#     i = 20
#     d = 30
#     g = 40
#     remote_err = []

#     err = api.HAND_SetFingerForcePID(hand_id, finger_id, p, i, d, g, remote_err)
#     assert err == HAND_RESP_SUCCESS


# def test_HAND_ResetForce(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     remote_err = []

#     err = api.HAND_ResetForce(hand_id, remote_err)
#     assert err == HAND_RESP_SUCCESS

# def test_HAND_SetSelfTestLevel(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     self_test_level = 1
#     remote_err = []

#     err = api.HAND_SetSelfTestLevel(hand_id, self_test_level, remote_err)
#     assert err == HAND_RESP_SUCCESS


# def test_HAND_SetBeepSwitch(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     beep_on = 1
#     remote_err = []

#     err = api.HAND_SetBeepSwitch(hand_id, beep_on, remote_err)
#     assert err == HAND_RESP_SUCCESS


# def test_HAND_Beep(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     duration = 100
#     remote_err = []

#     err = api.HAND_Beep(hand_id, duration, remote_err)
#     assert err == HAND_RESP_SUCCESS


# def test_HAND_SetButtonPressedCnt(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     pressed_cnt = 10
#     remote_err = []

#     err = api.HAND_SetButtonPressedCnt(hand_id, pressed_cnt, remote_err)
#     assert err == HAND_RESP_SUCCESS


# def test_HAND_StartInit(api):
#     if api is None:
#         pytest.skip("API 初始化失败，跳过测试")
#     hand_id = 0x02
#     remote_err = []

#     err = api.HAND_StartInit(hand_id, remote_err)
#     assert err == HAND_RESP_SUCCESS
