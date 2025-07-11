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
    err, remote_err = api.HAND_GetProtocolVersion(hand_id, major, minor, [])
    assert err == HAND_RESP_SUCCESS, f"获取协议版本失败: err={err},remote_err={remote_err}"
    logger.info(f"成功获取协议版本: V{major[0]}.{minor[0]}")

def test_HAND_GetFirmwareVersion(api):
    hand_id = 0x02
    major, minor, revision = [0], [0], [0]
    err, remote_err = api.HAND_GetFirmwareVersion(hand_id, major, minor, revision, [])
    assert err == HAND_RESP_SUCCESS, f"获取固件版本失败: err={err},remote_err={remote_err}"
    logger.info(f"成功获固件版本: V{major[0]}.{minor[0]}.{revision[0]}")

def test_HAND_GetHardwareVersion(api):
    hand_id = 0x02
    hw_type, hw_ver, boot_version = [0], [0],[0]
    err, remote_err = api.HAND_GetHardwareVersion(hand_id, hw_type, hw_ver, boot_version, [])
    assert err == HAND_RESP_SUCCESS, f"获取硬件版本失败: err={err},remote_err={remote_err}"
    logger.info(f"成功获取硬件版本: V{hw_type[0]}.{hw_ver[0]}.{boot_version[0]}")


def test_HAND_GetFingerPID(api):
    hand_id = 0x02
    finger_id = 0x00
    p = [0]
    i = [0]
    d = [0]
    g = [0]
    for j in range(6):
        err, remote_err = api.HAND_GetFingerPID(hand_id, finger_id+j, p, i, d, g, [])
        assert err == HAND_RESP_SUCCESS, f"获取手指p, i, d, g值失败: err={err},remote_err={remote_err}"
        logger.info(f"成功获取手指{finger_id+j} p, i, d, g值: {p[0]},{i[0]},{d[0]},{g[0]}")


def test_HAND_GetFingerCurrentLimit(api):
    hand_id = 0x02
    finger_id = 0x00
    current_limit = [0]
    for i in range(6):
        err, remote_err = api.HAND_GetFingerCurrentLimit(hand_id, finger_id+i, current_limit, [])
        assert err == HAND_RESP_SUCCESS, f"获取手指电流限制值失败: err={err},remote_err={remote_err}"
        logger.info(f"成功获取手指{finger_id+i} 电流限制值: {current_limit[0]}")

def test_HAND_GetFingerCurrent(api):
    hand_id = 0x02
    finger_id = 0x00
    current = [0]
    for i in range(6):
        err, remote_err = api.HAND_GetFingerCurrent(hand_id, finger_id+i, current, [])
        assert err == HAND_RESP_SUCCESS,f"获取手指电流值失败: err={err},remote_err={remote_err}"
        logger.info(f"成功获取手指{finger_id+i} 电流值: {current[0]}")

def test_HAND_GetFingerForceTarget(api):
    hand_id = 0x02
    finger_id = 0x00
    force_target = [0]
    for i in range(6):
        err, remote_err = api.HAND_GetFingerForceTarget(hand_id, finger_id, force_target, [])
        assert err == HAND_RESP_SUCCESS,f"获取手指力量目标值失败: err={err},remote_err={remote_err}"
        logger.info(f"成功获取手指{finger_id+i} 力量目标值: {force_target[0]}")

def test_HAND_GetFingerForce(api):
    hand_id = 0x02
    finger_id = 0x00
    force_entry_cnt = [0]
    force = [0] * MAX_FORCE_ENTRIES
    for i in range(6):
        err, remote_err = api.HAND_GetFingerForce(hand_id, finger_id+i, force_entry_cnt, force, [])
        assert err == HAND_RESP_SUCCESS,f"获取手指当前力量值失败: err={err},remote_err={remote_err}"
        logger.info(f"成功获取手指{finger_id+i} 力量目标值: {force}")

def test_HAND_GetFingerPosLimit(api):
    hand_id = 0x02
    finger_id = 0x00
    low_limit = [0]
    high_limit = [0]
    for i in range(6):
        err, remote_err = api.HAND_GetFingerPosLimit(hand_id, finger_id+i, low_limit, high_limit, [])
        assert err == HAND_RESP_SUCCESS,f"获取手指绝对位置限制值失败: err={err},remote_err={remote_err}"
        logger.info(f"成功获取手指{finger_id+i} 绝对位置限制值: {low_limit[0]}, {high_limit[0]}")

def test_HAND_GetFingerPosAbs(api):
    hand_id = 0x02
    finger_id = 0x00
    target_pos = [0]
    current_pos = [0]
    for i in range(6):
        err, remote_err = api.HAND_GetFingerPosAbs(hand_id, finger_id+i, target_pos, current_pos, [])
        assert err == HAND_RESP_SUCCESS,f"获取手指绝当前绝对位置值失败: err={err},remote_err={remote_err}"
        logger.info(f"成功获取手指{finger_id+i} 当前绝对位置值: {target_pos[0]}, {current_pos[0]}")


def test_HAND_GetFingerPos(api):
    hand_id = 0x02
    finger_id = 0x00
    target_pos = [0]
    current_pos = [0]
    for i in range(6):
        err, remote_err = api.HAND_GetFingerPos(hand_id, finger_id+i, target_pos, current_pos, [])
        assert err == HAND_RESP_SUCCESS,f"获取手指绝当前逻辑位置值失败: err={err},remote_err={remote_err}"
        logger.info(f"成功获取手指{finger_id+i} 当前逻辑位置值: {target_pos[0]}, {current_pos[0]}")

def test_HAND_GetFingerAngle(api):
    hand_id = 0x02
    finger_id = 0x00
    target_angle = [0]
    current_angle = [0]
    for i in range(6):
        err, remote_err = api.HAND_GetFingerAngle(hand_id, finger_id+i, target_angle, current_angle, [])
        assert err == HAND_RESP_SUCCESS,f"获取手指第一关节角度值失败:err={err},remote_err={remote_err}"
        logger.info(f"成功获取手指{finger_id+i} 第一关节角度值: {target_angle[0]}, {current_angle[0]}")

def test_HAND_GetThumbRootPos(api):
    hand_id = 0x02
    raw_encoder = [0]
    pos = [0]
    err, remote_err  = api.HAND_GetThumbRootPos(hand_id, raw_encoder, pos, [])
    assert err == HAND_RESP_SUCCESS,f"获取大拇指旋转预设位置值失败: err={err},remote_err={remote_err}"
    logger.info(f"成功获取大拇指旋转预设位置值: {raw_encoder[0]}, {pos[0]}")

def test_HAND_GetFingerPosAbsAll(api):
    hand_id = 0x02
    target_pos = [0] * MAX_MOTOR_CNT
    current_pos = [0] * MAX_MOTOR_CNT
    motor_cnt = [MAX_MOTOR_CNT]
    err, remote_err = api.HAND_GetFingerPosAbsAll(hand_id, target_pos, current_pos, motor_cnt, [])
    assert err == HAND_RESP_SUCCESS,f"获取所有手指当前的绝对位置值失败: err={err},remote_err={remote_err}"
    logger.info(f"成功获取所有手指当前的绝对位置值: {target_pos}, {current_pos},{motor_cnt}")


def test_HAND_GetFingerPosAll(api):
    hand_id = 0x02
    target_pos = [0] * MAX_MOTOR_CNT
    current_pos = [0] * MAX_MOTOR_CNT
    motor_cnt = [MAX_MOTOR_CNT]
    remote_err = []
    err, remote_err = api.HAND_GetFingerPosAll(hand_id, target_pos, current_pos, motor_cnt, remote_err)
    assert err == HAND_RESP_SUCCESS,f"获取所有手指当前的逻辑位置值失败: err={err},remote_err={remote_err}"
    logger.info(f"成功获取所有手指当前的逻辑位置值: {target_pos}, {current_pos},{motor_cnt}")

def test_HAND_GetFingerAngleAll(api):
    hand_id = 0x02
    target_angle = [0] * MAX_MOTOR_CNT
    current_angle = [0] * MAX_MOTOR_CNT
    motor_cnt = [MAX_MOTOR_CNT]
    err, remote_err = api.HAND_GetFingerAngleAll(hand_id, target_angle, current_angle, motor_cnt, [])
    assert err == HAND_RESP_SUCCESS,f"获取所有手指值失败: err={err},remote_err={remote_err}"
    logger.info(f"成功获取所有手指当前的逻辑位置值: {target_angle}, {current_angle},{motor_cnt}")
    
def test_HAND_GetFingerForcePID(api):
    hand_id = 0x02
    finger_id = 0x00
    p = [0]
    i = [0]
    d = [0]
    g = [0]
    for j in range(5): #拇指旋转没带
        err, remote_err = api.HAND_GetFingerForcePID(hand_id, finger_id+j, p, i, d, g, [])
        assert err == HAND_RESP_SUCCESS,f"获取手指力量p, i, d, g值失败: err={err},remote_err={remote_err}"
        logger.info(f"成功获取手指{finger_id+j} 力量p, i, d, g值: {p[0]}, {i[0]},{d[0]},{g[0]}")

def test_HAND_GetSelfTestLevel(api):
    hand_id = 0x02
    self_test_level = [0]
    err, remote_err = api.HAND_GetSelfTestLevel(hand_id, self_test_level, [])
    assert err == HAND_RESP_SUCCESS,f"获取手自检开关状态失败: err={err},remote_err={remote_err}"
    logger.info(f"成功获取手自检开关状态: {self_test_level[0]}")

def test_HAND_GetBeepSwitch(api):
    hand_id = 0x02
    beep_switch = [0]
    err, remote_err = api.HAND_GetBeepSwitch(hand_id, beep_switch, [])
    assert err == HAND_RESP_SUCCESS,f"获取手蜂鸣器开关状态失败: err={err},remote_err={remote_err}"
    logger.info(f"成功获取手蜂鸣器开关状态: {beep_switch[0]}")

def test_HAND_GetButtonPressedCnt(api):
    hand_id = 0x02
    pressed_cnt = [0]
    err, remote_err = api.HAND_GetButtonPressedCnt(hand_id, pressed_cnt, [])
    assert err == HAND_RESP_SUCCESS,f"获取手按钮按下次数值失败:  err={err},remote_err={remote_err}"
    logger.info(f"成功获取手按钮按下次数值: {pressed_cnt[0]}")

def test_HAND_GetUID(api):
    hand_id = 0x02
    uid_w0 = [0]
    uid_w1 = [0]
    uid_w2 = [0]
    err, remote_err = api.HAND_GetUID(hand_id, uid_w0, uid_w1, uid_w2, [])
    assert err == HAND_RESP_SUCCESS,f"获取手UID值失败: err={err},remote_err={remote_err}"
    logger.info(f"成功获取手UID值: {uid_w0[0]},{uid_w1[0]},{uid_w2[0]}")

def test_HAND_GetBatteryVoltage(api):
    hand_id = 0x02
    voltage = [0]
    err, remote_err = api.HAND_GetBatteryVoltage(hand_id, voltage, [])
    assert err == HAND_RESP_SUCCESS,f"获取手电池电压值失败: err={err},remote_err={remote_err}"
    logger.info(f"成功获取手电池电压值: {voltage[0]}")

def test_HAND_GetUsageStat(api):
    hand_id = 0x02
    total_use_time = [0]
    total_open_times = [0] * MAX_MOTOR_CNT
    motor_cnt = MAX_MOTOR_CNT
    err, remote_err = api.HAND_GetUsageStat(hand_id, total_use_time, total_open_times, motor_cnt, [])
    assert err == HAND_RESP_SUCCESS,f"获取手使用数据值失败: err={err},remote_err={remote_err}"
    logger.info(f"成功获取手使用数据值: {total_use_time[0]},{total_open_times},{motor_cnt}")

# # --------------------------- SET 命令测试 ---------------------------
def test_HAND_Reset(api):
    hand_id = 0x02
    RESET_MODE ={
        '工作模式':0,
        'DFU模式':1
    }
    # mode = 0
    remote_err = []

    err, remote_err = api.HAND_Reset(hand_id, RESET_MODE.get('工作模式'), remote_err)
    assert err == HAND_RESP_SUCCESS,f"设置手重置失败: err={err},remote_err={remote_err}"
    logger.info(f'设置手重置重启到工作模式成功')
    time.sleep(15)
    
    err, remote_err = api.HAND_Reset(hand_id, RESET_MODE.get('DFU模式'), remote_err)
    assert err == HAND_RESP_SUCCESS,f"设置手重置失败: err={err},remote_err={remote_err}"
    logger.info(f'设置手重置重启到DFU模式成功')
    time.sleep(15)
    
    logger.info('恢复默认值')
    err, remote_err = api.HAND_Reset(hand_id, RESET_MODE.get('工作模式'), remote_err)
    assert err == HAND_RESP_SUCCESS,f"恢复默认值失败: err={err},remote_err={remote_err}"
    logger.info('恢复默认值成功')
    
@pytest.mark.skip('Rohand 暂时跳过关机接口测试，单独测试pass')
def test_HAND_PowerOff(api):
    hand_id = 0x02
    remote_err = []

    err, remote_err = api.HAND_PowerOff(hand_id, remote_err)
    assert err == HAND_RESP_SUCCESS,f"设置关机失败: err={err},remote_err={remote_err}"
    logger.info('设置关机成功成功')


@pytest.mark.skip('先跳过设备ID的修改')  
def test_HAND_SetID(api):
    """测试设置设备ID功能（适配API实际方法，移除HAND_GetID依赖）"""
    original_hand_id = 0x02  # 初始默认ID
    test_results = []
    
    # 保存原始API的私有数据用于重建连接
    private_data = api.get_private_data() if hasattr(api, 'get_private_data') else None
    print('111')
    try:
        # 定义测试数据（ID范围：2-247为有效）
        test_cases = [
            (3,     "hand id最小值2（有效）"),
            (125,   "hand id中间值125（有效）"),
            (247,   "hand id最大值247（有效）"),
            (1,     "hand id边界值1（无效）"),
            (0,     "hand id边界值0（无效）"),
            (-1,    "hand id边界值-1（无效）"),
            (248,   "hand id边界值248（无效）"),
            (256,   "hand id边界值256（无效）"),
        ]
        
        for new_id, desc in test_cases:
            logger.info(f"\n----- 测试 {desc} -----")
            remote_err = []
            
            # 发送设置ID命令（使用API中实际存在的HAND_SetNodeID对应方法）
            set_err, set_remote_err = api.HAND_SetID(original_hand_id, new_id, remote_err)
            print('2222')
            # 处理有效ID（2-247）
            if 3 <= new_id <= 247:
                # 验证设置命令是否成功
                assert set_err == HAND_RESP_SUCCESS, \
                    f"有效ID设置命令失败: {desc}, 错误码: {set_err}, 远程错误: {set_remote_err}"
                print('333')
                # 设备重启等待（根据实际重启时间调整）
                logger.info(f"等待设备重启（新ID: {new_id}）...")
                time.sleep(5)
                print('4444')
                # 关闭当前连接
                if hasattr(api, 'shutdown'):
                    api.shutdown()
                CAN_Shutdown(private_data)
                print('555')
                # 重建连接（使用新ID）并验证是否能通信
                new_private_data = CAN_Init(port_name="1", baudrate=1000000)
                assert new_private_data is not None, "CAN总线初始化失败"
                print('666')
                # 创建新API实例（使用新ID）
                new_api = OHandSerialAPI(
                    private_data=new_private_data,
                    protocol=0,  # HAND_PROTOCOL_UART
                    address_master=new_id,
                    send_data_impl=send_data_impl,
                    recv_data_impl=recv_data_impl
                )
                new_api.HAND_SetTimerFunction(get_milli_seconds_impl, delay_milli_seconds_impl)
                new_api.HAND_SetCommandTimeOut(255)
                
                # 间接验证新ID生效：通过查询其他基础信息（如协议版本）判断连接有效性
                major, minor = [0], [0]
                verify_err, _ = new_api.HAND_GetProtocolVersion(new_id, major, minor, [])
                assert verify_err == HAND_RESP_SUCCESS, \
                    f"新ID {new_id} 通信失败，验证协议版本错误: {verify_err}"
                
                test_results.append((f"ID测试({desc})", "通过"))
                logger.info(f"新ID {new_id} 验证成功（通信正常）")
                
                # 恢复原始ID
                recover_err, _ = new_api.HAND_SetID(new_id, original_hand_id, [])
                assert recover_err == HAND_RESP_SUCCESS, \
                    f"恢复原始ID命令失败，错误码: {recover_err}"
                
                # 等待恢复后重启
                logger.info(f"等待设备恢复原始ID {original_hand_id}...")
                time.sleep(5)
                
                # 关闭当前连接
                if hasattr(new_api, 'shutdown'):
                    new_api.shutdown()
                CAN_Shutdown(new_private_data)
                
                # 重建原始ID连接
                private_data = CAN_Init(port_name="1", baudrate=1000000)
                assert private_data is not None, "CAN总线初始化失败"
                
                api = OHandSerialAPI(
                    private_data=private_data,
                    protocol=0,
                    address_master=original_hand_id,
                    send_data_impl=send_data_impl,
                    recv_data_impl=recv_data_impl
                )
                api.HAND_SetTimerFunction(get_milli_seconds_impl, delay_milli_seconds_impl)
                api.HAND_SetCommandTimeOut(255)
                
                # 验证原始ID恢复：查询协议版本判断连接
                major, minor = [0], [0]
                recover_verify_err, _ = api.HAND_GetProtocolVersion(original_hand_id, major, minor, [])
                assert recover_verify_err == HAND_RESP_SUCCESS, \
                    f"原始ID {original_hand_id} 恢复失败，通信错误: {recover_verify_err}"
                logger.info(f"原始ID {original_hand_id} 恢复成功（通信正常）")
            
            # 处理无效ID（超出2-247范围）
            else:
                # 验证设置命令是否被拒绝
                assert set_err != HAND_RESP_SUCCESS, \
                    f"无效ID设置未被拒绝: {desc}, 错误码: {set_err}, 远程错误: {set_remote_err}"
                
                # 验证原始ID仍能通信（未被修改）
                major, minor = [0], [0]
                check_err, _ = api.HAND_GetProtocolVersion(original_hand_id, major, minor, [])
                assert check_err == HAND_RESP_SUCCESS, \
                    f"无效ID设置后原始ID通信失败，错误码: {check_err}"
                
                test_results.append((f"ID测试({desc})", "通过（预期失败）"))
    
    except AssertionError as e:
        logger.error(f"测试断言失败: {str(e)}")
        test_results.append(("全局断言", f"失败: {str(e)}"))
        raise
    except Exception as e:
        logger.error(f"测试异常: {str(e)}")
        test_results.append(("全局异常", f"失败: {str(e)}"))
        raise
    finally:
        # 最终确保设备恢复为原始ID并验证
        try:
            logger.info("\n----- 最终恢复原始ID -----")
            if hasattr(api, 'shutdown'):
                api.shutdown()
            CAN_Shutdown(private_data)
            
            # 重建原始ID连接
            private_data = CAN_Init(port_name="1", baudrate=1000000)
            api = OHandSerialAPI(
                private_data=private_data,
                protocol=0,
                address_master=original_hand_id,
                send_data_impl=send_data_impl,
                recv_data_impl=recv_data_impl
            )
            api.HAND_SetTimerFunction(get_milli_seconds_impl, delay_milli_seconds_impl)
            
            # 恢复原始ID命令
            final_err, _ = api.HAND_SetID(original_hand_id, original_hand_id, [])
            time.sleep(3)
            
            # 验证最终状态
            major, minor = [0], [0]
            final_verify_err, _ = api.HAND_GetProtocolVersion(original_hand_id, major, minor, [])
            if final_verify_err == HAND_RESP_SUCCESS:
                logger.info(f"最终恢复原始ID {original_hand_id} 成功（通信正常）")
            else:
                logger.warning(f"最终恢复原始ID失败，通信错误: {final_verify_err}")
        except Exception as e:
            logger.error(f"最终恢复原始ID异常: {str(e)}")
        
        # 测试结果汇总
        logger.info("\n===== 设置设备ID测试结果汇总 =====")
        passed = sum(1 for case, result in test_results if "通过" in result)
        total = len(test_results)
        logger.info(f"总测试用例: {total}, 通过: {passed}, 失败: {total - passed}")
        for case, result in test_results:
            logger.info(f"{case}: {result}")
        logger.info("=======================")
            
# @pytest.mark.skip('测试设置pid一直报超时，此case暂时跳过')
def test_HAND_SetFingerPID(api):
    ######
    # api.HAND_SetCommandTimeOut(500)
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
            (100,   "P值最小值100"),
            (24000, "P值中间值24000"),
            (50000, "P值最大值50000"),
            (99,    "P值边界值99"),
            (0,     "P值边界值0"),
            (-1,    "P值边界值-1"),
            (50001, "P值边界值50001"),
            (65535, "P值边界值65535"),
            (65536, "P值边界值65536")
        ],
        'I': [
            (0,     "I值最小值0"),
            (5000,  "I值中间值5000"),
            (10000, "I值最大值10000"),
            (-1,    "I值边界值-1"),
            (10001, "I值边界值10001"),
            (65535, "I值边界值65535"),
            (65536, "I值边界值65536")
        ],
        'D': [
            (0,     "D值最小值0"),
            (25001, "D值中间值25001"),
            (50000, "D值最大值50000"),
            (-1,    "D值边界值-1"),
            (50001, "D值边界值50001"),
            (65535, "D值边界值65535"),
            (65536, "D值边界值65536")
        ],
        'G': [
            (1,     "G值最小值1"),
            (50,    "G值中间值50"),
            (100,   "G值最大值100"),
            (0,     "G值边界值0"),
            (-1,    "G值边界值-1"),
            (101,   "G值边界值101"),
            (65535, "G值边界值65535"),
            (65536, "G值边界值65536")
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
                err,remote_err = api.HAND_SetFingerPID(
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
                        f"手指 {finger_id} 设置有效P值失败: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} P值测试({desc})", "通过"))
                else:  # 无效P值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效P值未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} P值测试({desc})", "通过(预期失败)"))
            
            # 测试I参数
            logger.info(f"测试手指 {finger_id} 的I参数")
            for i_value, desc in PARAM_TEST_DATA['I']:
                remote_err = []
                err, remote_err = api.HAND_SetFingerPID(
                    HAND_ID, finger_id, 
                    DEFAULT_P,      # P固定为默认值
                    i_value,        # 测试变量I
                    DEFAULT_D,      # D固定为默认值
                    DEFAULT_G,      # G固定为默认值
                    remote_err
                )
                # 验证结果
                if 0 <= i_value <= 10000:  # 有效I值范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效I值失败: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} I值测试({desc})", "通过"))
                else:
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效I值未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} I值测试({desc})", "通过(预期失败)"))
            
            # 测试D参数(代码结构与I参数测试类似)
            logger.info(f"测试手指 {finger_id} 的D参数")
            for d_value, desc in PARAM_TEST_DATA['D']:
                remote_err = []
                err, remote_err  = api.HAND_SetFingerPID(
                    HAND_ID, finger_id, 
                    DEFAULT_P,      # P固定为默认值
                    DEFAULT_I,      # I固定为默认值
                    d_value,        # 测试变量d
                    DEFAULT_G,      # G固定为默认值
                    remote_err
                )
                # 验证结果
                if 0 <= d_value <= 50000:  # 有效D值范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效D值失败: {desc}, 错误码:  err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} D值测试({desc})", "通过"))
                else:
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效D值未报错: {desc}, 错误码:  err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} D值测试({desc})", "通过(预期失败)"))
                    
            # 测试G参数(代码结构与I参数测试类似)
            logger.info(f"测试手指 {finger_id} 的G参数")
            for g_value, desc in PARAM_TEST_DATA['G']:
                remote_err = []
                err, remote_err = api.HAND_SetFingerPID(
                    HAND_ID, finger_id, 
                    DEFAULT_P,      # P固定为默认值
                    DEFAULT_I,      # I固定为默认值
                    DEFAULT_D,      # D固定为默认值
                    g_value,        # 测试变量g
                    remote_err
                )
                # 验证结果
                if 1 <= g_value <= 100:  # 有效G值范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效G值失败: {desc}, 错误码:err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} G值测试({desc})", "通过"))
                else:
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效G值未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} G值测试({desc})", "通过(预期失败)"))
            
            logger.info(f"手指 {finger_id} 所有参数测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指的默认PIDG值 =====")
        for finger_id in FINGERS:
            remote_err = []
            err, remote_err = api.HAND_SetFingerPID(
                HAND_ID, finger_id, 
                DEFAULT_P, DEFAULT_I, DEFAULT_D, DEFAULT_G, remote_err
            )
            assert err == HAND_RESP_SUCCESS, \
                f"恢复手指 {finger_id} 默认值失败, 错误码: err={err},remote_err={remote_err}"
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

# @pytest.mark.skip('测试设置current limit一直报超时,此case暂时跳过')
def test_HAND_SetFingerCurrentLimit(api):
    # 定义测试常量
    HAND_ID = 0x02
    FINGERS = [0, 1, 2, 3, 4, 5]  # 6个手指ID
    
    # 默认参数值
    DEFAULT_CURRENT = 1299
    
    # 定义各参数的测试值(包含有效/边界/无效值)
    PARAM_TEST_DATA = {
        'current_limit': [
            (0,     "电流最小值0"),
            (600,   "电流中间值600"),
            (1299,  "电流最大值1299"),
            (-1,    "电流边界值-1"),
            (1300,  "电流边界值1300"),
            (65535, "电流边界值65535"),
            (65536, "电流边界值65536")
        ]
    }
    
    # 测试结果存储
    test_results = []
    
    try:
        """------------------- 单变量测试 -------------------"""
        for finger_id in FINGERS:
            logger.info(f"\n===== 开始测试手指 {finger_id} 的电流限制 =====")
            
            # 测试电流限制参数
            for current_limit, desc in PARAM_TEST_DATA['current_limit']:
                remote_err = []
                err, remote_err = api.HAND_SetFingerCurrentLimit(
                    HAND_ID, finger_id, 
                    current_limit,  # 测试变量电流限制值
                    remote_err
                )
                
                # 验证结果（假设有效范围：0-1299）
                if 0 <= current_limit <= 1299:  # 有效电流范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效电流值失败: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} 电流测试({desc})", "通过"))
                else:  # 无效电流值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效电流值未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} 电流测试({desc})", "通过(预期失败)"))
            
            logger.info(f"手指 {finger_id} 电流限制测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指的默认电流限制 =====")
        for finger_id in FINGERS:
            remote_err = []
            err,remote_err = api.HAND_SetFingerCurrentLimit(
                HAND_ID, finger_id, 
                DEFAULT_CURRENT, remote_err
            )
            assert err == HAND_RESP_SUCCESS, \
                f"恢复手指 {finger_id} 默认电流失败, 错误码:err={err},remote_err={remote_err}"
            logger.info(f"手指 {finger_id} 已恢复默认电流值: {DEFAULT_CURRENT}")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复所有手指默认值
        try:
            logger.warning("正在尝试恢复所有手指默认电流值...")
            for finger_id in FINGERS:
                api.HAND_SetFingerCurrentLimit(
                    HAND_ID, finger_id, 
                    DEFAULT_CURRENT, []
                )
        except Exception as recovery_err:
            logger.error(f"恢复默认电流值失败: {str(recovery_err)}")
        raise  # 重新抛出原始错误
    
    finally:
        """------------------- 测试结果汇总 -------------------"""
        logger.info("\n===== 电流限制测试结果汇总 =====")
        passed = sum(1 for case, result in test_results if "通过" in result)
        total = len(test_results)
        logger.info(f"总测试用例: {total}, 通过: {passed}, 失败: {total - passed}")
        
        for case, result in test_results:
            logger.info(f"{case}: {result}")
        logger.info("=======================")

# @pytest.mark.skip('测试设置force target一直报超时,此case暂时跳过')
def test_HAND_SetFingerForceTarget(api):
    # 定义测试常量
    HAND_ID = 0x02
    FINGERS = [0, 1, 2, 3, 4, 5]  # 6个手指ID
    
    # 默认参数值
    DEFAULT_FORCE_TARGET = 0
    
    # 定义各参数的测试值(包含有效/边界/无效值)
    PARAM_TEST_DATA = {
        'force_target': [
            (0,          "目标力最小值0"),
            (1,          "目标力值1"),
            (32767,      "目标力中间值32767"),
            (65535,      "目标力最大值65535"),
            (-1,         "目标力边界值-1"),
            (65536,      "目标力边界值65536")
        ]
    }
    
    # 测试结果存储
    test_results = []
    
    try:
        """------------------- 单变量测试 -------------------"""
        for finger_id in FINGERS:
            logger.info(f"\n===== 开始测试手指 {finger_id} 的目标力设置 =====")
            
            # 测试目标力参数
            for force_target, desc in PARAM_TEST_DATA['force_target']:
                remote_err = []
                err, remote_err = api.HAND_SetFingerForceTarget(
                    HAND_ID, finger_id, 
                    force_target,  # 测试变量目标力值
                    remote_err
                )
                
                # 验证结果（假设有效范围：0-65535）
                if 0 <= force_target <= 65535:  # 有效目标力范围（16位无符号整数）
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效目标力失败: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} 目标力测试({desc})", "通过"))
                else:  # 无效目标力值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效目标力未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} 目标力测试({desc})", "通过(预期失败)"))
            
            logger.info(f"手指 {finger_id} 目标力设置测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指的默认目标力 =====")
        for finger_id in FINGERS:
            remote_err = []
            err, remote_err = api.HAND_SetFingerForceTarget(
                HAND_ID, finger_id, 
                DEFAULT_FORCE_TARGET, remote_err
            )
            assert err == HAND_RESP_SUCCESS, \
                f"恢复手指 {finger_id} 默认目标力失败, 错误码: err={err},remote_err={remote_err}"
            logger.info(f"手指 {finger_id} 已恢复默认目标力: {DEFAULT_FORCE_TARGET}")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复所有手指默认值
        try:
            logger.warning("正在尝试恢复所有手指默认目标力...")
            for finger_id in FINGERS:
                api.HAND_SetFingerForceTarget(
                    HAND_ID, finger_id, 
                    DEFAULT_FORCE_TARGET, []
                )
        except Exception as recovery_err:
            logger.error(f"恢复默认目标力失败: {str(recovery_err)}")
        raise  # 重新抛出原始错误
    
    finally:
        """------------------- 测试结果汇总 -------------------"""
        logger.info("\n===== 目标力设置测试结果汇总 =====")
        passed = sum(1 for case, result in test_results if "通过" in result)
        total = len(test_results)
        logger.info(f"总测试用例: {total}, 通过: {passed}, 失败: {total - passed}")
        
        for case, result in test_results:
            logger.info(f"{case}: {result}")
        logger.info("=======================")

# @pytest.mark.skip('测试设置pos limit 一直报超时,此case暂时跳过')
def test_HAND_SetFingerPosLimit(api):
    # 定义测试常量
    HAND_ID = 0x02
    FINGERS = [0, 1, 2, 3, 4, 5]  # 6个手指ID
    
    # 默认参数值（范围0-65535，默认值0）
    DEFAULT_POS_LIMIT = 0
    
    # 定义参数的测试值(包含有效/边界/无效值)
    PARAM_TEST_DATA = {
        'pos_limit': [
            (0,          "目标位置最小值0"),
            (1,          "目标位置值1"),
            (32767,      "目标位置中间值32767"),
            (65535,      "目标位置最大值65535"),
            (-1,         "目标位置边界值-1"),
            (65536,      "目标位置边界值65536")
        ]
    }
    
    # 测试结果存储
    test_results = []
    
    try:
        """------------------- 单变量测试 -------------------"""
        for finger_id in FINGERS:
            logger.info(f"\n===== 开始测试手指 {finger_id} 的位置限制 =====")
            
            # 测试位置限制参数
            for pos_limit, desc in PARAM_TEST_DATA['pos_limit']:
                remote_err = []
                err, remote_err = api.HAND_SetFingerPosLimit(
                    HAND_ID, finger_id, 
                    pos_limit,  # 测试变量位置限制值
                    remote_err
                )
                
                # 验证结果
                if 0 <= pos_limit <= 65535:  # 有效范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效位置限制失败: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} 位置限制测试({desc})", "通过"))
                else:  # 无效值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效位置限制未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} 位置限制测试({desc})", "通过(预期失败)"))
            
            logger.info(f"手指 {finger_id} 位置限制测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指的默认位置限制 =====")
        for finger_id in FINGERS:
            remote_err = []
            err, remote_err = api.HAND_SetFingerPosLimit(
                HAND_ID, finger_id, 
                DEFAULT_POS_LIMIT,  # 恢复默认值
                remote_err
            )
            assert err == HAND_RESP_SUCCESS, \
                f"恢复手指 {finger_id} 默认位置限制失败, 错误码: err={err},remote_err={remote_err}"
            logger.info(f"手指 {finger_id} 已恢复默认位置限制: {DEFAULT_POS_LIMIT}")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复所有手指默认值
        try:
            logger.warning("正在尝试恢复所有手指默认位置限制...")
            for finger_id in FINGERS:
                api.HAND_SetFingerPosLimit(
                    HAND_ID, finger_id, 
                    DEFAULT_POS_LIMIT, 
                    []
                )
        except Exception as recovery_err:
            logger.error(f"恢复默认位置限制失败: {str(recovery_err)}")
        raise  # 重新抛出原始错误
    
    finally:
        """------------------- 测试结果汇总 -------------------"""
        logger.info("\n===== 位置限制测试结果汇总 =====")
        passed = sum(1 for case, result in test_results if "通过" in result)
        total = len(test_results)
        logger.info(f"总测试用例: {total}, 通过: {passed}, 失败: {total - passed}")
        
        for case, result in test_results:
            logger.info(f"{case}: {result}")
        logger.info("=======================")

# @pytest.mark.skip('单独跑测试是可以通过，研发后续会优化代码，暂时跳过')
def test_HAND_FingerStart(api):
    hand_id = 0x02
    finger_id_bits = 0x01
    remote_err = []

    err, remote_err = api.HAND_FingerStart(hand_id, finger_id_bits, remote_err)
    assert err == HAND_RESP_SUCCESS, f"设置开始移动手指失败，错误码: err={err},remote_err={remote_err}"
    logger.info(f'设置开始移动手指成功')
    
# @pytest.mark.skip('单独跑测试是可以通过，研发后续会优化代码，暂时跳过')
def test_HAND_FingerStop(api):
    hand_id = 0x02
    finger_id_bits = 0x01
    remote_err = []

    err, remote_err = api.HAND_FingerStop(hand_id, finger_id_bits, remote_err)
    assert err == HAND_RESP_SUCCESS, f"设置停止移动手指失败，错误码: err={err},remote_err={remote_err}"
    logger.info(f'设置停止移动手指成功')

# @pytest.mark.skip('测试设置finger pos abs 一直报超时,此case暂时跳过')
def test_HAND_SetFingerPosAbs(api):
    # 定义测试常量
    HAND_ID = 0x02
    FINGERS = [0, 1, 2, 3, 4, 5]  # 6个手指ID
    
    # 默认参数值（速度范围调整为0-65535）
    DEFAULT_POS = 0
    DEFAULT_SPEED = 127  # 速度默认值调整为32767
    
    # 定义各参数的测试值(包含有效/边界/无效值)
    PARAM_TEST_DATA = {
        'raw_pos': [
            (0,       "手指绝对位置最小值0"),
            (32767,   "手指绝对位置中间值32767"),
            (65535,   "手指绝对位置最大值65535"),
            (-1,      "手指绝对位置边界值-1"),
            (65536,   "手指绝对位置边界值65536")
        ],
        'speed': [
            (0,       "手指移动速度最小值0"),
            (127,     "手指移动速度中间值127"),
            (255,     "手指移动速度最大值255"),
            (-1,      "手指移动速度边界值-1"),
            (256,     "手指移动速度边界值256")
        ]
    }
    
    # 测试结果存储
    test_results = []
    
    try:
        """------------------- 单变量测试 -------------------"""
        for finger_id in FINGERS:
            logger.info(f"\n===== 开始测试手指 {finger_id} 的绝对位置设置 =====")
            
            # 测试位置参数（固定速度为默认值）
            logger.info(f"测试手指 {finger_id} 的位置参数")
            for raw_pos, desc in PARAM_TEST_DATA['raw_pos']:
                remote_err = []
                err, remote_err = api.HAND_SetFingerPosAbs(
                    HAND_ID, finger_id, 
                    raw_pos,      # 测试变量位置值
                    DEFAULT_SPEED,  # 速度固定为默认值
                    remote_err
                )
                
                # 验证结果
                if 0 <= raw_pos <= 65535:  # 有效位置范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效位置失败: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} 位置测试({desc})", "通过"))
                else:  # 无效位置值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效位置未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} 位置测试({desc})", "通过(预期失败)"))
            
            # 测试速度参数（固定位置为默认值）
            logger.info(f"测试手指 {finger_id} 的速度参数")
            for speed, desc in PARAM_TEST_DATA['speed']:
                remote_err = []
                err, remote_err = api.HAND_SetFingerPosAbs(
                    HAND_ID, finger_id, 
                    DEFAULT_POS,  # 位置固定为默认值
                    speed,        # 测试变量速度值
                    remote_err
                )
                
                # 验证结果
                if 0 <= speed <= 255:  # 有效速度范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效速度失败: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} 速度测试({desc})", "通过"))
                else:  # 无效速度值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效速度未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} 速度测试({desc})", "通过(预期失败)"))
            
            logger.info(f"手指 {finger_id} 绝对位置设置测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指的默认位置 =====")
        for finger_id in FINGERS:
            remote_err = []
            err, remote_err = api.HAND_SetFingerPosAbs(
                HAND_ID, finger_id, 
                DEFAULT_POS, DEFAULT_SPEED,  # 恢复默认位置和速度
                remote_err
            )
            assert err == HAND_RESP_SUCCESS, \
                f"恢复手指 {finger_id} 默认位置失败, 错误码: err={err},remote_err={remote_err}"
            logger.info(f"手指 {finger_id} 已恢复默认位置: {DEFAULT_POS}, 速度: {DEFAULT_SPEED}")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复所有手指默认值
        try:
            logger.warning("正在尝试恢复所有手指默认位置...")
            for finger_id in FINGERS:
                api.HAND_SetFingerPosAbs(
                    HAND_ID, finger_id, 
                    DEFAULT_POS, DEFAULT_SPEED, 
                    []
                )
        except Exception as recovery_err:
            logger.error(f"恢复默认位置失败: {str(recovery_err)}")
        raise  # 重新抛出原始错误
    
    finally:
        """------------------- 测试结果汇总 -------------------"""
        logger.info("\n===== 绝对位置设置测试结果汇总 =====")
        passed = sum(1 for case, result in test_results if "通过" in result)
        total = len(test_results)
        logger.info(f"总测试用例: {total}, 通过: {passed}, 失败: {total - passed}")
        
        for case, result in test_results:
            logger.info(f"{case}: {result}")
        logger.info("=======================")

# @pytest.mark.skip('测试设置finger pos 一直报超时,此case暂时跳过')
def test_HAND_SetFingerPos(api):
    # 定义测试常量
    HAND_ID = 0x02
    FINGERS = [0, 1, 2, 3, 4, 5]  # 6个手指ID
    
    # 默认参数值
    DEFAULT_POS = 0     # 位置默认值
    DEFAULT_SPEED = 127   # 速度默认值32767
    
    # 定义各参数的测试值(包含有效/边界/无效值)
    PARAM_TEST_DATA = {
        'pos': [
            (0,       "手指逻辑位置最小值0"),
            (32767,   "手指逻辑位置中间值32767"),
            (65535,   "手指逻辑位置最大值65535"),
            (-1,      "手指逻辑位置边界值-1"),
            (65536,   "手指逻辑位置边界值65536")
        ],
        'speed': [
            (0,       "手指移动速度最小值0"),
            (127,     "手指移动速度中间值127"),
            (255,     "手指移动速度最大值255"),
            (-1,      "手指移动速度边界值-1"),
            (256,     "手指移动速度边界值256")
        ]
    }
    
    # 测试结果存储
    test_results = []
    
    try:
        """------------------- 单变量测试 -------------------"""
        for finger_id in FINGERS:
            logger.info(f"\n===== 开始测试手指 {finger_id} 的相对位置设置 =====")
            
            # 测试位置参数（固定速度为默认值）
            logger.info(f"测试手指 {finger_id} 的位置参数")
            for pos, desc in PARAM_TEST_DATA['pos']:
                remote_err = []
                err, remote_err = api.HAND_SetFingerPos(
                    HAND_ID, finger_id, 
                    pos,          # 测试变量位置值
                    DEFAULT_SPEED,  # 速度固定为默认值
                    remote_err
                )
                
                # 验证结果
                if 0 <= pos <= 65535:  # 有效位置范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效位置失败: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} 位置测试({desc})", "通过"))
                else:  # 无效位置值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效位置未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} 位置测试({desc})", "通过(预期失败)"))
            
            # 测试速度参数（固定位置为默认值）
            logger.info(f"测试手指 {finger_id} 的速度参数")
            for speed, desc in PARAM_TEST_DATA['speed']:
                remote_err = []
                err, remote_err = api.HAND_SetFingerPos(
                    HAND_ID, finger_id, 
                    DEFAULT_POS,  # 位置固定为默认值
                    speed,        # 测试变量速度值
                    remote_err
                )
                
                # 验证结果
                if 0 <= speed <= 255:  # 有效速度范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效速度失败: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} 速度测试({desc})", "通过"))
                else:  # 无效速度值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效速度未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} 速度测试({desc})", "通过(预期失败)"))
            
            logger.info(f"手指 {finger_id} 相对位置设置测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指的默认位置 =====")
        for finger_id in FINGERS:
            remote_err = []
            err, remote_err = api.HAND_SetFingerPos(
                HAND_ID, finger_id, 
                DEFAULT_POS, DEFAULT_SPEED,  # 恢复默认位置和速度
                remote_err
            )
            assert err == HAND_RESP_SUCCESS, \
                f"恢复手指 {finger_id} 默认位置失败, 错误码: err={err},remote_err={remote_err}"
            logger.info(f"手指 {finger_id} 已恢复默认位置: {DEFAULT_POS}, 速度: {DEFAULT_SPEED}")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复所有手指默认值
        try:
            logger.warning("正在尝试恢复所有手指默认位置...")
            for finger_id in FINGERS:
                api.HAND_SetFingerPos(
                    HAND_ID, finger_id, 
                    DEFAULT_POS, DEFAULT_SPEED, 
                    []
                )
        except Exception as recovery_err:
            logger.error(f"恢复默认位置失败: {str(recovery_err)}")
        raise  # 重新抛出原始错误
    
    finally:
        """------------------- 测试结果汇总 -------------------"""
        logger.info("\n===== 相对位置设置测试结果汇总 =====")
        passed = sum(1 for case, result in test_results if "通过" in result)
        total = len(test_results)
        logger.info(f"总测试用例: {total}, 通过: {passed}, 失败: {total - passed}")
        
        for case, result in test_results:
            logger.info(f"{case}: {result}")
        logger.info("=======================")

# @pytest.mark.skip('测试设置finger angle 一直报超时,此case暂时跳过')
def test_HAND_SetFingerAngle(api):
    # 定义测试常量
    HAND_ID = 0x02
    FINGERS = [0, 1, 2, 3, 4, 5]  # 6个手指ID
    
    # 默认参数值
    DEFAULT_ANGLE = 0     # 角度默认值
    DEFAULT_SPEED = 127     # 速度默认值
    
    # 定义各参数的测试值(包含有效/边界/无效值)
    PARAM_TEST_DATA = {
        'angle': [
            (0,       "手指角度最小值0"),
            (16384,   "手指角度中间值16384"),
            (32767,   "手指角度最大值32767"),
            (32768,   "手指角度负数最大值32768"),
            (65535,   "手指角度负数最小值65535"),
            (-1,      "手指角度边界值-1"),
            (65536,   "手指角度边界值-165536"),
        ],
       'speed': [
            (0,       "手指移动速度最小值0"),
            (127,     "手指移动速度中间值127"),
            (255,     "手指移动速度最大值255"),
            (-1,      "手指移动速度边界值-1"),
            (256,     "手指移动速度边界值256")
        ]
    }
    
    # 测试结果存储
    test_results = []
    
    try:
        """------------------- 单变量测试 -------------------"""
        for finger_id in FINGERS:
            logger.info(f"\n===== 开始测试手指 {finger_id} 的角度设置 =====")
            
            # 测试角度参数（固定速度为默认值）
            logger.info(f"测试手指 {finger_id} 的角度参数")
            for angle, desc in PARAM_TEST_DATA['angle']:
                remote_err = []
                err, remote_err = api.HAND_SetFingerAngle(
                    HAND_ID, finger_id, 
                    angle,          # 测试变量角度值
                    DEFAULT_SPEED,  # 速度固定为默认值
                    remote_err
                )
                
                # 验证结果
                if 0 <= angle <= 65535:  # 有效角度范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效角度失败: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} 角度测试({desc})", "通过"))
                else:  # 无效角度值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效角度未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} 角度测试({desc})", "通过(预期失败)"))
            
            # 测试速度参数（固定角度为默认值）
            logger.info(f"测试手指 {finger_id} 的速度参数")
            for speed, desc in PARAM_TEST_DATA['speed']:
                remote_err = []
                err, remote_err = api.HAND_SetFingerAngle(
                    HAND_ID, finger_id, 
                    DEFAULT_ANGLE,  # 角度固定为默认值
                    speed,          # 测试变量速度值
                    remote_err
                )
                
                # 验证结果
                if 0 <= speed <= 255:  # 有效速度范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效速度失败: {desc}, 错误码:err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} 速度测试({desc})", "通过"))
                else:  # 无效速度值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效速度未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} 速度测试({desc})", "通过(预期失败)"))
            
            logger.info(f"手指 {finger_id} 角度设置测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指的默认角度 =====")
        for finger_id in FINGERS:
            remote_err = []
            err, remote_err = api.HAND_SetFingerAngle(
                HAND_ID, finger_id, 
                DEFAULT_ANGLE, DEFAULT_SPEED,  # 恢复默认角度和速度
                remote_err
            )
            assert err == HAND_RESP_SUCCESS, \
                f"恢复手指 {finger_id} 默认角度失败, 错误码: err={err},remote_err={remote_err}"
            logger.info(f"手指 {finger_id} 已恢复默认角度: {DEFAULT_ANGLE}, 速度: {DEFAULT_SPEED}")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复所有手指默认值
        try:
            logger.warning("正在尝试恢复所有手指默认角度...")
            for finger_id in FINGERS:
                api.HAND_SetFingerAngle(
                    HAND_ID, finger_id, 
                    DEFAULT_ANGLE, DEFAULT_SPEED, 
                    []
                )
        except Exception as recovery_err:
            logger.error(f"恢复默认角度失败: {str(recovery_err)}")
        raise  # 重新抛出原始错误
    
    finally:
        """------------------- 测试结果汇总 -------------------"""
        logger.info("\n===== 角度设置测试结果汇总 =====")
        passed = sum(1 for case, result in test_results if "通过" in result)
        total = len(test_results)
        logger.info(f"总测试用例: {total}, 通过: {passed}, 失败: {total - passed}")
        
        for case, result in test_results:
            logger.info(f"{case}: {result}")
        logger.info("=======================")

# @pytest.mark.skip('测试设置thumb root pos 一直报超时,此case暂时跳过')
def test_HAND_SetThumbRootPos(api):
    # 定义测试常量
    HAND_ID = 0x02
    
    # 默认参数值
    DEFAULT_POS = 0     # 位置默认值（合法值：0, 1, 2）
    DEFAULT_SPEED = 127   # 速度默认值（范围：0-255）
    
    # 定义各参数的测试值(包含有效/边界/无效值)
    PARAM_TEST_DATA = {
        'thumb_root_pos': [
            (0,     "旋转大拇指到预设位置值0"),
            (1,     "旋转大拇指到预设位置值1"),
            (2,     "旋转大拇指到预设位置值2"),
            (-1,    "旋转大拇指到预设位置边界值-1"),
            (3,     "旋转大拇指到预设位置边界值3"),
        ],
        'speed': [
            (0,       "手指移动速度最小值0"),
            (127,     "手指移动速度中间值127"),
            (255,     "手指移动速度最大值255"),
            (-1,      "手指移动速度边界值-1"),
            (256,     "手指移动速度边界值256")
        ]
    }
    
    # 测试结果存储
    test_results = []
    
    try:
        """------------------- 单变量测试 -------------------"""
        logger.info(f"\n===== 开始测试拇指根部位置设置 =====")
        
        # 测试位置参数（固定速度为默认值）
        logger.info(f"测试拇指根部位置参数")
        for pos, desc in PARAM_TEST_DATA['thumb_root_pos']:
            remote_err = []
            err, remote_err = api.HAND_SetThumbRootPos(
                HAND_ID, 
                pos,              # 测试变量位置值
                DEFAULT_SPEED,    # 速度固定为默认值
                remote_err
            )
            
            # 验证结果
            if pos in [0, 1, 2]:  # 有效位置范围
                assert err == HAND_RESP_SUCCESS, \
                    f"设置拇指根部有效位置失败: {desc}, 错误码: err={err},remote_err={remote_err}"
                test_results.append((f"拇指根部位置测试({desc})", "通过"))
            else:  # 无效位置值
                assert err != HAND_RESP_SUCCESS, \
                    f"设置拇指根部无效位置未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                test_results.append((f"拇指根部位置测试({desc})", "通过(预期失败)"))
        
        # 测试速度参数（固定位置为默认值）
        logger.info(f"测试拇指根部速度参数")
        for speed, desc in PARAM_TEST_DATA['speed']:
            remote_err = []
            err, remote_err = api.HAND_SetThumbRootPos(
                HAND_ID, 
                DEFAULT_POS,      # 位置固定为默认值
                speed,            # 测试变量速度值
                remote_err
            )
            
            # 验证结果
            if 0 <= speed <= 255:  # 有效速度范围
                assert err == HAND_RESP_SUCCESS, \
                    f"设置拇指根部有效速度失败: {desc}, 错误码: err={err},remote_err={remote_err}"
                test_results.append((f"拇指根部速度测试({desc})", "通过"))
            else:  # 无效速度值
                assert err != HAND_RESP_SUCCESS, \
                    f"设置拇指根部无效速度未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                test_results.append((f"拇指根部速度测试({desc})", "通过(预期失败)"))
        
        logger.info(f"拇指根部位置设置测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复拇指根部默认位置 =====")
        remote_err = []
        err, remote_err = api.HAND_SetThumbRootPos(
            HAND_ID, 
            DEFAULT_POS, DEFAULT_SPEED,  # 恢复默认位置和速度
            remote_err
        )
        assert err == HAND_RESP_SUCCESS, \
            f"恢复拇指根部默认位置失败, 错误码: err={err},remote_err={remote_err}"
        logger.info(f"拇指根部已恢复默认位置: {DEFAULT_POS}, 速度: {DEFAULT_SPEED}")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复默认值
        try:
            logger.warning("正在尝试恢复拇指根部默认位置...")
            api.HAND_SetThumbRootPos(
                HAND_ID, 
                DEFAULT_POS, DEFAULT_SPEED, 
                []
            )
        except Exception as recovery_err:
            logger.error(f"恢复默认位置失败: {str(recovery_err)}")
        raise  # 重新抛出原始错误
    
    finally:
        """------------------- 测试结果汇总 -------------------"""
        logger.info("\n===== 拇指根部位置设置测试结果汇总 =====")
        passed = sum(1 for case, result in test_results if "通过" in result)
        total = len(test_results)
        logger.info(f"总测试用例: {total}, 通过: {passed}, 失败: {total - passed}")
        
        for case, result in test_results:
            logger.info(f"{case}: {result}")
        logger.info("=======================")

# @pytest.mark.skip('测试设置finger pos abs all一直报超时,此case暂时跳过')
def test_HAND_SetFingerPosAbsAll(api):
    # 定义测试常量
    HAND_ID = 0x02
    MAX_MOTORS = 6  # 假设手有6个手指
    
    # 默认参数值
    DEFAULT_POS = 0     # 位置默认值
    DEFAULT_SPEED = 127   # 速度默认值
    
    # 定义各参数的测试值(包含有效/边界/无效值)
    PARAM_TEST_DATA = {
        'pos_abs_all': [
            (0,       "所有手指绝对位置最小值0"),
            (32767,   "所有手指绝对位置中间值32767"),
            (65535,   "所有手指绝对位置最大值65535"),
            (-1,      "所有手指绝对位置边界值-1"),
            (65536,   "所有手指绝对位置边界值65536"),
        ],
        'speed': [
            (0,       "手指移动速度最小值0"),
            (127,     "手指移动速度中间值127"),
            (255,     "手指移动速度最大值255"),
            (-1,      "手指移动速度边界值-1"),
            (256,     "手指移动速度边界值256")
        ]
    }
    
    # 测试结果存储
    test_results = []
    
    try:
        """------------------- 单变量测试 -------------------"""
        logger.info(f"\n===== 开始批量设置手指绝对位置测试 =====")
        
        # 测试位置参数（固定速度为默认值）
        logger.info(f"测试位置参数")
        for pos, desc in PARAM_TEST_DATA['pos_abs_all']:
            # 生成统一位置数组
            pos_array = [pos] * MAX_MOTORS
            speed_array = [DEFAULT_SPEED] * MAX_MOTORS
            remote_err = []
            
            err, remote_err = api.HAND_SetFingerPosAbsAll(
                HAND_ID, pos_array, speed_array, MAX_MOTORS, remote_err
            )
            
            # 验证结果
            if 0 <= pos <= 65535:  # 有效位置范围
                assert err == HAND_RESP_SUCCESS, \
                    f"设置有效位置失败: {desc}, 错误码: err={err},remote_err={remote_err}"
                test_results.append((f"位置测试({desc})", "通过"))
            else:  # 无效位置值
                assert err != HAND_RESP_SUCCESS, \
                    f"设置无效位置未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                test_results.append((f"位置测试({desc})", "通过(预期失败)"))
        
        # 测试速度参数（固定位置为默认值）
        logger.info(f"测试速度参数")
        for speed, desc in PARAM_TEST_DATA['speed']:
            # 生成统一速度数组
            pos_array = [DEFAULT_POS] * MAX_MOTORS
            speed_array = [speed] * MAX_MOTORS
            remote_err = []
            
            err, remote_err = api.HAND_SetFingerPosAbsAll(
                HAND_ID, pos_array, speed_array, MAX_MOTORS, remote_err
            )
            
            # 验证结果
            if 0 <= speed <= 255:  # 有效速度范围
                assert err == HAND_RESP_SUCCESS, \
                    f"设置有效速度失败: {desc}, 错误码: err={err},remote_err={remote_err}"
                test_results.append((f"速度测试({desc})", "通过"))
            else:  # 无效速度值
                assert err != HAND_RESP_SUCCESS, \
                    f"设置无效速度未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                test_results.append((f"速度测试({desc})", "通过(预期失败)"))
        
        logger.info(f"批量设置手指绝对位置测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指默认位置 =====")
        remote_err = []
        
        err, remote_err = api.HAND_SetFingerPosAbsAll(
            HAND_ID, 
            [DEFAULT_POS] * MAX_MOTORS,
            [DEFAULT_SPEED] * MAX_MOTORS,
            MAX_MOTORS,
            remote_err
        )
        assert err == HAND_RESP_SUCCESS, \
            f"恢复默认位置失败, 错误码: err={err},remote_err={remote_err}"
        logger.info(f"所有手指已恢复默认位置: {DEFAULT_POS}, 速度: {DEFAULT_SPEED}")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复默认值
        try:
            logger.warning("正在尝试恢复所有手指默认位置...")
            api.HAND_SetFingerPosAbsAll(
                HAND_ID, 
                [DEFAULT_POS] * MAX_MOTORS,
                [DEFAULT_SPEED] * MAX_MOTORS,
                MAX_MOTORS,
                []
            )
        except Exception as recovery_err:
            logger.error(f"恢复默认位置失败: {str(recovery_err)}")
        raise  # 重新抛出原始错误
    
    finally:
        """------------------- 测试结果汇总 -------------------"""
        logger.info("\n===== 批量设置手指绝对位置测试结果汇总 =====")
        passed = sum(1 for case, result in test_results if "通过" in result)
        total = len(test_results)
        logger.info(f"总测试用例: {total}, 通过: {passed}, 失败: {total - passed}")
        
        for case, result in test_results:
            logger.info(f"{case}: {result}")
        logger.info("=======================")

# @pytest.mark.skip('测试设置finger pos all一直报超时,此case暂时跳过')
def test_HAND_SetFingerPosAll(api):
    # 定义测试常量
    HAND_ID = 0x02
    
    # 默认参数值
    DEFAULT_POS = 0     # 位置默认值
    DEFAULT_SPEED = 127   # 速度默认值
    
    # 定义各参数的测试值(包含有效/边界/无效值)
    PARAM_TEST_DATA = {
        'pos_all': [
            (0,       "所有手指绝逻辑位置最小值0"),
            (32767,   "所有手指逻辑位置中间值32767"),
            (65535,   "所有手指逻辑位置最大值65535"),
            (-1,      "所有手指逻辑位置边界值-1"),
            (65536,   "所有手指逻辑位置边界值65536"),
        ],
       'speed': [
            (0,       "手指移动速度最小值0"),
            (127,     "手指移动速度中间值127"),
            (255,     "手指移动速度最大值255"),
            (-1,      "手指移动速度边界值-1"),
            (256,     "手指移动速度边界值256")
        ]
    }
    
    # 测试结果存储
    test_results = []
    
    try:
        """------------------- 单变量测试 -------------------"""
        logger.info(f"\n===== 开始批量设置手指相对位置测试 =====")
        
        # 测试位置参数（固定速度为默认值）
        logger.info(f"测试位置参数")
        for pos, desc in PARAM_TEST_DATA['pos_all']:
            # 生成统一位置数组
            pos_array = [pos] * MAX_MOTOR_CNT
            speed_array = [DEFAULT_SPEED] * MAX_MOTOR_CNT
            remote_err = []
            
            err, remote_err = api.HAND_SetFingerPosAll(
                HAND_ID, pos_array, speed_array, MAX_MOTOR_CNT, remote_err
            )
            
            # 验证结果
            if 0 <= pos <= 65535:  # 有效位置范围
                assert err == HAND_RESP_SUCCESS, \
                    f"设置有效位置失败: {desc}, 错误码:err={err},remote_err={remote_err}"
                test_results.append((f"位置测试({desc})", "通过"))
            else:  # 无效位置值
                assert err != HAND_RESP_SUCCESS, \
                    f"设置无效位置未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                test_results.append((f"位置测试({desc})", "通过(预期失败)"))
        
        # 测试速度参数（固定位置为默认值）
        logger.info(f"测试速度参数")
        for speed, desc in PARAM_TEST_DATA['speed']:
            # 生成统一速度数组
            pos_array = [DEFAULT_POS] * MAX_MOTOR_CNT
            speed_array = [speed] * MAX_MOTOR_CNT
            remote_err = []
            
            err, recovery_err = api.HAND_SetFingerPosAll(
                HAND_ID, pos_array, speed_array, MAX_MOTOR_CNT, remote_err
            )
            
            # 验证结果
            if 0 <= speed <= 255:  # 有效速度范围
                assert err == HAND_RESP_SUCCESS, \
                    f"设置有效速度失败: {desc}, 错误码: err={err},remote_err={remote_err}"
                test_results.append((f"速度测试({desc})", "通过"))
            else:  # 无效速度值
                assert err != HAND_RESP_SUCCESS, \
                    f"设置无效速度未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                test_results.append((f"速度测试({desc})", "通过(预期失败)"))
        
        logger.info(f"批量设置手指相对位置测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指默认位置 =====")
        remote_err = []
        
        err, remote_err = api.HAND_SetFingerPosAll(
            HAND_ID, 
            [DEFAULT_POS] * MAX_MOTOR_CNT,
            [DEFAULT_SPEED] * MAX_MOTOR_CNT,
            MAX_MOTOR_CNT,
            remote_err
        )
        assert err == HAND_RESP_SUCCESS, \
            f"恢复默认位置失败, 错误码: err={err},remote_err={remote_err}"
        logger.info(f"所有手指已恢复默认位置: {DEFAULT_POS}, 速度: {DEFAULT_SPEED}")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复默认值
        try:
            logger.warning("正在尝试恢复所有手指默认位置...")
            api.HAND_SetFingerPosAll(
                HAND_ID, 
                [DEFAULT_POS] * MAX_MOTOR_CNT,
                [DEFAULT_SPEED] * MAX_MOTOR_CNT,
                MAX_MOTOR_CNT,
                []
            )
        except Exception as recovery_err:
            logger.error(f"恢复默认位置失败: {str(recovery_err)}")
        raise  # 重新抛出原始错误
    
    finally:
        """------------------- 测试结果汇总 -------------------"""
        logger.info("\n===== 批量设置手指相对位置测试结果汇总 =====")
        passed = sum(1 for case, result in test_results if "通过" in result)
        total = len(test_results)
        logger.info(f"总测试用例: {total}, 通过: {passed}, 失败: {total - passed}")
        
        for case, result in test_results:
            logger.info(f"{case}: {result}")
        logger.info("=======================")

# @pytest.mark.skip('测试设置finger angle all一直报超时,此case暂时跳过')
def test_HAND_SetFingerAngleAll(api):
    # 定义测试常量
    HAND_ID = 0x02
    
    # 默认参数值
    DEFAULT_ANGLE = 0     # 角度默认值
    DEFAULT_SPEED = 127    # 速度默认值
    
    # 定义各参数的测试值(包含有效/边界/无效值)
    PARAM_TEST_DATA = {
       'angle_all': [
            (0,       "所有手指角度最小值0"),
            (16384,   "所有手指角度中间值16384"),
            (32767,   "所有手指角度最大值32767"),
            (32768,   "所有手指角度负数最大值32768"),
            (65535,   "所有手指角度负数最小值65535"),
            (-1,      "所有手指角度边界值-1"),
            (65536,   "所有手指角度边界值-165536"),
        ],
       'speed': [
            (0,       "手指移动速度最小值0"),
            (127,     "手指移动速度中间值127"),
            (255,     "手指移动速度最大值255"),
            (-1,      "手指移动速度边界值-1"),
            (256,     "手指移动速度边界值256")
        ]
    }
    
    # 测试结果存储
    test_results = []
    
    try:
        """------------------- 单变量测试 -------------------"""
        logger.info(f"\n===== 开始批量设置手指角度测试 =====")
        
        # 测试角度参数（固定速度为默认值）
        logger.info(f"测试角度参数")
        for angle, desc in PARAM_TEST_DATA['angle_all']:
            # 生成统一角度数组
            angle_array = [angle] * MAX_MOTOR_CNT
            speed_array = [DEFAULT_SPEED] * MAX_MOTOR_CNT
            remote_err = []
            
            err, remote_err = api.HAND_SetFingerAngleAll(
                HAND_ID, angle_array, speed_array, MAX_MOTOR_CNT, remote_err
            )
            
            # 验证结果
            if 0 <= angle <= 65535:  # 有效角度范围
                assert err == HAND_RESP_SUCCESS, \
                    f"设置有效角度失败: {desc}, 错误码: err={err},remote_err={remote_err}"
                test_results.append((f"角度测试({desc})", "通过"))
            else:  # 无效角度值
                assert err != HAND_RESP_SUCCESS, \
                    f"设置无效角度未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                test_results.append((f"角度测试({desc})", "通过(预期失败)"))
        
        # 测试速度参数（固定角度为默认值）
        logger.info(f"测试速度参数")
        for speed, desc in PARAM_TEST_DATA['speed']:
            # 生成统一速度数组
            angle_array = [DEFAULT_ANGLE] * MAX_MOTOR_CNT
            speed_array = [speed] * MAX_MOTOR_CNT
            remote_err = []
            
            err, remote_err = api.HAND_SetFingerAngleAll(
                HAND_ID, angle_array, speed_array, MAX_MOTOR_CNT, remote_err
            )
            
            # 验证结果
            if 0 <= speed <= 255:  # 有效速度范围
                assert err == HAND_RESP_SUCCESS, \
                    f"设置有效速度失败: {desc}, 错误码: err={err},remote_err={remote_err}"
                test_results.append((f"速度测试({desc})", "通过"))
            else:  # 无效速度值
                assert err != HAND_RESP_SUCCESS, \
                    f"设置无效速度未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                test_results.append((f"速度测试({desc})", "通过(预期失败)"))
        
        logger.info(f"批量设置手指角度测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指默认角度 =====")
        remote_err = []
        
        err, recovery_err = api.HAND_SetFingerAngleAll(
            HAND_ID, 
            [DEFAULT_ANGLE] * MAX_MOTOR_CNT,
            [DEFAULT_SPEED] * MAX_MOTOR_CNT,
            MAX_MOTOR_CNT,
            remote_err
        )
        assert err == HAND_RESP_SUCCESS, \
            f"恢复默认角度失败, 错误码:err={err},remote_err={remote_err}"
        logger.info(f"所有手指已恢复默认角度: {DEFAULT_ANGLE}, 速度: {DEFAULT_SPEED}")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复默认值
        try:
            logger.warning("正在尝试恢复所有手指默认角度...")
            api.HAND_SetFingerAngleAll(
                HAND_ID, 
                [DEFAULT_ANGLE] * MAX_MOTOR_CNT,
                [DEFAULT_SPEED] * MAX_MOTOR_CNT,
                MAX_MOTOR_CNT,
                []
            )
        except Exception as recovery_err:
            logger.error(f"恢复默认角度失败: {str(recovery_err)}")
        raise  # 重新抛出原始错误
    
    finally:
        """------------------- 测试结果汇总 -------------------"""
        logger.info("\n===== 批量设置手指角度测试结果汇总 =====")
        passed = sum(1 for case, result in test_results if "通过" in result)
        total = len(test_results)
        logger.info(f"总测试用例: {total}, 通过: {passed}, 失败: {total - passed}")
        
        for case, result in test_results:
            logger.info(f"{case}: {result}")
        logger.info("=======================")

# @pytest.mark.skip('测试设置finger force pid一直报超时,此case暂时跳过')
def test_HAND_SetFingerForcePID(api):
    # 定义测试常量
    HAND_ID = 0x02
    FINGERS = [0, 1, 2, 3, 4, 5]  # 6个手指ID
    
    # 默认参数值（与test_HAND_SetFingerPID保持一致）
    DEFAULT_P = 25000
    DEFAULT_I = 200
    DEFAULT_D = 25000
    DEFAULT_G = 100
    
    # 定义各参数的测试值(包含有效/边界/无效值)
    PARAM_TEST_DATA = {
        'P': [
            (100,   "P值最小值100"),
            (24000, "P值中间值24000"),
            (50000, "P值最大值50000"),
            (99,    "P值边界值99"),
            (0,     "P值边界值0"),
            (-1,    "P值边界值-1"),
            (50001, "P值边界值50001"),
            (65535, "P值边界值65535"),
            (65536, "P值边界值65536")
        ],
        'I': [
            (0,     "I值最小值0"),
            (5000,  "I值中间值5000"),
            (10000, "I值最大值10000"),
            (-1,    "I值边界值-1"),
            (10001, "I值边界值10001"),
            (65535, "I值边界值65535"),
            (65536, "I值边界值65536")
        ],
        'D': [
            (0,     "D值最小值0"),
            (25001, "D值中间值25001"),
            (50000, "D值最大值50000"),
            (-1,    "D值边界值-1"),
            (50001, "D值边界值50001"),
            (65535, "D值边界值65535"),
            (65536, "D值边界值65536")
        ],
        'G': [
            (1,     "G值最小值1"),
            (50,    "G值中间值50"),
            (100,   "G值最大值100"),
            (0,     "G值边界值0"),
            (-1,    "G值边界值-1"),
            (101,   "G值边界值101"),
            (65535, "G值边界值65535"),
            (65536, "G值边界值65536")
        ]
    }
    
    # 测试结果存储
    test_results = []
    
    try:
        """------------------- 单变量测试 -------------------"""
        for finger_id in FINGERS:
            logger.info(f"\n===== 开始测试手指 {finger_id} 的力控PID参数 =====")
            
            # 测试P参数
            logger.info(f"测试手指 {finger_id} 的P参数")
            for p_value, desc in PARAM_TEST_DATA['P']:
                remote_err = []
                err, remote_err = api.HAND_SetFingerForcePID(
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
                        f"手指 {finger_id} 设置有效P值失败: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} P值测试({desc})", "通过"))
                else:  # 无效P值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效P值未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} P值测试({desc})", "通过(预期失败)"))
            
            # 测试I参数
            logger.info(f"测试手指 {finger_id} 的I参数")
            for i_value, desc in PARAM_TEST_DATA['I']:
                remote_err = []
                err, remote_err = api.HAND_SetFingerForcePID(
                    HAND_ID, finger_id, 
                    DEFAULT_P,      # P固定为默认值
                    i_value,        # 测试变量I
                    DEFAULT_D,      # D固定为默认值
                    DEFAULT_G,      # G固定为默认值
                    remote_err
                )
                
                # 验证结果
                if 0 <= i_value <= 10000:  # 有效I值范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效I值失败: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} I值测试({desc})", "通过"))
                else:  # 无效I值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效I值未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} I值测试({desc})", "通过(预期失败)"))
            
            # 测试D参数
            logger.info(f"测试手指 {finger_id} 的D参数")
            for d_value, desc in PARAM_TEST_DATA['D']:
                remote_err = []
                err, remote_err = api.HAND_SetFingerForcePID(
                    HAND_ID, finger_id, 
                    DEFAULT_P,      # P固定为默认值
                    DEFAULT_I,      # I固定为默认值
                    d_value,        # 测试变量D
                    DEFAULT_G,      # G固定为默认值
                    remote_err
                )
                
                # 验证结果
                if 0 <= d_value <= 50000:  # 有效D值范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效D值失败: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} D值测试({desc})", "通过"))
                else:  # 无效D值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效D值未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} D值测试({desc})", "通过(预期失败)"))
            
            # 测试G参数
            logger.info(f"测试手指 {finger_id} 的G参数")
            for g_value, desc in PARAM_TEST_DATA['G']:
                remote_err = []
                err, remote_err = api.HAND_SetFingerForcePID(
                    HAND_ID, finger_id, 
                    DEFAULT_P,      # P固定为默认值
                    DEFAULT_I,      # I固定为默认值
                    DEFAULT_D,      # D固定为默认值
                    g_value,        # 测试变量G
                    remote_err
                )
                
                # 验证结果
                if 1 <= g_value <= 100:  # 有效G值范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效G值失败: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} G值测试({desc})", "通过"))
                else:  # 无效G值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效G值未报错: {desc}, 错误码: err={err},remote_err={remote_err}"
                    test_results.append((f"手指{finger_id} G值测试({desc})", "通过(预期失败)"))
            
            logger.info(f"手指 {finger_id} 的力控PID参数测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指的默认力控PID参数 =====")
        for finger_id in FINGERS:
            remote_err = []
            err, remote_err = api.HAND_SetFingerForcePID(
                HAND_ID, finger_id, 
                DEFAULT_P, DEFAULT_I, DEFAULT_D, DEFAULT_G, remote_err
            )
            assert err == HAND_RESP_SUCCESS, \
                f"恢复手指 {finger_id} 默认力控PID参数失败, 错误码: err={err},remote_err={remote_err}"
            logger.info(f"手指 {finger_id} 已恢复默认力控PID参数")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复所有手指默认值
        try:
            logger.warning("正在尝试恢复所有手指默认力控PID参数...")
            for finger_id in FINGERS:
                api.HAND_SetFingerForcePID(
                    HAND_ID, finger_id, 
                    DEFAULT_P, DEFAULT_I, DEFAULT_D, DEFAULT_G, []
                )
        except Exception as recovery_err:
            logger.error(f"恢复默认力控PID参数失败: {str(recovery_err)}")
        raise  # 重新抛出原始错误
    
    finally:
        """------------------- 测试结果汇总 -------------------"""
        logger.info("\n===== 力控PID参数测试结果汇总 =====")
        passed = sum(1 for case, result in test_results if "通过" in result)
        total = len(test_results)
        logger.info(f"总测试用例: {total}, 通过: {passed}, 失败: {total - passed}")
        
        for case, result in test_results:
            logger.info(f"{case}: {result}")
        logger.info("=======================")

def test_HAND_ResetForce(api):# 修改api调用接口函数，添加none后测试pass
    hand_id = 0x02
    remote_err = []

    err,remote_err = api.HAND_ResetForce(hand_id, remote_err)
    assert err == HAND_RESP_SUCCESS, f"重置力量值，错误码: err={err},remote_err={remote_err}"
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
    err,remote_err = api.HAND_SetSelfTestLevel(hand_id, SELF_TEST_LEVEL['半自检'], remote_err)
    assert err == HAND_RESP_SUCCESS, f"设置半自检失败，错误码: err={err},remote_err={remote_err}"
    
    time.sleep(5)  # 等待自检执行
    
    current_level = [0]
    err,remote_err = api.HAND_GetSelfTestLevel(hand_id, current_level, [])
    assert err == HAND_RESP_SUCCESS, f"获取自检级别失败，错误码: err={err},remote_err={remote_err}"
    
    assert current_level[0] == SELF_TEST_LEVEL['半自检'], (
        f"自检级别验证失败：期望半自检({SELF_TEST_LEVEL['半自检']})，"
        f"实际{list(SELF_TEST_LEVEL.keys())[list(SELF_TEST_LEVEL.values()).index(current_level[0])]}({current_level[0]})"
    )
    logger.info("成功设置半自检")
    
    # 测试设置为完整自检（恢复默认状态）
    remote_err = [0]
    err, remote_err = api.HAND_SetSelfTestLevel(hand_id, SELF_TEST_LEVEL['完整自检'], remote_err)
    assert err == HAND_RESP_SUCCESS, f"设置完整自检失败，错误码: err={err},remote_err={remote_err}"
    
    time.sleep(5)  # 等待自检执行
    
    err,remote_err = api.HAND_GetSelfTestLevel(hand_id, current_level, [])
    assert err == HAND_RESP_SUCCESS, f"获取自检级别失败，错误码:err={err},remote_err={remote_err}"
    
    assert current_level[0] == SELF_TEST_LEVEL['完整自检'], (
        f"自检级别验证失败：期望完整自检({SELF_TEST_LEVEL['完整自检']})，"
        f"实际{list(SELF_TEST_LEVEL.keys())[list(SELF_TEST_LEVEL.values()).index(current_level[0])]}({current_level[0]})"
    )
    logger.info("成功设置完整自检")
    
    # 确保测试结束后恢复默认状态
    remote_err = [0]
    err, remote_err = api.HAND_SetSelfTestLevel(hand_id, SELF_TEST_LEVEL['完整自检'], remote_err)
    if err != HAND_RESP_SUCCESS:
        logger.error(f"恢复默认自检级别失败，错误码: err={err},remote_err={remote_err}")

def test_HAND_SetBeepSwitch(api):
    hand_id = 0x02
    BEEP_STATUS = {
        'OFF': 0,
        'ON': 1
    }
    
    # 测试关闭蜂鸣器
    err, remote_err = api.HAND_SetBeepSwitch(hand_id, BEEP_STATUS['OFF'], [])
    assert err == HAND_RESP_SUCCESS, f"设置蜂鸣器关闭失败，错误码: err={err},remote_err={remote_err}"
    
    time.sleep(0.5)  # 等待设备响应
    
    status_container = [0]
    err, remote_err = api.HAND_GetBeepSwitch(hand_id, status_container, [])
    assert err == HAND_RESP_SUCCESS, f"获取蜂鸣器状态失败，错误码: err={err},remote_err={remote_err}"
    
    actual_status = status_container[0]
    assert actual_status == BEEP_STATUS['OFF'], (
        f"蜂鸣器关闭状态验证失败：期望={BEEP_STATUS['OFF']}，实际={actual_status}"
    )
    logger.info("蜂鸣器已成功关闭")
    
    # 测试开启蜂鸣器
    err, remote_err = api.HAND_SetBeepSwitch(hand_id, BEEP_STATUS['ON'], [])
    assert err == HAND_RESP_SUCCESS, f"设置蜂鸣器开启失败，错误码: err={err},remote_err={remote_err}"
    
    time.sleep(0.5)  # 等待设备响应
    
    err, remote_err = api.HAND_GetBeepSwitch(hand_id, status_container, [])
    assert err == HAND_RESP_SUCCESS, f"获取蜂鸣器状态失败，错误码: err={err},remote_err={remote_err}"
    
    actual_status = status_container[0]
    assert actual_status == BEEP_STATUS['ON'], (
        f"蜂鸣器开启状态验证失败：期望={BEEP_STATUS['ON']}，实际={actual_status}"
    )
    logger.info("蜂鸣器已成功开启")
    
    # 恢复默认状态
    err, remote_err = api.HAND_SetBeepSwitch(hand_id, BEEP_STATUS['ON'], [])
    if err != HAND_RESP_SUCCESS:
        logger.error(f"恢复蜂鸣器默认状态失败，错误码: err={err},remote_err={remote_err}")
    else:
        logger.info('蜂鸣器开关已恢复默认状态')

# @pytest.mark.skip('测试设置hand beep一直报超时,此case暂时跳过')
def test_HAND_Beep(api): # 设置时长慧报3的错误码
    hand_id = 0x02
    duration = 500
    err, remote_err = api.HAND_Beep(hand_id, duration, [])
    assert err == HAND_RESP_SUCCESS,f"设置蜂鸣器时长失败:  err={err},remote_err={remote_err}"
    logger.info(f'成功设置蜂鸣器时长：{duration}')

def test_HAND_SetButtonPressedCnt(api):
    hand_id = 0x02
    
    # 测试正常范围（0-255）
    # 测试最小值
    target_pressed_cnt = 0
    remote_err = [0]
    err, remote_err = api.HAND_SetButtonPressedCnt(hand_id, target_pressed_cnt, remote_err)
    assert err == HAND_RESP_SUCCESS, (
        f"设置按钮按下次数失败（值={target_pressed_cnt}），错误码:  err={err},remote_err={remote_err}"
    )
    
    observed_pressed_cnt = [0]
    err,remote_err = api.HAND_GetButtonPressedCnt(hand_id, observed_pressed_cnt, remote_err)
    assert err == HAND_RESP_SUCCESS, (
        f"获取按钮按下次数失败（值={target_pressed_cnt}），错误码:  err={err},remote_err={remote_err}"
    )
    
    actual_cnt = observed_pressed_cnt[0]
    assert actual_cnt == target_pressed_cnt, (
        f"按钮按下次数验证失败：目标值={target_pressed_cnt}，实际值={actual_cnt}"
    )
    
    logger.info(f"按钮按下次数设置成功，值={target_pressed_cnt}")
    
    # 测试中间值
    target_pressed_cnt = 128
    remote_err = [0]
    err, remote_err = api.HAND_SetButtonPressedCnt(hand_id, target_pressed_cnt, remote_err)
    assert err == HAND_RESP_SUCCESS, (
        f"设置按钮按下次数失败（值={target_pressed_cnt}），错误码: err={err},remote_err={remote_err}"
    )
    
    observed_pressed_cnt = [0]
    err, remote_err = api.HAND_GetButtonPressedCnt(hand_id, observed_pressed_cnt, remote_err)
    assert err == HAND_RESP_SUCCESS, (
        f"获取按钮按下次数失败（值={target_pressed_cnt}），错误码: err={err},remote_err={remote_err}"
    )
    
    actual_cnt = observed_pressed_cnt[0]
    assert actual_cnt == target_pressed_cnt, (
        f"按钮按下次数验证失败：目标值={target_pressed_cnt}，实际值={actual_cnt}"
    )
    
    logger.info(f"按钮按下次数设置成功，值={target_pressed_cnt}")
    
    # 测试最大值
    target_pressed_cnt = 255
    remote_err = [0]
    err, remote_err = api.HAND_SetButtonPressedCnt(hand_id, target_pressed_cnt, remote_err)
    assert err == HAND_RESP_SUCCESS, (
        f"设置按钮按下次数失败（值={target_pressed_cnt}），错误码: err={err},remote_err={remote_err}"
    )
    
    observed_pressed_cnt = [0]
    err, remote_err = api.HAND_GetButtonPressedCnt(hand_id, observed_pressed_cnt, remote_err)
    assert err == HAND_RESP_SUCCESS, (
        f"获取按钮按下次数失败（值={target_pressed_cnt}），错误码:err={err},remote_err={remote_err}"
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
    err,remote_err = api.HAND_StartInit(hand_id, remote_err)
    assert err == HAND_RESP_SUCCESS,f"初始化手失败，错误码: 错误码:err={err},remote_err={remote_err}"
    logger.info(f'手初始化成功')
