from asyncio import sleep
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
def test_HAND_Reset(api):
    hand_id = 0x02
    RESET_MODE ={
        '工作模式':0,
        'DFU模式':1
    }
    # mode = 0
    remote_err = []

    err = api.HAND_Reset(hand_id, RESET_MODE.get('工作模式'), remote_err)
    assert err == HAND_RESP_SUCCESS,f"设置手重置失败: {err}"
    logger.info(f'设置手重置重启到工作模式成功')
    time.sleep(15)
    
    err = api.HAND_Reset(hand_id, RESET_MODE.get('DFU模式'), remote_err)
    assert err == HAND_RESP_SUCCESS,f"设置手重置失败: {err}"
    logger.info(f'设置手重置重启到DFU模式成功')
    time.sleep(15)
    
    logger.info('恢复默认值')
    err = api.HAND_Reset(hand_id, RESET_MODE.get('工作模式'), remote_err)
    assert err == HAND_RESP_SUCCESS,f"恢复默认值失败: {err}"
    logger.info('恢复默认值成功')
    
@pytest.mark.skip('Rohand 暂时跳过关机接口测试，单独测试pass')
def test_HAND_PowerOff(api):
    hand_id = 0x02
    remote_err = []

    err = api.HAND_PowerOff(hand_id, remote_err)
    assert err == HAND_RESP_SUCCESS,f"设置关机失败: {err}"
    logger.info('设置关机成功成功')

# @pytest.mark.skip('先跳过设备ID的修改')
# def test_HAND_SetID(api):
#     hand_id = 0x02
#     new_id = 0x02
#     verify_sets = [
#             3
#         ]
#     remote_err = []

#     err = api.HAND_SetID(hand_id, new_id, remote_err)
#     assert err == HAND_RESP_SUCCESS,f"设置设备ID失败: {err}"
#     logger.info(f'设置设备ID成功{new_id}')

def test_HAND_SetFingerPID(api):
    ######
    # err = api.HAND_SetFingerPID(hand_id=0x02, finger_id=0x00,p=100,i=200,d=25000,g=100,remote_err=[])
    # assert err == HAND_RESP_SUCCESS,f'设置pid值失败, 错误码{err}'
    # logger.info(f'设置pid值成功')
    
    ######
    
    """手指PID参数设置功能测试 - 单变量控制"""
    # 定义测试常量
    HAND_ID = 0x02
    FINGERS = [0, 1, 2, 3, 4, 5]  # 6个手指ID
    
    # 默认参数值
    DEFAULT_P = 25000
    DEFAULT_I = 200
    DEFAULT_D = 25000
    DEFAULT_G = 100
    
    # 定义各参数的测试值(包含有效/边界/无效值)
    PARAM_TEST_DATA = {
        'P': [
            (100,  "P值最小值"),
            (25000, "P值默认值"),
            (50000, "P值最大值"),
            (99,   "P值小于最小值"),
            (50001,"P值大于最大值"),
        ],
        'I': [
            (0,    "I值最小值"),
            (200,  "I值默认值"),
            (10000,"I值最大值"),
            (10001,"I值大于最大值"),
        ],
        'D': [
            (0,    "D值最小值"),
            (25000,"D值默认值"),
            (50000,"D值最大值"),
            (50001,"D值大于最大值"),
        ],
        'G': [
            (1,    "G值最小值"),
            (50,   "G值中间值"),
            (100,  "G值最大值"),
            (0,    "G值小于最小值"),
            (101,  "G值大于最大值"),
        ]
    }
    
    # 测试结果存储
    test_results = []
    
    try:
        """------------------- 单变量测试 -------------------"""
        for finger_id in FINGERS:
            logger.info(f"\n===== 开始测试手指 {finger_id} =====")
            
            # 测试P参数
            logger.info(f"测试手指 {finger_id} 的P参数")
            for p_value, desc in PARAM_TEST_DATA['P']:
                remote_err = []
                err = api.HAND_SetFingerPID(
                    HAND_ID, finger_id, 
                    p_value,        # 测试变量P
                    DEFAULT_I,      # I固定为默认值
                    DEFAULT_D,      # D固定为默认值
                    DEFAULT_G,      # G固定为默认值
                    remote_err
                )
                
                # 验证结果
                if 100 <= p_value <= 50000:  # 有效P值范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效P值失败: {desc}, 错误码: {err}"
                    test_results.append((f"手指{finger_id} P值测试({desc})", "通过"))
                else:  # 无效P值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效P值未报错: {desc}, 错误码: {err}"
                    test_results.append((f"手指{finger_id} P值测试({desc})", "通过(预期失败)"))
            
            # 测试I参数(类似P参数测试逻辑)
            logger.info(f"测试手指 {finger_id} 的I参数")
            for i_value, desc in PARAM_TEST_DATA['I']:
                remote_err = []
                err = api.HAND_SetFingerPID(
                    HAND_ID, finger_id, 
                    DEFAULT_P,      # P固定为默认值
                    i_value,        # 测试变量I
                    DEFAULT_D,      # D固定为默认值
                    DEFAULT_G,      # G固定为默认值
                    remote_err
                )
                
                if 0 <= i_value <= 10000:  # 有效I值范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效I值失败: {desc}, 错误码: {err}"
                else:
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效I值未报错: {desc}, 错误码: {err}"
            
            # 测试D参数(代码结构与I参数测试类似)
            # 测试G参数(代码结构与I参数测试类似)
            
            logger.info(f"手指 {finger_id} 所有参数测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指的默认PIDG值 =====")
        for finger_id in FINGERS:
            remote_err = []
            err = api.HAND_SetFingerPID(
                HAND_ID, finger_id, 
                DEFAULT_P, DEFAULT_I, DEFAULT_D, DEFAULT_G, remote_err
            )
            assert err == HAND_RESP_SUCCESS, \
                f"恢复手指 {finger_id} 默认值失败, 错误码: {err}"
            logger.info(f"手指 {finger_id} 已恢复默认值")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复所有手指默认值
        try:
            logger.warning("正在尝试恢复所有手指默认值...")
            for finger_id in FINGERS:
                api.HAND_SetFingerPID(
                    HAND_ID, finger_id, 
                    DEFAULT_P, DEFAULT_I, DEFAULT_D, DEFAULT_G, []
                )
        except Exception as recovery_err:
            logger.error(f"恢复默认值失败: {str(recovery_err)}")
        raise  # 重新抛出原始错误
    
    finally:
        """------------------- 测试结果汇总 -------------------"""
        logger.info("\n===== 测试结果汇总 =====")
        passed = sum(1 for case, result in test_results if "通过" in result)
        total = len(test_results)
        logger.info(f"总测试用例: {total}, 通过: {passed}, 失败: {total - passed}")
        
        for case, result in test_results:
            logger.info(f"{case}: {result}")
        logger.info("=======================")


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

@pytest.mark.skip('单独跑测试是可以通过，研发后续会优化代码，暂时跳过')
def test_HAND_FingerStart(api):
    hand_id = 0x02
    finger_id_bits = 0x01
    remote_err = []

    err = api.HAND_FingerStart(hand_id, finger_id_bits, remote_err)
    assert err == HAND_RESP_SUCCESS, f"设置开始移动手指失败，错误码: {err}"
    logger.info(f'设置开始移动手指成功')
    
@pytest.mark.skip('单独跑测试是可以通过，研发后续会优化代码，暂时跳过')
def test_HAND_FingerStop(api):
    hand_id = 0x02
    finger_id_bits = 0x01
    remote_err = []

    err = api.HAND_FingerStop(hand_id, finger_id_bits, remote_err)
    assert err == HAND_RESP_SUCCESS, f"设置停止移动手指失败，错误码: {err}"
    logger.info(f'设置停止移动手指成功')


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

def test_HAND_ResetForce(api):# 修改api调用接口函数，添加none后测试pass
    hand_id = 0x02
    remote_err = []

    err = api.HAND_ResetForce(hand_id, remote_err)
    assert err == HAND_RESP_SUCCESS, f"重置力量值，错误码: {err}"
    logger.info("成功重置力量值")

def test_HAND_SetSelfTestLevel(api):
    hand_id = 0x02
    SELF_TEST_LEVEL = {
        '等待指令': 0,
        '半自检': 1,
        '完整自检': 2
    }
    
    # 测试设置为半自检
    remote_err = [0]
    err = api.HAND_SetSelfTestLevel(hand_id, SELF_TEST_LEVEL['半自检'], remote_err)
    assert err == HAND_RESP_SUCCESS, f"设置半自检失败，错误码: {err}"
    
    time.sleep(1)  # 等待自检执行
    
    current_level = [0]
    err = api.HAND_GetSelfTestLevel(hand_id, current_level, [])
    assert err == HAND_RESP_SUCCESS, f"获取自检级别失败，错误码: {err}"
    
    assert current_level[0] == SELF_TEST_LEVEL['半自检'], (
        f"自检级别验证失败：期望半自检({SELF_TEST_LEVEL['半自检']})，"
        f"实际{list(SELF_TEST_LEVEL.keys())[list(SELF_TEST_LEVEL.values()).index(current_level[0])]}({current_level[0]})"
    )
    logger.info("成功设置半自检")
    
    # 测试设置为完整自检（恢复默认状态）
    remote_err = [0]
    err = api.HAND_SetSelfTestLevel(hand_id, SELF_TEST_LEVEL['完整自检'], remote_err)
    assert err == HAND_RESP_SUCCESS, f"设置完整自检失败，错误码: {err}"
    
    time.sleep(1)  # 等待自检执行
    
    err = api.HAND_GetSelfTestLevel(hand_id, current_level, [])
    assert err == HAND_RESP_SUCCESS, f"获取自检级别失败，错误码: {err}"
    
    assert current_level[0] == SELF_TEST_LEVEL['完整自检'], (
        f"自检级别验证失败：期望完整自检({SELF_TEST_LEVEL['完整自检']})，"
        f"实际{list(SELF_TEST_LEVEL.keys())[list(SELF_TEST_LEVEL.values()).index(current_level[0])]}({current_level[0]})"
    )
    logger.info("成功设置完整自检")
    
    # 确保测试结束后恢复默认状态
    remote_err = [0]
    err = api.HAND_SetSelfTestLevel(hand_id, SELF_TEST_LEVEL['完整自检'], remote_err)
    if err != HAND_RESP_SUCCESS:
        logger.error(f"恢复默认自检级别失败，错误码: {err}")


def test_HAND_SetBeepSwitch(api):
    hand_id = 0x02
    BEEP_STATUS = {
        'OFF': 0,
        'ON': 1
    }
    
    # 测试关闭蜂鸣器
    err = api.HAND_SetBeepSwitch(hand_id, BEEP_STATUS['OFF'], [])
    assert err == HAND_RESP_SUCCESS, f"设置蜂鸣器关闭失败，错误码: {err}"
    
    time.sleep(0.5)  # 等待设备响应
    
    status_container = [0]
    err = api.HAND_GetBeepSwitch(hand_id, status_container, [])
    assert err == HAND_RESP_SUCCESS, f"获取蜂鸣器状态失败，错误码: {err}"
    
    actual_status = status_container[0]
    assert actual_status == BEEP_STATUS['OFF'], (
        f"蜂鸣器关闭状态验证失败：期望={BEEP_STATUS['OFF']}，实际={actual_status}"
    )
    logger.info("蜂鸣器已成功关闭")
    
    # 测试开启蜂鸣器
    err = api.HAND_SetBeepSwitch(hand_id, BEEP_STATUS['ON'], [])
    assert err == HAND_RESP_SUCCESS, f"设置蜂鸣器开启失败，错误码: {err}"
    
    time.sleep(0.5)  # 等待设备响应
    
    err = api.HAND_GetBeepSwitch(hand_id, status_container, [])
    assert err == HAND_RESP_SUCCESS, f"获取蜂鸣器状态失败，错误码: {err}"
    
    actual_status = status_container[0]
    assert actual_status == BEEP_STATUS['ON'], (
        f"蜂鸣器开启状态验证失败：期望={BEEP_STATUS['ON']}，实际={actual_status}"
    )
    logger.info("蜂鸣器已成功开启")
    
    # 恢复默认状态
    err = api.HAND_SetBeepSwitch(hand_id, BEEP_STATUS['ON'], [])
    if err != HAND_RESP_SUCCESS:
        logger.error(f"恢复蜂鸣器默认状态失败，错误码: {err}")
    else:
        logger.info('蜂鸣器开关已恢复默认状态')


# def test_HAND_Beep(api): # 设置时长慧报3的错误码
#     hand_id = 0x02
#     duration = 500
#     err = api.HAND_Beep(hand_id, duration, [])
#     assert err == HAND_RESP_SUCCESS,f"设置蜂鸣器时长失败: {err}"
#     logger.info(f'成功设置蜂鸣器时长：{duration}')

def test_HAND_SetButtonPressedCnt(api):
    hand_id = 0x02
    
    # 测试正常范围（0-255）
    # 测试最小值
    target_pressed_cnt = 0
    remote_err = [0]
    err = api.HAND_SetButtonPressedCnt(hand_id, target_pressed_cnt, remote_err)
    assert err == HAND_RESP_SUCCESS, (
        f"设置按钮按下次数失败（值={target_pressed_cnt}），错误码: {err}"
    )
    
    observed_pressed_cnt = [0]
    err = api.HAND_GetButtonPressedCnt(hand_id, observed_pressed_cnt, remote_err)
    assert err == HAND_RESP_SUCCESS, (
        f"获取按钮按下次数失败（值={target_pressed_cnt}），错误码: {err}"
    )
    
    actual_cnt = observed_pressed_cnt[0]
    assert actual_cnt == target_pressed_cnt, (
        f"按钮按下次数验证失败：目标值={target_pressed_cnt}，实际值={actual_cnt}"
    )
    
    logger.info(f"按钮按下次数设置成功，值={target_pressed_cnt}")
    
    # 测试中间值
    target_pressed_cnt = 128
    remote_err = [0]
    err = api.HAND_SetButtonPressedCnt(hand_id, target_pressed_cnt, remote_err)
    assert err == HAND_RESP_SUCCESS, (
        f"设置按钮按下次数失败（值={target_pressed_cnt}），错误码: {err}"
    )
    
    observed_pressed_cnt = [0]
    err = api.HAND_GetButtonPressedCnt(hand_id, observed_pressed_cnt, remote_err)
    assert err == HAND_RESP_SUCCESS, (
        f"获取按钮按下次数失败（值={target_pressed_cnt}），错误码: {err}"
    )
    
    actual_cnt = observed_pressed_cnt[0]
    assert actual_cnt == target_pressed_cnt, (
        f"按钮按下次数验证失败：目标值={target_pressed_cnt}，实际值={actual_cnt}"
    )
    
    logger.info(f"按钮按下次数设置成功，值={target_pressed_cnt}")
    
    # 测试最大值
    target_pressed_cnt = 255
    remote_err = [0]
    err = api.HAND_SetButtonPressedCnt(hand_id, target_pressed_cnt, remote_err)
    assert err == HAND_RESP_SUCCESS, (
        f"设置按钮按下次数失败（值={target_pressed_cnt}），错误码: {err}"
    )
    
    observed_pressed_cnt = [0]
    err = api.HAND_GetButtonPressedCnt(hand_id, observed_pressed_cnt, remote_err)
    assert err == HAND_RESP_SUCCESS, (
        f"获取按钮按下次数失败（值={target_pressed_cnt}），错误码: {err}"
    )
    
    actual_cnt = observed_pressed_cnt[0]
    assert actual_cnt == target_pressed_cnt, (
        f"按钮按下次数验证失败：目标值={target_pressed_cnt}，实际值={actual_cnt}"
    )
    
    logger.info(f"按钮按下次数设置成功，值={target_pressed_cnt}")
    
    # 测试超出范围（256-65535） - 期望触发ValueError
    # 测试超出范围的最小值（256）
    try:
        api.HAND_SetButtonPressedCnt(hand_id, 256, [0])
    except ValueError as e:
        logger.info(f"成功捕获预期的ValueError（值=256）: {str(e)}")
    else:
        assert False, "设置超出范围的值（256）未触发ValueError"
    
    # 测试中间值（32768）
    try:
        api.HAND_SetButtonPressedCnt(hand_id, 32768, [0])
    except ValueError as e:
        logger.info(f"成功捕获预期的ValueError（值=32768）: {str(e)}")
    else:
        assert False, "设置超出范围的值（32768）未触发ValueError"
    
    # 测试超出范围的最大值（65535）
    try:
        api.HAND_SetButtonPressedCnt(hand_id, 65535, [0])
    except ValueError as e:
        logger.info(f"成功捕获预期的ValueError（值=65535）: {str(e)}")
    else:
        assert False, "设置超出范围的值（65535）未触发ValueError"
    
    # 测试负数（-1）
    try:
        api.HAND_SetButtonPressedCnt(hand_id, -1, [0])
    except ValueError as e:
        logger.info(f"成功捕获预期的ValueError（值=-1）: {str(e)}")
    else:
        assert False, "设置负数（-1）未触发ValueError"

def test_HAND_StartInit(api):
    hand_id = 0x02
    remote_err = []
    err = api.HAND_StartInit(hand_id, remote_err)
    assert err == HAND_RESP_SUCCESS,f"初始化手失败，错误码: {err}"
    logger.info(f'手初始化成功')
