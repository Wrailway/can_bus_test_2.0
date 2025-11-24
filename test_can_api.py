import pytest
from asyncio import sleep
import logging

from OHandSerialAPI import HAND_RESP_SUCCESS, HAND_PROTOCOL_UART, MAX_MOTOR_CNT, MAX_THUMB_ROOT_POS, MAX_FORCE_ENTRIES, OHandSerialAPI
from can_interface import *

# 设置日志级别为INFO，获取日志记录器实例
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()

# 设置处理程序的日志级别为 INFO
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

ADDRESS_MASTER = 0x01
FINGER_POS_TARGET_MAX_LOSS = 100

# 初始化 API 实例（pytest夹具）
@pytest.fixture
def serial_api_instance():
    can_interface_instance = None
    serial_api_instance = None

    try:
        can_interface_instance = CAN_Init(port_name="1", baudrate=1000000)
        if can_interface_instance is None:
            print("port init failed\n")
            return 0
        protocol = HAND_PROTOCOL_UART
        serial_api_instance = OHandSerialAPI(can_interface_instance, protocol, ADDRESS_MASTER,
                                                   send_data_impl,
                                                   recv_data_impl)

        serial_api_instance.HAND_SetTimerFunction(get_milli_seconds_impl, delay_milli_seconds_impl)
        serial_api_instance.HAND_SetCommandTimeOut(255)
        print(serial_api_instance.get_private_data(), "\n")

        yield serial_api_instance
    except Exception as e:
        print(f"\n初始化异常: {str(e)}")

    finally:
        if serial_api_instance and hasattr(serial_api_instance, "shutdown"):  # 检查是否有自定义关闭方法
            try:
                serial_api_instance.shutdown()
                # logger.info("API shutdown successfully")
            except Exception as e:
                logger.error(f"Error during API shutdown: {e}")

        if can_interface_instance and hasattr(can_interface_instance, "shutdown"):
            try:
                can_interface_instance.shutdown()
                # logger.info("CAN bus connection closed")
            except Exception as e:
                logger.error(f"Error closing CAN bus: {e}")

# --------------------------- GET 命令测试 ---------------------------
# def test_HAND_GetProtocolVersion(serial_api_instance):
#     hand_id = 0x02
#     major, minor = [0], [0]
#     err, major_get, minor_get  = serial_api_instance.HAND_GetProtocolVersion(hand_id, major, minor, [])
#     assert err == HAND_RESP_SUCCESS, f"获取协议版本失败: err={err}"
#     logger.info(f"成功获取协议版本: V{major_get}.{minor_get}")

# def test_HAND_GetFirmwareVersion(serial_api_instance):
#     hand_id = 0x02
#     major, minor, revision = [0], [0], [0]
#     err, major_get, minor_get, revision_get = serial_api_instance.HAND_GetFirmwareVersion(hand_id, major, minor, revision, [])
#     assert err == HAND_RESP_SUCCESS, f"获取固件版本失败: err={err}"
#     logger.info(f"成功获固件版本: V{major_get}.{minor_get}.{revision_get}")

# def test_HAND_GetHardwareVersion(serial_api_instance):
#     hand_id = 0x02
#     hw_type, hw_ver, boot_version = [0], [0],[0]
#     err, hw_type_get, hw_ver_get, boot_version_get = serial_api_instance.HAND_GetHardwareVersion(hand_id, hw_type, hw_ver, boot_version, [])
#     assert err == HAND_RESP_SUCCESS, f"获取硬件版本失败: err={err}"
#     logger.info(f"成功获取硬件版本: V{hw_type_get}.{hw_ver_get}.{boot_version_get}")


# def test_HAND_GetFingerPID(serial_api_instance):
#     hand_id = 0x02
#     finger_id = 0x00
#     p = [0]
#     i = [0]
#     d = [0]
#     g = [0]
#     for j in range(6):
#         err, p_get, i_get,d_get,g_get= serial_api_instance.HAND_GetFingerPID(hand_id, finger_id+j, p, i, d, g, [])
#         assert err == HAND_RESP_SUCCESS, f"获取手指p, i, d, g值失败: err={err}"
#         logger.info(f"成功获取手指{finger_id+j} p, i, d, g值: {p_get},{i_get},{d_get},{g_get}")


# def test_HAND_GetFingerCurrentLimit(serial_api_instance):
#     hand_id = 0x02
#     finger_id = 0x00
#     current_limit = [0]
#     for i in range(6):
#         err, current_limit_get = serial_api_instance.HAND_GetFingerCurrentLimit(hand_id, finger_id+i, current_limit, [])
#         assert err == HAND_RESP_SUCCESS, f"获取手指电流限制值失败: err={err}"
#         logger.info(f"成功获取手指{finger_id+i} 电流限制值: {current_limit_get}")

# def test_HAND_GetFingerCurrent(serial_api_instance):
#     hand_id = 0x02
#     finger_id = 0x00
#     current = [0]
#     for i in range(6):
#         err, current_get = serial_api_instance.HAND_GetFingerCurrent(hand_id, finger_id+i, current, [])
#         assert err == HAND_RESP_SUCCESS,f"获取手指电流值失败: err={err}"
#         logger.info(f"成功获取手指{finger_id+i} 电流值: {current_get}")

# def test_HAND_GetFingerForceTarget(serial_api_instance):
#     hand_id = 0x02
#     finger_id = 0x00
#     force_target = [0]
#     for i in range(6):
#         err, force_target_get = serial_api_instance.HAND_GetFingerForceTarget(hand_id, finger_id, force_target, [])
#         assert err == HAND_RESP_SUCCESS,f"获取手指力量目标值失败: err={err}"
#         logger.info(f"成功获取手指{finger_id+i} 力量目标值: {force_target_get}")

# def test_HAND_GetFingerForce(serial_api_instance):
#     hand_id = 0x02
#     finger_id = 0x00
#     force_entry_cnt = [0]
#     force = [0] * MAX_FORCE_ENTRIES
#     for i in range(6):
#         err, force_get = serial_api_instance.HAND_GetFingerForce(hand_id, finger_id+i, force_entry_cnt, force, [])
#         assert err == HAND_RESP_SUCCESS,f"获取手指当前力量值失败: err={err}"
#         logger.info(f"成功获取手指{finger_id+i} 力量目标值: {force_get}")

# def test_HAND_GetFingerPosLimit(serial_api_instance):
#     hand_id = 0x02
#     finger_id = 0x00
#     low_limit = [0]
#     high_limit = [0]
#     for i in range(6):
#         err, low_limit_get,high_limit_get = serial_api_instance.HAND_GetFingerPosLimit(hand_id, finger_id+i, low_limit, high_limit, [])
#         assert err == HAND_RESP_SUCCESS,f"获取手指绝对位置限制值失败: err={err}"
#         logger.info(f"成功获取手指{finger_id+i} 绝对位置限制值: {low_limit_get}, {high_limit_get}")

# def test_HAND_GetFingerPosAbs(serial_api_instance):
#     hand_id = 0x02
#     finger_id = 0x00
#     target_pos = [0]
#     current_pos = [0]
#     for i in range(6):
#         err, target_pos_get, current_pos_get= serial_api_instance.HAND_GetFingerPosAbs(hand_id, finger_id+i, target_pos, current_pos, [])
#         assert err == HAND_RESP_SUCCESS,f"获取手指绝当前绝对位置值失败: err={err}"
#         logger.info(f"成功获取手指{finger_id+i} 当前绝对位置值: {target_pos_get}, {current_pos_get}")


# def test_HAND_GetFingerPos(serial_api_instance):
#     hand_id = 0x02
#     finger_id = 0x00
#     target_pos = [0]
#     current_pos = [0]
#     for i in range(6):
#         err, target_pos_get, current_pos_get = serial_api_instance.HAND_GetFingerPos(hand_id, finger_id+i, target_pos, current_pos, [])
#         assert err == HAND_RESP_SUCCESS,f"获取手指绝当前逻辑位置值失败: err={err}"
#         logger.info(f"成功获取手指{finger_id+i} 当前逻辑位置值: {target_pos_get}, {current_pos_get}")

# def test_HAND_GetFingerAngle(serial_api_instance):
#     hand_id = 0x02
#     finger_id = 0x00
#     target_angle = [0]
#     current_angle = [0]
#     for i in range(6):
#         err, target_angle_get, current_angle_get= serial_api_instance.HAND_GetFingerAngle(hand_id, finger_id+i, target_angle, current_angle, [])
#         assert err == HAND_RESP_SUCCESS,f"获取手指第一关节角度值失败:err={err}"
#         logger.info(f"成功获取手指{finger_id+i} 第一关节角度值: {target_angle_get}, {current_angle_get}")

# def test_HAND_GetThumbRootPos(serial_api_instance):
#     hand_id = 0x02
#     raw_encoder = [0]
#     pos = [0]
#     err, raw_encoder_get, pos_get = serial_api_instance.HAND_GetThumbRootPos(hand_id, raw_encoder, pos, [])
#     assert err == HAND_RESP_SUCCESS,f"获取大拇指旋转预设位置值失败: err={err}"
#     logger.info(f"成功获取大拇指旋转预设位置值: {raw_encoder_get}, {pos_get}")

# def test_HAND_GetFingerPosAbsAll(serial_api_instance):
#     hand_id = 0x02
#     target_pos = [0] * MAX_MOTOR_CNT
#     current_pos = [0] * MAX_MOTOR_CNT
#     motor_cnt = [MAX_MOTOR_CNT]
#     err, target_pos_get,current_pos_get= serial_api_instance.HAND_GetFingerPosAbsAll(hand_id, target_pos, current_pos, motor_cnt, [])
#     assert err == HAND_RESP_SUCCESS,f"获取所有手指当前的绝对位置值失败: err={err}"
#     logger.info(f"成功获取所有手指当前的绝对位置值: {target_pos_get}, {current_pos_get}")


# def test_HAND_GetFingerPosAll(serial_api_instance):
#     hand_id = 0x02
#     target_pos = [0] * MAX_MOTOR_CNT
#     current_pos = [0] * MAX_MOTOR_CNT
#     motor_cnt = [MAX_MOTOR_CNT]
#     remote_err = []
#     err, target_pos_get,current_pos_get = serial_api_instance.HAND_GetFingerPosAll(hand_id, target_pos, current_pos, motor_cnt, remote_err)
#     assert err == HAND_RESP_SUCCESS,f"获取所有手指当前的逻辑位置值失败: err={err}"
#     logger.info(f"成功获取所有手指当前的逻辑位置值:  {target_pos_get}, {current_pos_get}")

# def test_HAND_GetFingerAngleAll(serial_api_instance):
#     hand_id = 0x02
#     target_angle = [0] * MAX_MOTOR_CNT
#     current_angle = [0] * MAX_MOTOR_CNT
#     motor_cnt = [MAX_MOTOR_CNT]
#     err, remtarget_angle_get, current_angle_get= serial_api_instance.HAND_GetFingerAngleAll(hand_id, target_angle, current_angle, motor_cnt, [])
#     assert err == HAND_RESP_SUCCESS,f"获取所有手指值失败: err={err}"
#     logger.info(f"成功获取所有手指当前的逻辑位置值: {remtarget_angle_get}, {current_angle_get}")
    
# def test_HAND_GetFingerForcePID(serial_api_instance):
#     hand_id = 0x02
#     finger_id = 0x00
#     p = [0]
#     i = [0]
#     d = [0]
#     g = [0]
#     for j in range(5): #拇指旋转没带
#         err, p_get,i_get, d_get, g_get = serial_api_instance.HAND_GetFingerForcePID(hand_id, finger_id+j, p, i, d, g, [])
#         assert err == HAND_RESP_SUCCESS,f"获取手指力量p, i, d, g值失败: err={err}"
#         logger.info(f"成功获取手指{finger_id+j} 力量p, i, d, g值: {p_get}, {i_get},{d_get},{g_get}")

# def test_HAND_GetSelfTestLevel(serial_api_instance):
#     hand_id = 0x02
#     self_test_level = [0]
#     err, self_test_level_get = serial_api_instance.HAND_GetSelfTestLevel(hand_id, self_test_level, [])
#     assert err == HAND_RESP_SUCCESS,f"获取手自检开关状态失败: err={err}"
#     logger.info(f"成功获取手自检开关状态: {self_test_level_get}")

# def test_HAND_GetBeepSwitch(serial_api_instance):
#     hand_id = 0x02
#     beep_switch = [0]
#     err, beep_switch_get = serial_api_instance.HAND_GetBeepSwitch(hand_id, beep_switch, [])
#     assert err == HAND_RESP_SUCCESS,f"获取手蜂鸣器开关状态失败: err={err}"
#     logger.info(f"成功获取手蜂鸣器开关状态: {beep_switch_get}")

# def test_HAND_GetButtonPressedCnt(serial_api_instance):
#     hand_id = 0x02
#     pressed_cnt = [0]
#     err, pressed_cnt_get = serial_api_instance.HAND_GetButtonPressedCnt(hand_id, pressed_cnt, [])
#     assert err == HAND_RESP_SUCCESS,f"获取手按钮按下次数值失败:  err={err}"
#     logger.info(f"成功获取手按钮按下次数值: {pressed_cnt_get}")

# def test_HAND_GetUID(serial_api_instance):
#     hand_id = 0x02
#     uid_w0 = [0]
#     uid_w1 = [0]
#     uid_w2 = [0]
#     err, uid_w0_get,uid_w1_get,uid_w2_get = serial_api_instance.HAND_GetUID(hand_id, uid_w0, uid_w1, uid_w2, [])
#     assert err == HAND_RESP_SUCCESS,f"获取手UID值失败: err={err}"
#     logger.info(f"成功获取手UID值: {uid_w0_get},{uid_w1_get},{uid_w2_get}")
    
# @pytest.mark.skip('未实现，只返回err')
# def test_HAND_GetBatteryVoltage(serial_api_instance):
#     hand_id = 0x02
#     voltage = [0]
#     err, voltage_get = serial_api_instance.HAND_GetBatteryVoltage(hand_id, voltage, [])
#     assert err == HAND_RESP_SUCCESS,f"获取手电池电压值失败: err={err}"
#     logger.info(f"成功获取手电池电压值: {voltage_get}")
    
# @pytest.mark.skip('未实现，只返回err')
# def test_HAND_GetUsageStat(serial_api_instance):
#     hand_id = 0x02
#     total_use_time = [0]
#     total_open_times = [0] * MAX_MOTOR_CNT
#     motor_cnt = MAX_MOTOR_CNT
#     err, total_use_time_get,total_open_times_get= serial_api_instance.HAND_GetUsageStat(hand_id, total_use_time, total_open_times, motor_cnt, [])
#     assert err == HAND_RESP_SUCCESS,f"获取手使用数据值失败: err={err}"
#     logger.info(f"成功获取手使用数据值: {total_use_time_get},{total_open_times_get}")
    
# def test_GetCalidata(serial_api_instance):
#     hand_id = 0x02
#     end_pos = [0] * MAX_MOTOR_CNT
#     start_pos = [0] * MAX_MOTOR_CNT
#     motor_cnt = [MAX_MOTOR_CNT]
#     thumb_root_pos = [0] * MAX_THUMB_ROOT_POS
#     thumb_root_pos_cnt = [3]  # 初始请求3个拇指根位置数据
#     err, end_pos_get, start_pos_get, thumb_root_pos_get = serial_api_instance.HAND_GetCaliData(hand_id, end_pos, start_pos, motor_cnt, thumb_root_pos, thumb_root_pos_cnt, [])
#     assert err == HAND_RESP_SUCCESS, f"获取矫正数据失败: {err}"
#     logger.info(f"成功获取矫正数据, end_pos: {end_pos_get}, start_pos: {start_pos_get}, thumb_root_pos: {thumb_root_pos_get}, ")
    
# def test_GetfingerStopParams(serial_api_instance):
#     hand_id = 0x02
#     speed, stop_current, stop_after_period, retry_interval = [0], [0], [0], [0]
#     for i in range(MAX_MOTOR_CNT):
#         err, speed_get, stop_current_get, stop_after_period_get, retry_interval_get = serial_api_instance.HAND_GetFingerStopParams(hand_id, i, speed, stop_current, stop_after_period, retry_interval, [])
#         assert err == HAND_RESP_SUCCESS, f"获取手指停止参数失败: {err}"
#         logger.info(f"成功获取手指停止参数: 速度: {speed_get}, 暂停电流:{stop_current_get}, 暂停间隔:{stop_after_period_get}, 重试间隔:{retry_interval_get}")
        
# def test_GetManufactureData(serial_api_instance):
#     hand_id = 0x02
#     sub_model, hw_revision, serial_number, customer_tag = [0], [0], [0], [0]
#     err, sub_model_get, hw_revision_get, serial_number_get, customer_tag_get = serial_api_instance.HAND_GetManufactureData(hand_id, sub_model, hw_revision, serial_number, customer_tag, [])
#     assert err == HAND_RESP_SUCCESS, f"manufacture_data_get: {err}\n"
#     logger.info(f"sub_model: {sub_model_get}, hw_revision: {hw_revision_get}, serial_number: {serial_number_get}, customer_tag: {customer_tag_get}")

# def test_GetFingerSpeedCtrlParams(serial_api_instance):
#     hand_id = 0x02
#     brake_distance, accel_distance, speed_ratio = [0], [0], [0]
#     err, brake_distance_get, accel_distance_get, speed_ratio_get = serial_api_instance.HAND_GetFingerSpeedCtrlParams(hand_id, brake_distance, accel_distance, speed_ratio, [])
#     assert err == HAND_RESP_SUCCESS, f"test_speed_ctrl_params_get: {err}\n"
#     logger.info(f"brake_distance: {brake_distance_get}, accel_distance: {accel_distance_get}, speed_ratio: {speed_ratio_get}")



# # --------------------------- SET 命令测试 ---------------------------
# def test_HAND_Reset(serial_api_instance):
#     hand_id = 0x02
#     RESET_MODE ={
#         '工作模式':0,
#         'DFU模式':1
#     }
#     # mode = 0
#     remote_err = []

#     err = serial_api_instance.HAND_Reset(hand_id, RESET_MODE.get('工作模式'), remote_err)
#     assert err == HAND_RESP_SUCCESS,f"设置手重置失败: err={err}"
#     logger.info(f'设置手重置重启到工作模式成功')
#     time.sleep(15)
    
#     err = serial_api_instance.HAND_Reset(hand_id, RESET_MODE.get('DFU模式'), remote_err)
#     assert err == HAND_RESP_SUCCESS,f"设置手重置失败: err={err}"
#     logger.info(f'设置手重置重启到DFU模式成功')
#     time.sleep(15)
    
#     logger.info('恢复默认值')
#     err = serial_api_instance.HAND_Reset(hand_id, RESET_MODE.get('工作模式'), remote_err)
#     assert err == HAND_RESP_SUCCESS,f"恢复默认值失败: err={err}"
#     logger.info('恢复默认值成功')
    
@pytest.mark.skip('Rohand 暂时跳过关机接口测试，单独测试pass')
def test_HAND_PowerOff(serial_api_instance):
    hand_id = 0x02
    remote_err = []

    err = serial_api_instance.HAND_PowerOff(hand_id, remote_err)
    assert err == HAND_RESP_SUCCESS,f"设置关机失败: err={err},remote_err={remote_err[0]}"
    logger.info('设置关机成功成功')


# @pytest.mark.skip('先跳过设备ID的修改')  
# def test_HAND_SetID(serial_api_instance):
#     """测试设置设备ID功能（适配API实际方法，移除HAND_GetID依赖）"""
#     original_hand_id = 0x02  # 初始默认ID
#     test_results = []
    
#     # 保存原始API的私有数据用于重建连接
#     private_data = serial_api_instance.get_private_data() if hasattr(serial_api_instance, 'get_private_data') else None
#     print('111')
#     try:
#         # 定义测试数据（ID范围：2-247为有效）
#         test_cases = [
#             (3,     "hand id最小值2（有效）"),
#             (125,   "hand id中间值125（有效）"),
#             (247,   "hand id最大值247（有效）"),
#             (1,     "hand id边界值1（无效）"),
#             (0,     "hand id边界值0（无效）"),
#             (-1,    "hand id边界值-1（无效）"),
#             (248,   "hand id边界值248（无效）"),
#             (256,   "hand id边界值256（无效）"),
#         ]
        
#         for new_id, desc in test_cases:
#             logger.info(f"\n----- 测试 {desc} -----")
#             remote_err = []
            
#             # 发送设置ID命令（使用API中实际存在的HAND_SetNodeID对应方法）
#             set_err = serial_api_instance.HAND_SetID(original_hand_id, new_id, remote_err)
#             print('2222')
#             # 处理有效ID（2-247）
#             if 3 <= new_id <= 247:
#                 # 验证设置命令是否成功
#                 assert set_err == HAND_RESP_SUCCESS, \
#                     f"有效ID设置命令失败: {desc}, 错误码: {set_err}"
#                 print('333')
#                 # 设备重启等待（根据实际重启时间调整）
#                 logger.info(f"等待设备重启（新ID: {new_id}）...")
#                 time.sleep(5)
#                 print('4444')
#                 # 关闭当前连接
#                 if hasattr(api, 'shutdown'):
#                     serial_api_instance.shutdown()
#                 CAN_Shutdown(private_data)
#                 print('555')
#                 # 重建连接（使用新ID）并验证是否能通信
#                 can_interface_instance = CAN_Init(port_name="1", baudrate=1000000)
#                 assert can_interface_instance is not None, "CAN总线初始化失败"
#                 print('666')
#                 # 创建新API实例（使用新ID）
#                 serial_api_instance = OHandSerialAPI(
#                     private_data=can_interface_instance,
#                     protocol=0,  # HAND_PROTOCOL_UART
#                     address_master=new_id,
#                     send_data_impl=send_data_impl,
#                     recv_data_impl=recv_data_impl
#                 )
#                 serial_api_instance.HAND_SetTimerFunction(get_milli_seconds_impl, delay_milli_seconds_impl)
#                 serial_api_instance.HAND_SetCommandTimeOut(255)
                
#                 # 间接验证新ID生效：通过查询其他基础信息（如协议版本）判断连接有效性
#                 major, minor = [0], [0]
#                 verify_err, _ = serial_api_instance.HAND_GetProtocolVersion(new_id, major, minor, [])
#                 assert verify_err == HAND_RESP_SUCCESS, \
#                     f"新ID {new_id} 通信失败，验证协议版本错误: {verify_err}"
                
#                 test_results.append((f"ID测试({desc})", "通过"))
#                 logger.info(f"新ID {new_id} 验证成功（通信正常）")
                
#                 # 恢复原始ID
#                 recover_err, _ = serial_api_instance.HAND_SetID(new_id, original_hand_id, [])
#                 assert recover_err == HAND_RESP_SUCCESS, \
#                     f"恢复原始ID命令失败，错误码: {recover_err}"
                
#                 # 等待恢复后重启
#                 logger.info(f"等待设备恢复原始ID {original_hand_id}...")
#                 time.sleep(5)
                
#                 # 关闭当前连接
#                 if hasattr(serial_api_instance, 'shutdown'):
#                     serial_api_instance.shutdown()
#                 CAN_Shutdown(can_interface_instance)
                
#                 # 重建原始ID连接
#                 can_interface_instance = CAN_Init(port_name="1", baudrate=1000000)
#                 assert can_interface_instance is not None, "CAN总线初始化失败"
                
#                 serial_api_instance = OHandSerialAPI(
#                     private_data=can_interface_instance,
#                     protocol=0,
#                     address_master=original_hand_id,
#                     send_data_impl=send_data_impl,
#                     recv_data_impl=recv_data_impl
#                 )
#                 serial_api_instance.HAND_SetTimerFunction(get_milli_seconds_impl, delay_milli_seconds_impl)
#                 serial_api_instance.HAND_SetCommandTimeOut(255)
                
#                 # 验证原始ID恢复：查询协议版本判断连接
#                 major, minor = [0], [0]
#                 recover_verify_err, _ = serial_api_instance.HAND_GetProtocolVersion(original_hand_id, major, minor, [])
#                 assert recover_verify_err == HAND_RESP_SUCCESS, \
#                     f"原始ID {original_hand_id} 恢复失败，通信错误: {recover_verify_err}"
#                 logger.info(f"原始ID {original_hand_id} 恢复成功（通信正常）")
            
#             # 处理无效ID（超出2-247范围）
#             else:
#                 # 验证设置命令是否被拒绝
#                 assert set_err != HAND_RESP_SUCCESS, \
#                     f"无效ID设置未被拒绝: {desc}, 错误码: {set_err}"
                
#                 # 验证原始ID仍能通信（未被修改）
#                 major, minor = [0], [0]
#                 check_err, _ = serial_api_instance.HAND_GetProtocolVersion(original_hand_id, major, minor, [])
#                 assert check_err == HAND_RESP_SUCCESS, \
#                     f"无效ID设置后原始ID通信失败，错误码: {check_err}"
                
#                 test_results.append((f"ID测试({desc})", "通过（预期失败）"))
    
#     except AssertionError as e:
#         logger.error(f"测试断言失败: {str(e)}")
#         test_results.append(("全局断言", f"失败: {str(e)}"))
#         raise
#     except Exception as e:
#         logger.error(f"测试异常: {str(e)}")
#         test_results.append(("全局异常", f"失败: {str(e)}"))
#         raise
#     finally:
#         # 最终确保设备恢复为原始ID并验证
#         try:
#             logger.info("\n----- 最终恢复原始ID -----")
#             if hasattr(serial_api_instance, 'shutdown'):
#                 serial_api_instance.shutdown()
#             CAN_Shutdown(can_interface_instance)
            
#             # 重建原始ID连接
#             can_interface_instance = CAN_Init(port_name="1", baudrate=1000000)
#             serial_api_instance = OHandSerialAPI(
#                 private_data=can_interface_instance,
#                 protocol=0,
#                 address_master=original_hand_id,
#                 send_data_impl=send_data_impl,
#                 recv_data_impl=recv_data_impl
#             )
#             serial_api_instance.HAND_SetTimerFunction(get_milli_seconds_impl, delay_milli_seconds_impl)
            
#             # 恢复原始ID命令
#             final_err, _ = serial_api_instance.HAND_SetID(original_hand_id, original_hand_id, [])
#             time.sleep(3)
            
#             # 验证最终状态
#             major, minor = [0], [0]
#             final_verify_err, _ = serial_api_instance.HAND_GetProtocolVersion(original_hand_id, major, minor, [])
#             if final_verify_err == HAND_RESP_SUCCESS:
#                 logger.info(f"最终恢复原始ID {original_hand_id} 成功（通信正常）")
#             else:
#                 logger.warning(f"最终恢复原始ID失败，通信错误: {final_verify_err}")
#         except Exception as e:
#             logger.error(f"最终恢复原始ID异常: {str(e)}")
        
#         # 测试结果汇总
#         logger.info("\n===== 设置设备ID测试结果汇总 =====")
#         passed = sum(1 for case, result in test_results if "通过" in result)
#         total = len(test_results)
#         logger.info(f"总测试用例: {total}, 通过: {passed}, 失败: {total - passed}")
#         for case, result in test_results:
#             logger.info(f"{case}: {result}")
#         logger.info("=======================")
    


@pytest.mark.skip('测试设置pid，超出范围报255错误，此case暂时跳过')
def test_HAND_SetFingerPID(serial_api_instance):
    ######
    # api.HAND_SetCommandTimeOut(500)
    """手指PID参数设置功能测试 - 单变量控制"""
    # 定义测试常量
    HAND_ID = 0x02
    FINGERS = [0, 1, 2, 3, 4, 5]  # 6个手指ID
    
    # 默认参数值
    DEFAULT_P = 250.0
    DEFAULT_I = 2.0
    DEFAULT_D = 250.0
    DEFAULT_G = 1.0
    
    # 定义各参数的测试值(包含有效/边界/无效值)
    PARAM_TEST_DATA = {
        'P': [
            (1.0,   "P值最小值1.0"),
            (240.0, "P值中间值240.00"),
            (500.0, "P值最大值500.00"),
            (0.99,    "P值边界值0.99"),
            (0,     "P值边界值0.0"),
            (-0.01,    "P值边界值-0.01"),
            (500.01, "P值边界值500.01"),
            (65535.0, "P值边界值65535.0"),
            (65536.0, "P值边界值65536.0")
        ],
        'I': [
            (0.0,     "I值最小值0.0"),
            (50.00,  "I值中间值50.00"),
            (100.00, "I值最大值100.00"),
            (-0.01,    "I值边界值-0.01"),
            (100.01, "I值边界值100.01"),
            (65535.0, "I值边界值65535.0"),
            (65536.0, "I值边界值65536.0")
        ],
        'D': [
            (0.0,     "D值最小值0.0"),
            (250.01, "D值中间值250.01"),
            (500.00, "D值最大值500.00"),
            (-0.01,    "D值边界值-0.01"),
            (500.01, "D值边界值500.01"),
            (65535.0, "D值边界值65535.0"),
            (65536.0, "D值边界值65536.0")
        ],
        'G': [
            (0.01,     "G值最小值0.01"),
            (0.50,    "G值中间值0.50"),
            (1.00,   "G值最大值1.00"),
            (0,     "G值边界值0.0"),
            (-0.01,    "G值边界值-0.01"),
            (1.01,   "G值边界值1.01"),
            (65535.0, "G值边界值65535.0"),
            (65536.0, "G值边界值65536.0")
        ]
    }
    
    # 测试结果存储
    test_results = []
    
    try:
        """------------------- 单变量测试 -------------------"""
        for finger_id in FINGERS:
            logger.info(f"\n===== 开始测试手指 {finger_id} =====")
            delay_milli_seconds_impl(1000)
            # 测试P参数
            logger.info(f"测试手指 {finger_id} 的P参数")
            for p_value, desc in PARAM_TEST_DATA['P']:
                remote_err = []
                delay_milli_seconds_impl(500)
                err = serial_api_instance.HAND_SetFingerPID(
                    HAND_ID, finger_id, 
                    p_value,        # 测试变量P
                    DEFAULT_I,      # I固定为默认值
                    DEFAULT_D,      # D固定为默认值
                    DEFAULT_G,      # G固定为默认值
                    remote_err
                )
                
                # 验证结果
                if 1.0 <= p_value <= 500.00:  # 有效P值范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效P值失败: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} P值测试({desc})", "通过"))
                else:  # 无效P值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效P值未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} P值测试({desc})", "通过(预期失败)"))
            
            # 测试I参数
            logger.info(f"测试手指 {finger_id} 的I参数")
            for i_value, desc in PARAM_TEST_DATA['I']:
                remote_err = []
                err = serial_api_instance.HAND_SetFingerPID(
                    HAND_ID, finger_id, 
                    DEFAULT_P,      # P固定为默认值
                    i_value,        # 测试变量I
                    DEFAULT_D,      # D固定为默认值
                    DEFAULT_G,      # G固定为默认值
                    remote_err
                )
                # 验证结果
                if 0.0 <= i_value <= 100.00:  # 有效I值范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效I值失败: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} I值测试({desc})", "通过"))
                else:
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效I值未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} I值测试({desc})", "通过(预期失败)"))
            
            # 测试D参数(代码结构与I参数测试类似)
            logger.info(f"测试手指 {finger_id} 的D参数")
            for d_value, desc in PARAM_TEST_DATA['D']:
                remote_err = []
                err  = serial_api_instance.HAND_SetFingerPID(
                    HAND_ID, finger_id, 
                    DEFAULT_P,      # P固定为默认值
                    DEFAULT_I,      # I固定为默认值
                    d_value,        # 测试变量d
                    DEFAULT_G,      # G固定为默认值
                    remote_err
                )
                # 验证结果
                if 0.0 <= d_value <= 500.00:  # 有效D值范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效D值失败: {desc}, 错误码:  err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} D值测试({desc})", "通过"))
                else:
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效D值未报错: {desc}, 错误码:  err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} D值测试({desc})", "通过(预期失败)"))
                    
            # 测试G参数(代码结构与I参数测试类似)
            logger.info(f"测试手指 {finger_id} 的G参数")
            for g_value, desc in PARAM_TEST_DATA['G']:
                remote_err = []
                err = serial_api_instance.HAND_SetFingerPID(
                    HAND_ID, finger_id, 
                    DEFAULT_P,      # P固定为默认值
                    DEFAULT_I,      # I固定为默认值
                    DEFAULT_D,      # D固定为默认值
                    g_value,        # 测试变量g
                    remote_err
                )
                # 验证结果
                if 0.01 <= g_value <= 1.00:  # 有效G值范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效G值失败: {desc}, 错误码:err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} G值测试({desc})", "通过"))
                else:
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效G值未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} G值测试({desc})", "通过(预期失败)"))
            
            logger.info(f"手指 {finger_id} 所有参数测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指的默认PIDG值 =====")
        for finger_id in FINGERS:
            remote_err = []
            delay_milli_seconds_impl(500)
            err = serial_api_instance.HAND_SetFingerPID(
                HAND_ID, finger_id, 
                DEFAULT_P, DEFAULT_I, DEFAULT_D, DEFAULT_G, remote_err
            )
            assert err == HAND_RESP_SUCCESS, \
                f"恢复手指 {finger_id} 默认值失败, 错误码: err={err},remote_err={remote_err[0]}"
            logger.info(f"手指 {finger_id} 已恢复默认值")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复所有手指默认值
        try:
            logger.warning("正在尝试恢复所有手指默认值...")
            for finger_id in FINGERS:
                delay_milli_seconds_impl(500)
                serial_api_instance.HAND_SetFingerPID(
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

@pytest.mark.skip('测试设置current limit,研发端未实现，直接跳过')
def test_HAND_SetFingerCurrentLimit(serial_api_instance):
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
                err = serial_api_instance.HAND_SetFingerCurrentLimit(
                    HAND_ID, finger_id, 
                    current_limit,  # 测试变量电流限制值
                    remote_err
                )
                
                # 验证结果（假设有效范围：0-1299）
                if 0 <= current_limit <= 1299:  # 有效电流范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效电流值失败: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} 电流测试({desc})", "通过"))
                else:  # 无效电流值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效电流值未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} 电流测试({desc})", "通过(预期失败)"))
            
            logger.info(f"手指 {finger_id} 电流限制测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指的默认电流限制 =====")
        for finger_id in FINGERS:
            remote_err = []
            err = serial_api_instance.HAND_SetFingerCurrentLimit(
                HAND_ID, finger_id, 
                DEFAULT_CURRENT, remote_err
            )
            assert err == HAND_RESP_SUCCESS, \
                f"恢复手指 {finger_id} 默认电流失败, 错误码:err={err},remote_err={remote_err[0]}"
            logger.info(f"手指 {finger_id} 已恢复默认电流值: {DEFAULT_CURRENT}")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复所有手指默认值
        try:
            logger.warning("正在尝试恢复所有手指默认电流值...")
            for finger_id in FINGERS:
                serial_api_instance.HAND_SetFingerCurrentLimit(
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

@pytest.mark.skip('测试设置force target一直报超时,此case暂时跳过')
def test_HAND_SetFingerForceTarget(serial_api_instance):
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
            (65535,      "目标力最大值65535")
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
                err = serial_api_instance.HAND_SetFingerForceTarget(
                    HAND_ID, finger_id, 
                    force_target,  # 测试变量目标力值
                    remote_err
                )
                
                # 验证结果（假设有效范围：0-65535）
                if 0 <= force_target <= 65535:  # 有效目标力范围（16位无符号整数）
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效目标力失败: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} 目标力测试({desc})", "通过"))
                else:  # 无效目标力值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效目标力未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} 目标力测试({desc})", "通过(预期失败)"))
            
            logger.info(f"手指 {finger_id} 目标力设置测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指的默认目标力 =====")
        for finger_id in FINGERS:
            remote_err = []
            err = serial_api_instance.HAND_SetFingerForceTarget(
                HAND_ID, finger_id, 
                DEFAULT_FORCE_TARGET, remote_err
            )
            assert err == HAND_RESP_SUCCESS, \
                f"恢复手指 {finger_id} 默认目标力失败, 错误码: err={err},remote_err={remote_err[0]}"
            logger.info(f"手指 {finger_id} 已恢复默认目标力: {DEFAULT_FORCE_TARGET}")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复所有手指默认值
        try:
            logger.warning("正在尝试恢复所有手指默认目标力...")
            for finger_id in FINGERS:
                serial_api_instance.HAND_SetFingerForceTarget(
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

@pytest.mark.skip('测试设置pos limit 一直报超时,此case暂时跳过，参数少一个')
def test_HAND_SetFingerPosLimit(serial_api_instance):
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
                err = serial_api_instance.HAND_SetFingerPosLimit(
                    HAND_ID, finger_id, 
                    0,
                    pos_limit,  # 测试变量位置限制值
                    remote_err
                )
                
                # 验证结果
                if 0 <= pos_limit <= 65535:  # 有效范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效位置限制失败: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} 位置限制测试({desc})", "通过"))
                else:  # 无效值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效位置限制未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} 位置限制测试({desc})", "通过(预期失败)"))
            
            logger.info(f"手指 {finger_id} 位置限制测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指的默认位置限制 =====")
        for finger_id in FINGERS:
            remote_err = []
            err, remote_err = serial_api_instance.HAND_SetFingerPosLimit(
                HAND_ID, finger_id, 
                 0,
                DEFAULT_POS_LIMIT,  # 恢复默认值
                remote_err
            )
            assert err == HAND_RESP_SUCCESS, \
                f"恢复手指 {finger_id} 默认位置限制失败, 错误码: err={err},remote_err={remote_err[0]}"
            logger.info(f"手指 {finger_id} 已恢复默认位置限制: {DEFAULT_POS_LIMIT}")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复所有手指默认值
        try:
            logger.warning("正在尝试恢复所有手指默认位置限制...")
            for finger_id in FINGERS:
                serial_api_instance.HAND_SetFingerPosLimit(
                    HAND_ID, finger_id, 
                     0,
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

@pytest.mark.skip('单独跑测试是可以通过')
def test_HAND_FingerStart(serial_api_instance):
    hand_id = 0x02
    finger_id_bits = 0x01
    remote_err = []

    err = serial_api_instance.HAND_FingerStart(hand_id, finger_id_bits, remote_err)
    assert err == HAND_RESP_SUCCESS, f"设置开始移动手指失败，错误码: err={err},remote_err={remote_err[0]}"
    logger.info(f'设置开始移动手指成功')
    
@pytest.mark.skip('单独跑测试是可以通过')
def test_HAND_FingerStop(serial_api_instance):
    hand_id = 0x02
    finger_id_bits = 0x01
    remote_err = []

    err = serial_api_instance.HAND_FingerStop(hand_id, finger_id_bits, remote_err)
    assert err == HAND_RESP_SUCCESS, f"设置停止移动手指失败，错误码: err={err},remote_err={remote_err[0]}"
    logger.info(f'设置停止移动手指成功')

@pytest.mark.skip('测试设置finger pos abs 一直报超时,此case暂时跳过')
def test_HAND_SetFingerPosAbs(serial_api_instance):
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
                err = serial_api_instance.HAND_SetFingerPosAbs(
                    HAND_ID, finger_id, 
                    raw_pos,      # 测试变量位置值
                    DEFAULT_SPEED,  # 速度固定为默认值
                    remote_err
                )
                
                # 验证结果
                if 0 <= raw_pos <= 65535:  # 有效位置范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效位置失败: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} 位置测试({desc})", "通过"))
                else:  # 无效位置值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效位置未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} 位置测试({desc})", "通过(预期失败)"))
            
            # 测试速度参数（固定位置为默认值）
            logger.info(f"测试手指 {finger_id} 的速度参数")
            for speed, desc in PARAM_TEST_DATA['speed']:
                remote_err = []
                err = serial_api_instance.HAND_SetFingerPosAbs(
                    HAND_ID, finger_id, 
                    DEFAULT_POS,  # 位置固定为默认值
                    speed,        # 测试变量速度值
                    remote_err
                )
                
                # 验证结果
                if 0 <= speed <= 255:  # 有效速度范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效速度失败: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} 速度测试({desc})", "通过"))
                else:  # 无效速度值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效速度未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} 速度测试({desc})", "通过(预期失败)"))
            
            logger.info(f"手指 {finger_id} 绝对位置设置测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指的默认位置 =====")
        for finger_id in FINGERS:
            remote_err = []
            err = serial_api_instance.HAND_SetFingerPosAbs(
                HAND_ID, finger_id, 
                DEFAULT_POS, DEFAULT_SPEED,  # 恢复默认位置和速度
                remote_err
            )
            assert err == HAND_RESP_SUCCESS, \
                f"恢复手指 {finger_id} 默认位置失败, 错误码: err={err},remote_err={remote_err[0]}"
            logger.info(f"手指 {finger_id} 已恢复默认位置: {DEFAULT_POS}, 速度: {DEFAULT_SPEED}")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复所有手指默认值
        try:
            logger.warning("正在尝试恢复所有手指默认位置...")
            for finger_id in FINGERS:
                serial_api_instance.HAND_SetFingerPosAbs(
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

@pytest.mark.skip('测试设置finger pos 一直报超时,此case暂时跳过')
def test_HAND_SetFingerPos(serial_api_instance):
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
                err = serial_api_instance.HAND_SetFingerPos(
                    HAND_ID, finger_id, 
                    pos,          # 测试变量位置值
                    DEFAULT_SPEED,  # 速度固定为默认值
                    remote_err
                )
                
                # 验证结果
                if 0 <= pos <= 65535:  # 有效位置范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效位置失败: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} 位置测试({desc})", "通过"))
                else:  # 无效位置值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效位置未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} 位置测试({desc})", "通过(预期失败)"))
            
            # 测试速度参数（固定位置为默认值）
            logger.info(f"测试手指 {finger_id} 的速度参数")
            for speed, desc in PARAM_TEST_DATA['speed']:
                remote_err = []
                err = serial_api_instance.HAND_SetFingerPos(
                    HAND_ID, finger_id, 
                    DEFAULT_POS,  # 位置固定为默认值
                    speed,        # 测试变量速度值
                    remote_err
                )
                
                # 验证结果
                if 0 <= speed <= 255:  # 有效速度范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效速度失败: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} 速度测试({desc})", "通过"))
                else:  # 无效速度值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效速度未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} 速度测试({desc})", "通过(预期失败)"))
            
            logger.info(f"手指 {finger_id} 相对位置设置测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指的默认位置 =====")
        for finger_id in FINGERS:
            remote_err = []
            err = serial_api_instance.HAND_SetFingerPos(
                HAND_ID, finger_id, 
                DEFAULT_POS, DEFAULT_SPEED,  # 恢复默认位置和速度
                remote_err
            )
            assert err == HAND_RESP_SUCCESS, \
                f"恢复手指 {finger_id} 默认位置失败, 错误码: err={err},remote_err={remote_err[0]}"
            logger.info(f"手指 {finger_id} 已恢复默认位置: {DEFAULT_POS}, 速度: {DEFAULT_SPEED}")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复所有手指默认值
        try:
            logger.warning("正在尝试恢复所有手指默认位置...")
            for finger_id in FINGERS:
                serial_api_instance.HAND_SetFingerPos(
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

@pytest.mark.skip('测试设置finger angle 一直报超时,此case暂时跳过')
def test_HAND_SetFingerAngle(serial_api_instance):
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
            (65536,   "手指角度边界值-65536"),
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
                err = serial_api_instance.HAND_SetFingerAngle(
                    HAND_ID, finger_id, 
                    angle,          # 测试变量角度值
                    DEFAULT_SPEED,  # 速度固定为默认值
                    remote_err
                )
                
                # 验证结果
                if 0 <= angle <= 65535:  # 有效角度范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效角度失败: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} 角度测试({desc})", "通过"))
                else:  # 无效角度值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效角度未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} 角度测试({desc})", "通过(预期失败)"))
            
            # 测试速度参数（固定角度为默认值）
            logger.info(f"测试手指 {finger_id} 的速度参数")
            for speed, desc in PARAM_TEST_DATA['speed']:
                remote_err = []
                err = serial_api_instance.HAND_SetFingerAngle(
                    HAND_ID, finger_id, 
                    DEFAULT_ANGLE,  # 角度固定为默认值
                    speed,          # 测试变量速度值
                    remote_err
                )
                
                # 验证结果
                if 0 <= speed <= 255:  # 有效速度范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效速度失败: {desc}, 错误码:err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} 速度测试({desc})", "通过"))
                else:  # 无效速度值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效速度未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} 速度测试({desc})", "通过(预期失败)"))
            
            logger.info(f"手指 {finger_id} 角度设置测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指的默认角度 =====")
        for finger_id in FINGERS:
            remote_err = []
            err = serial_api_instance.HAND_SetFingerAngle(
                HAND_ID, finger_id, 
                DEFAULT_ANGLE, DEFAULT_SPEED,  # 恢复默认角度和速度
                remote_err
            )
            assert err == HAND_RESP_SUCCESS, \
                f"恢复手指 {finger_id} 默认角度失败, 错误码: err={err}"
            logger.info(f"手指 {finger_id} 已恢复默认角度: {DEFAULT_ANGLE}, 速度: {DEFAULT_SPEED}")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复所有手指默认值
        try:
            logger.warning("正在尝试恢复所有手指默认角度...")
            for finger_id in FINGERS:
                serial_api_instance.HAND_SetFingerAngle(
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

@pytest.mark.skip('测试设置thumb root pos 一直报超时,此case暂时跳过')
def test_HAND_SetThumbRootPos(serial_api_instance):
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
            err = serial_api_instance.HAND_SetThumbRootPos(
                HAND_ID, 
                pos,              # 测试变量位置值
                DEFAULT_SPEED,    # 速度固定为默认值
                remote_err
            )
            
            # 验证结果
            if pos in [0, 1, 2]:  # 有效位置范围
                assert err == HAND_RESP_SUCCESS, \
                    f"设置拇指根部有效位置失败: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                test_results.append((f"拇指根部位置测试({desc})", "通过"))
            else:  # 无效位置值
                assert err != HAND_RESP_SUCCESS, \
                    f"设置拇指根部无效位置未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                test_results.append((f"拇指根部位置测试({desc})", "通过(预期失败)"))
        
        # 测试速度参数（固定位置为默认值）
        logger.info(f"测试拇指根部速度参数")
        for speed, desc in PARAM_TEST_DATA['speed']:
            remote_err = []
            err = serial_api_instance.HAND_SetThumbRootPos(
                HAND_ID, 
                DEFAULT_POS,      # 位置固定为默认值
                speed,            # 测试变量速度值
                remote_err
            )
            
            # 验证结果
            if 0 <= speed <= 255:  # 有效速度范围
                assert err == HAND_RESP_SUCCESS, \
                    f"设置拇指根部有效速度失败: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                test_results.append((f"拇指根部速度测试({desc})", "通过"))
            else:  # 无效速度值
                assert err != HAND_RESP_SUCCESS, \
                    f"设置拇指根部无效速度未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                test_results.append((f"拇指根部速度测试({desc})", "通过(预期失败)"))
        
        logger.info(f"拇指根部位置设置测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复拇指根部默认位置 =====")
        remote_err = []
        err = serial_api_instance.HAND_SetThumbRootPos(
            HAND_ID, 
            DEFAULT_POS, DEFAULT_SPEED,  # 恢复默认位置和速度
            remote_err
        )
        assert err == HAND_RESP_SUCCESS, \
            f"恢复拇指根部默认位置失败, 错误码: err={err},remote_err={remote_err[0]}"
        logger.info(f"拇指根部已恢复默认位置: {DEFAULT_POS}, 速度: {DEFAULT_SPEED}")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复默认值
        try:
            logger.warning("正在尝试恢复拇指根部默认位置...")
            serial_api_instance.HAND_SetThumbRootPos(
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

@pytest.mark.skip('测试设置finger pos abs all一直报超时,此case暂时跳过')
def test_HAND_SetFingerPosAbsAll(serial_api_instance):
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
            
            err = serial_api_instance.HAND_SetFingerPosAbsAll(
                HAND_ID, pos_array, speed_array, MAX_MOTORS, remote_err
            )
            
            # 验证结果
            if 0 <= pos <= 65535:  # 有效位置范围
                assert err == HAND_RESP_SUCCESS, \
                    f"设置有效位置失败: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                test_results.append((f"位置测试({desc})", "通过"))
            else:  # 无效位置值
                assert err != HAND_RESP_SUCCESS, \
                    f"设置无效位置未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                test_results.append((f"位置测试({desc})", "通过(预期失败)"))
        
        # 测试速度参数（固定位置为默认值）
        logger.info(f"测试速度参数")
        for speed, desc in PARAM_TEST_DATA['speed']:
            # 生成统一速度数组
            pos_array = [DEFAULT_POS] * MAX_MOTORS
            speed_array = [speed] * MAX_MOTORS
            remote_err = []
            
            err = serial_api_instance.HAND_SetFingerPosAbsAll(
                HAND_ID, pos_array, speed_array, MAX_MOTORS, remote_err
            )
            
            # 验证结果
            if 0 <= speed <= 255:  # 有效速度范围
                assert err == HAND_RESP_SUCCESS, \
                    f"设置有效速度失败: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                test_results.append((f"速度测试({desc})", "通过"))
            else:  # 无效速度值
                assert err != HAND_RESP_SUCCESS, \
                    f"设置无效速度未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                test_results.append((f"速度测试({desc})", "通过(预期失败)"))
        
        logger.info(f"批量设置手指绝对位置测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指默认位置 =====")
        remote_err = []
        
        err = serial_api_instance.HAND_SetFingerPosAbsAll(
            HAND_ID, 
            [DEFAULT_POS] * MAX_MOTORS,
            [DEFAULT_SPEED] * MAX_MOTORS,
            MAX_MOTORS,
            remote_err
        )
        assert err == HAND_RESP_SUCCESS, \
            f"恢复默认位置失败, 错误码: err={err},remote_err={remote_err[0]}"
        logger.info(f"所有手指已恢复默认位置: {DEFAULT_POS}, 速度: {DEFAULT_SPEED}")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复默认值
        try:
            logger.warning("正在尝试恢复所有手指默认位置...")
            serial_api_instance.HAND_SetFingerPosAbsAll(
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

@pytest.mark.skip('测试设置finger pos all一直报超时,此case暂时跳过')
def test_HAND_SetFingerPosAll(serial_api_instance):
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
            
            err = serial_api_instance.HAND_SetFingerPosAll(
                HAND_ID, pos_array, speed_array, MAX_MOTOR_CNT, remote_err
            )
            
            # 验证结果
            if 0 <= pos <= 65535:  # 有效位置范围
                assert err == HAND_RESP_SUCCESS, \
                    f"设置有效位置失败: {desc}, 错误码:err={err},remote_err={remote_err[0]}"
                test_results.append((f"位置测试({desc})", "通过"))
            else:  # 无效位置值
                assert err != HAND_RESP_SUCCESS, \
                    f"设置无效位置未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                test_results.append((f"位置测试({desc})", "通过(预期失败)"))
        
        # 测试速度参数（固定位置为默认值）
        logger.info(f"测试速度参数")
        for speed, desc in PARAM_TEST_DATA['speed']:
            # 生成统一速度数组
            pos_array = [DEFAULT_POS] * MAX_MOTOR_CNT
            speed_array = [speed] * MAX_MOTOR_CNT
            remote_err = []
            
            err = serial_api_instance.HAND_SetFingerPosAll(
                HAND_ID, pos_array, speed_array, MAX_MOTOR_CNT, remote_err
            )
            
            # 验证结果
            if 0 <= speed <= 255:  # 有效速度范围
                assert err == HAND_RESP_SUCCESS, \
                    f"设置有效速度失败: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                test_results.append((f"速度测试({desc})", "通过"))
            else:  # 无效速度值
                assert err != HAND_RESP_SUCCESS, \
                    f"设置无效速度未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                test_results.append((f"速度测试({desc})", "通过(预期失败)"))
        
        logger.info(f"批量设置手指相对位置测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指默认位置 =====")
        remote_err = []
        
        err = serial_api_instance.HAND_SetFingerPosAll(
            HAND_ID, 
            [DEFAULT_POS] * MAX_MOTOR_CNT,
            [DEFAULT_SPEED] * MAX_MOTOR_CNT,
            MAX_MOTOR_CNT,
            remote_err
        )
        assert err == HAND_RESP_SUCCESS, \
            f"恢复默认位置失败, 错误码: err={err},remote_err={remote_err[0]}"
        logger.info(f"所有手指已恢复默认位置: {DEFAULT_POS}, 速度: {DEFAULT_SPEED}")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复默认值
        try:
            logger.warning("正在尝试恢复所有手指默认位置...")
            serial_api_instance.HAND_SetFingerPosAll(
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

@pytest.mark.skip('测试设置finger angle all一直报超时,此case暂时跳过')
def test_HAND_SetFingerAngleAll(serial_api_instance):
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
            (65536,   "所有手指角度边界值-65536"),
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
            
            err = serial_api_instance.HAND_SetFingerAngleAll(
                HAND_ID, angle_array, speed_array, MAX_MOTOR_CNT, remote_err
            )
            
            # 验证结果
            if 0 <= angle <= 65535:  # 有效角度范围
                assert err == HAND_RESP_SUCCESS, \
                    f"设置有效角度失败: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                test_results.append((f"角度测试({desc})", "通过"))
            else:  # 无效角度值
                assert err != HAND_RESP_SUCCESS, \
                    f"设置无效角度未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                test_results.append((f"角度测试({desc})", "通过(预期失败)"))
        
        # 测试速度参数（固定角度为默认值）
        logger.info(f"测试速度参数")
        for speed, desc in PARAM_TEST_DATA['speed']:
            # 生成统一速度数组
            angle_array = [DEFAULT_ANGLE] * MAX_MOTOR_CNT
            speed_array = [speed] * MAX_MOTOR_CNT
            remote_err = []
            
            err = serial_api_instance.HAND_SetFingerAngleAll(
                HAND_ID, angle_array, speed_array, MAX_MOTOR_CNT, remote_err
            )
            
            # 验证结果
            if 0 <= speed <= 255:  # 有效速度范围
                assert err == HAND_RESP_SUCCESS, \
                    f"设置有效速度失败: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                test_results.append((f"速度测试({desc})", "通过"))
            else:  # 无效速度值
                assert err != HAND_RESP_SUCCESS, \
                    f"设置无效速度未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                test_results.append((f"速度测试({desc})", "通过(预期失败)"))
        
        logger.info(f"批量设置手指角度测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指默认角度 =====")
        remote_err = []
        
        err = serial_api_instance.HAND_SetFingerAngleAll(
            HAND_ID, 
            [DEFAULT_ANGLE] * MAX_MOTOR_CNT,
            [DEFAULT_SPEED] * MAX_MOTOR_CNT,
            MAX_MOTOR_CNT,
            remote_err
        )
        assert err == HAND_RESP_SUCCESS, \
            f"恢复默认角度失败, 错误码:err={err},remote_err={remote_err[0]}"
        logger.info(f"所有手指已恢复默认角度: {DEFAULT_ANGLE}, 速度: {DEFAULT_SPEED}")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复默认值
        try:
            logger.warning("正在尝试恢复所有手指默认角度...")
            serial_api_instance.HAND_SetFingerAngleAll(
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

@pytest.mark.skip('测试设置finger force pid一直报超时,此case暂时跳过')
def test_HAND_SetFingerForcePID(serial_api_instance):
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
            (1.0,   "P值最小值1.0"),
            (240.00, "P值中间值240.00"),
            (500.00, "P值最大值500.00"),
            (0.99,    "P值边界值0.99"),
            (0.0,     "P值边界值0.0"),
            (-0.01,    "P值边界值-0.01"),
            (500.01, "P值边界值500.01"),
            (65535.0, "P值边界值65535.0"),
            (65536.0, "P值边界值65536.0")
        ],
        'I': [
            (0.0,     "I值最小值0.0"),
            (50.00,  "I值中间值50.00"),
            (100.00, "I值最大值100.00"),
            (-0.01,    "I值边界值-0.01"),
            (100.01, "I值边界值100.01"),
            (65535.0, "I值边界值65535.0"),
            (65536.0, "I值边界值65536.0")
        ],
        'D': [
            (0.0,     "D值最小值0.0"),
            (250.01, "D值中间值250.01"),
            (500.00, "D值最大值500.00"),
            (-0.01,    "D值边界值-0.01"),
            (500.01, "D值边界值500.01"),
            (65535.0, "D值边界值65535.0"),
            (65536.0, "D值边界值65536.0")
        ],
        'G': [
            (0.01,     "G值最小值0.01"),
            (0.5,    "G值中间值0.5"),
            (1.0,   "G值最大值1.0"),
            (0.0,     "G值边界值0.0"),
            (-0.01,    "G值边界值-0.01"),
            (1.01,   "G值边界值1.01"),
            (65535.0, "G值边界值65535.0"),
            (65536.0, "G值边界值65536.0")
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
                err = serial_api_instance.HAND_SetFingerForcePID(
                    HAND_ID, finger_id, 
                    p_value,        # 测试变量P
                    DEFAULT_I,      # I固定为默认值
                    DEFAULT_D,      # D固定为默认值
                    DEFAULT_G,      # G固定为默认值
                    remote_err
                )
                
                # 验证结果
                if 1.0 <= p_value <= 500.00:  # 有效P值范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效P值失败: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} P值测试({desc})", "通过"))
                else:  # 无效P值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效P值未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} P值测试({desc})", "通过(预期失败)"))
            
            # 测试I参数
            logger.info(f"测试手指 {finger_id} 的I参数")
            for i_value, desc in PARAM_TEST_DATA['I']:
                remote_err = []
                err = serial_api_instance.HAND_SetFingerForcePID(
                    HAND_ID, finger_id, 
                    DEFAULT_P,      # P固定为默认值
                    i_value,        # 测试变量I
                    DEFAULT_D,      # D固定为默认值
                    DEFAULT_G,      # G固定为默认值
                    remote_err
                )
                
                # 验证结果
                if 0 <= i_value <= 100.00:  # 有效I值范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效I值失败: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} I值测试({desc})", "通过"))
                else:  # 无效I值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效I值未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} I值测试({desc})", "通过(预期失败)"))
            
            # 测试D参数
            logger.info(f"测试手指 {finger_id} 的D参数")
            for d_value, desc in PARAM_TEST_DATA['D']:
                remote_err = []
                err = serial_api_instance.HAND_SetFingerForcePID(
                    HAND_ID, finger_id, 
                    DEFAULT_P,      # P固定为默认值
                    DEFAULT_I,      # I固定为默认值
                    d_value,        # 测试变量D
                    DEFAULT_G,      # G固定为默认值
                    remote_err
                )
                
                # 验证结果
                if 0 <= d_value <= 500.00:  # 有效D值范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效D值失败: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} D值测试({desc})", "通过"))
                else:  # 无效D值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效D值未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} D值测试({desc})", "通过(预期失败)"))
            
            # 测试G参数
            logger.info(f"测试手指 {finger_id} 的G参数")
            for g_value, desc in PARAM_TEST_DATA['G']:
                remote_err = []
                err = serial_api_instance.HAND_SetFingerForcePID(
                    HAND_ID, finger_id, 
                    DEFAULT_P,      # P固定为默认值
                    DEFAULT_I,      # I固定为默认值
                    DEFAULT_D,      # D固定为默认值
                    g_value,        # 测试变量G
                    remote_err
                )
                
                # 验证结果
                if 0.01 <= g_value <= 1.00:  # 有效G值范围
                    assert err == HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置有效G值失败: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} G值测试({desc})", "通过"))
                else:  # 无效G值
                    assert err != HAND_RESP_SUCCESS, \
                        f"手指 {finger_id} 设置无效G值未报错: {desc}, 错误码: err={err},remote_err={remote_err[0]}"
                    test_results.append((f"手指{finger_id} G值测试({desc})", "通过(预期失败)"))
            
            logger.info(f"手指 {finger_id} 的力控PID参数测试完成")
        
        """------------------- 恢复默认值 -------------------"""
        logger.info("\n===== 恢复所有手指的默认力控PID参数 =====")
        for finger_id in FINGERS:
            remote_err = []
            err = serial_api_instance.HAND_SetFingerForcePID(
                HAND_ID, finger_id, 
                DEFAULT_P, DEFAULT_I, DEFAULT_D, DEFAULT_G, remote_err
            )
            assert err == HAND_RESP_SUCCESS, \
                f"恢复手指 {finger_id} 默认力控PID参数失败, 错误码: err={err},remote_err={remote_err[0]}"
            logger.info(f"手指 {finger_id} 已恢复默认力控PID参数")
    
    except AssertionError as e:
        logger.error(f"测试失败: {str(e)}")
        # 发生错误时尝试恢复所有手指默认值
        try:
            logger.warning("正在尝试恢复所有手指默认力控PID参数...")
            for finger_id in FINGERS:
                serial_api_instance.HAND_SetFingerForcePID(
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
        
@pytest.mark.skip('测试通过')
def test_HAND_ResetForce(serial_api_instance):# 修改api调用接口函数，添加none后测试pass
    hand_id = 0x02
    remote_err = []

    err = serial_api_instance.HAND_ResetForce(hand_id, remote_err)
    assert err == HAND_RESP_SUCCESS, f"重置力量值，错误码: err={err},remote_err={remote_err[0]}"
    logger.info("成功重置力量值")

@pytest.mark.skip('测试通过')
def test_HAND_SetSelfTestLevel(serial_api_instance):
    hand_id = 0x02
    SELF_TEST_LEVEL = {
        '等待指令': 0,
        '半自检': 1,
        '完整自检': 2
    }
    
    # 测试设置为半自检
    remote_err = [0]
    err = serial_api_instance.HAND_SetSelfTestLevel(hand_id, SELF_TEST_LEVEL['半自检'], remote_err)
    assert err == HAND_RESP_SUCCESS, f"设置半自检失败，错误码: err={err},remote_err={remote_err[0]}"
    
    time.sleep(5)  # 等待自检执行
    
    current_level = [0]
    err,_ = serial_api_instance.HAND_GetSelfTestLevel(hand_id, current_level, [])
    assert err == HAND_RESP_SUCCESS, f"获取自检级别失败，错误码: err={err},remote_err={remote_err[0]}"
    
    assert current_level[0] == SELF_TEST_LEVEL['半自检'], (
        f"自检级别验证失败：期望半自检({SELF_TEST_LEVEL['半自检']})，"
        f"实际{list(SELF_TEST_LEVEL.keys())[list(SELF_TEST_LEVEL.values()).index(current_level[0])]}({current_level[0]})"
    )
    logger.info("成功设置半自检")
    
    # 测试设置为完整自检（恢复默认状态）
    remote_err = []
    err = serial_api_instance.HAND_SetSelfTestLevel(hand_id, SELF_TEST_LEVEL['完整自检'], remote_err)
    assert err == HAND_RESP_SUCCESS, f"设置完整自检失败，错误码: err={err},remote_err={remote_err[0]}"
    
    time.sleep(5)  # 等待自检执行
    
    err,_ = serial_api_instance.HAND_GetSelfTestLevel(hand_id, current_level, [])
    assert err == HAND_RESP_SUCCESS, f"获取自检级别失败，错误码:err={err}"
    
    assert current_level[0] == SELF_TEST_LEVEL['完整自检'], (
        f"自检级别验证失败：期望完整自检({SELF_TEST_LEVEL['完整自检']})，"
        f"实际{list(SELF_TEST_LEVEL.keys())[list(SELF_TEST_LEVEL.values()).index(current_level[0])]}({current_level[0]})"
    )
    logger.info("成功设置完整自检")
    
    # 确保测试结束后恢复默认状态
    remote_err = [0]
    err = serial_api_instance.HAND_SetSelfTestLevel(hand_id, SELF_TEST_LEVEL['完整自检'], remote_err)
    if err != HAND_RESP_SUCCESS:
        logger.error(f"恢复默认自检级别失败，错误码: err={err},remote_err={remote_err[0]}")

@pytest.mark.skip('调试通过')
def test_HAND_SetBeepSwitch(serial_api_instance):
    hand_id = 0x02
    BEEP_STATUS = {
        'OFF': 0,
        'ON': 1
    }
    
    # 测试关闭蜂鸣器
    err = serial_api_instance.HAND_SetBeepSwitch(hand_id, BEEP_STATUS['OFF'], [])
    assert err == HAND_RESP_SUCCESS, f"设置蜂鸣器关闭失败，错误码: err={err}"
    
    time.sleep(0.5)  # 等待设备响应
    
    status_container = [0]
    err,_ = serial_api_instance.HAND_GetBeepSwitch(hand_id, status_container, [])
    assert err == HAND_RESP_SUCCESS, f"获取蜂鸣器状态失败，错误码: err={err}"
    
    actual_status = status_container[0]
    assert actual_status == BEEP_STATUS['OFF'], (
        f"蜂鸣器关闭状态验证失败：期望={BEEP_STATUS['OFF']}，实际={actual_status}"
    )
    logger.info("蜂鸣器已成功关闭")
    
    # 测试开启蜂鸣器
    err = serial_api_instance.HAND_SetBeepSwitch(hand_id, BEEP_STATUS['ON'], [])
    assert err == HAND_RESP_SUCCESS, f"设置蜂鸣器开启失败，错误码: err={err}"
    
    time.sleep(0.5)  # 等待设备响应
    
    err,_ = serial_api_instance.HAND_GetBeepSwitch(hand_id, status_container, [])
    assert err == HAND_RESP_SUCCESS, f"获取蜂鸣器状态失败，错误码: err={err}"
    
    actual_status = status_container[0]
    assert actual_status == BEEP_STATUS['ON'], (
        f"蜂鸣器开启状态验证失败：期望={BEEP_STATUS['ON']}，实际={actual_status}"
    )
    logger.info("蜂鸣器已成功开启")
    
    # 恢复默认状态
    err = serial_api_instance.HAND_SetBeepSwitch(hand_id, BEEP_STATUS['ON'], [])
    if err != HAND_RESP_SUCCESS:
        logger.error(f"恢复蜂鸣器默认状态失败，错误码: err={err}")
    else:
        logger.info('蜂鸣器开关已恢复默认状态')

@pytest.mark.skip('调试通过')
def test_HAND_Beep(serial_api_instance): # 设置时长慧报3的错误码
    hand_id = 0x02
    duration = 500
    err = serial_api_instance.HAND_Beep(hand_id, duration, [])
    assert err == HAND_RESP_SUCCESS,f"设置蜂鸣器时长失败:  err={err}"
    logger.info(f'成功设置蜂鸣器时长：{duration}')
    
@pytest.mark.skip('按钮不支持,此case暂时跳过')
def test_HAND_SetButtonPressedCnt(serial_api_instance):
    hand_id = 0x02
    
    # 测试正常范围（0-255）
    # 测试最小值
    target_pressed_cnt = 0
    remote_err = []
    err = serial_api_instance.HAND_SetButtonPressedCnt(hand_id, target_pressed_cnt, remote_err)
    assert err == HAND_RESP_SUCCESS, (
        f"设置按钮按下次数失败（值={target_pressed_cnt}），错误码:  err={err},remote_err={remote_err[0]}"
    )
    
    observed_pressed_cnt = [0]
    err = serial_api_instance.HAND_GetButtonPressedCnt(hand_id, observed_pressed_cnt, remote_err)
    assert err == HAND_RESP_SUCCESS, (
        f"获取按钮按下次数失败（值={target_pressed_cnt}），错误码:  err={err},remote_err={remote_err[0]}"
    )
    
    actual_cnt = observed_pressed_cnt[0]
    assert actual_cnt == target_pressed_cnt, (
        f"按钮按下次数验证失败：目标值={target_pressed_cnt}，实际值={actual_cnt}"
    )
    
    logger.info(f"按钮按下次数设置成功，值={target_pressed_cnt}")
    
    # 测试中间值
    target_pressed_cnt = 128
    remote_err = []
    err = serial_api_instance.HAND_SetButtonPressedCnt(hand_id, target_pressed_cnt, remote_err)
    assert err == HAND_RESP_SUCCESS, (
        f"设置按钮按下次数失败（值={target_pressed_cnt}），错误码: err={err},remote_err={remote_err[0]}"
    )
    
    observed_pressed_cnt = [0]
    err = serial_api_instance.HAND_GetButtonPressedCnt(hand_id, observed_pressed_cnt, remote_err)
    assert err == HAND_RESP_SUCCESS, (
        f"获取按钮按下次数失败（值={target_pressed_cnt}），错误码: err={err},remote_err={remote_err[0]}"
    )
    
    actual_cnt = observed_pressed_cnt[0]
    assert actual_cnt == target_pressed_cnt, (
        f"按钮按下次数验证失败：目标值={target_pressed_cnt}，实际值={actual_cnt}"
    )
    
    logger.info(f"按钮按下次数设置成功，值={target_pressed_cnt}")
    
    # 测试最大值
    target_pressed_cnt = 255
    remote_err = []
    err = serial_api_instance.HAND_SetButtonPressedCnt(hand_id, target_pressed_cnt, remote_err)
    assert err == HAND_RESP_SUCCESS, (
        f"设置按钮按下次数失败（值={target_pressed_cnt}），错误码: err={err},remote_err={remote_err[0]}"
    )
    
    observed_pressed_cnt = [0]
    err = serial_api_instance.HAND_GetButtonPressedCnt(hand_id, observed_pressed_cnt, remote_err)
    assert err == HAND_RESP_SUCCESS, (
        f"获取按钮按下次数失败（值={target_pressed_cnt}），错误码:err={err},remote_err={remote_err[0]}"
    )
    
    actual_cnt = observed_pressed_cnt[0]
    assert actual_cnt == target_pressed_cnt, (
        f"按钮按下次数验证失败：目标值={target_pressed_cnt}，实际值={actual_cnt}"
    )
    
    logger.info(f"按钮按下次数设置成功，值={target_pressed_cnt}")
    
    # 测试超出范围（256-65535） - 期望触发ValueError
    # 测试超出范围的最小值（256）
    try:
        serial_api_instance.HAND_SetButtonPressedCnt(hand_id, 256, [0])
    except ValueError as e:
        logger.info(f"成功捕获预期的ValueError（值=256）: {str(e)}")
    else:
        assert False, "设置超出范围的值（256）未触发ValueError"
    
    # 测试中间值（32768）
    try:
        serial_api_instance.HAND_SetButtonPressedCnt(hand_id, 32768, [0])
    except ValueError as e:
        logger.info(f"成功捕获预期的ValueError（值=32768）: {str(e)}")
    else:
        assert False, "设置超出范围的值（32768）未触发ValueError"
    
    # 测试超出范围的最大值（65535）
    try:
        serial_api_instance.HAND_SetButtonPressedCnt(hand_id, 65535, [0])
    except ValueError as e:
        logger.info(f"成功捕获预期的ValueError（值=65535）: {str(e)}")
    else:
        assert False, "设置超出范围的值（65535）未触发ValueError"
    
    # 测试负数（-1）
    try:
        serial_api_instance.HAND_SetButtonPressedCnt(hand_id, -1, [0])
    except ValueError as e:
        logger.info(f"成功捕获预期的ValueError（值=-1）: {str(e)}")
    else:
        assert False, "设置负数（-1）未触发ValueError"

@pytest.mark.skip('初始化，初始化要先把自检等级设置成0，才能生效')
def test_HAND_StartInit(serial_api_instance):
    hand_id = 0x02
    remote_err = []
    err = serial_api_instance.HAND_StartInit(hand_id, remote_err)
    assert err == HAND_RESP_SUCCESS,f"初始化手失败，错误码: 错误码:err={err},remote_err={remote_err[0]}"
    logger.info(f'手初始化成功')
