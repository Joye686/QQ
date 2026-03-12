#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运费清单 CSV 转 JSON 转换脚本
将 shipping_fee_list.csv 转换为 demo_data_real.json 格式
"""

import csv
import json
from datetime import datetime

# 字段映射 - 如果你的 CSV 列名不同，在这里修改
COLUMN_MAPPING = {
    'order_no': 'order_no',           # 订单号
    'ship_no': 'ship_no',             # 发货单号
    'order_date': 'order_date',       # 订单日期 YYYY-MM-DD
    'site': 'site',                   # 站点 M/W/R
    'speed_type': 'speed_type',       # 运送方式 快速/普通
    'product_l3': 'product_l3',       # 三级产品
    'tracking_no': 'tracking_no',     # 追踪号
    'warehouse': 'warehouse',         # 仓库名称
    'country': 'country',             # 国家名称
    'item_count': 'item_count',       # 商品数量
    'order_status': 'order_status',   # 订单状态
    'promise_ship_date': 'promise_ship_date',  # 承诺发货日期
    'ship_date': 'ship_date',         # 实际发货日期
    'promise_delivery_date': 'promise_delivery_date',  # 承诺送达日期
    'delivery_date': 'delivery_date', # 实际送达日期
    'delivery_days': 'delivery_days', # 送达天数
    'weight_kg': 'weight_kg',         # 重量 KG
    'logistics_cost': 'logistics_cost',  # 物流费用
    'ship_month': 'ship_month',       # 发货月份 YYMM
    'order_month': 'order_month',     # 订单月份 YYMM
    'product_l1': 'product_l1',       # 一级产品 Standard/Expedited
    'is_overdue_ship': 'is_overdue_ship',    # 是否超期发货
    'is_overdue_delivery': 'is_overdue_delivery',  # 是否超期送达
    'overdue_days': 'overdue_days',   # 超期天数
    'supplier': 'supplier',           # 供应商
    'promise_days': 'promise_days',   # 承诺天数
    'package_count': 'package_count', # 包裹数
    'order_count': 'order_count',     # 订单数
    'revenue': 'revenue',             # 收入
    'order_type': 'order_type',       # 订单类型 shipped/partial/unshipped
    'country_code': 'country_code',   # 国家代码 US/UK/CA/AU/OTHER
    'warehouse_code': 'warehouse_code',  # 仓库代码 jiaxing/overseas
    'speed_type_code': 'speed_type_code',  # 速度代码 快/慢
    'product_l2': 'product_l2'        # 二级产品
}

# 国家代码映射
COUNTRY_MAP = {
    '美国': 'US', 'US': 'US', 'USA': 'US',
    '英国': 'UK', 'UK': 'UK', 'GB': 'UK',
    '加拿大': 'CA', 'CA': 'CA', 'Canada': 'CA',
    '澳大利亚': 'AU', 'AU': 'AU', 'Australia': 'AU',
}

# 仓库代码映射
WAREHOUSE_MAP = {
    '嘉兴仓': 'jiaxing', '嘉兴': 'jiaxing', '中国仓': 'jiaxing',
    '美国仓': 'overseas', '海外仓': 'overseas', '海外': 'overseas',
    '英国仓': 'overseas', '加拿大仓': 'overseas',
}

# 速度类型映射
SPEED_MAP = {
    '快速': '快', '快': '快', 'Expedited': '快',
    '普通': '慢', '慢': '慢', 'Standard': '慢',
}

# 产品一级映射（根据产品 L3 自动推断）
PRODUCT_L1_MAP = {
    'Standard': ['JC-USPS', 'JC-UPS Ground Return', 'HABIT POST delivery', 'HABIT Commercial delivery',
                 'Yanwen Airmail Registered', 'Yanwen Huixuan', 'Yanwen Fully-tracked',
                 'YUNTU THPHR', 'Yuntu registration', 'yuntu remote', 'Yuntu Commercial delivery',
                 'CNE clothing line', 'CNE Global Smart', 'CNE global priority',
                 'liumai-USPS', 'Liumai L01 USA', 'liumai L01',
                 'JS EXPRESS', 'JS clothing line', 'JS Super Express',
                 'MPwarehouse-RM', 'MP-Return-RM',
                 'LTWarehouse-CAPOST', 'LTWarehouse-UNIUNI', 'LT-CAPOST Expedited',
                 'LTRemote-USPS-K', 'LT-Return-CA', 'LT-Return-USPS',
                 'US-UNI', 'US-UNI2', 'Happy Returns',
                 'Winit Fulfillment-2D', 'Winit Fulfillment-5D', 'Winit Fulfillment-7D',
                 'CK1-usps', 'USPS Return', '4PX-Linkpost Economy'],
    'Expedited': ['FedEx Priority', 'FedEx Economy', 'DHL Express', 'AWPHK-DHL MAX']
}

def get_product_l1(product_l3):
    """根据产品 L3 推断产品 L1"""
    for l1, l3_list in PRODUCT_L1_MAP.items():
        if product_l3 in l3_list:
            return l1
    # 默认返回 Standard
    return 'Standard'

def convert_value(key, value):
    """转换字段值类型"""
    if value is None or value == '':
        return ''
    
    # 数字类型
    if key in ['item_count', 'package_count', 'order_count', 'overdue_days']:
        try:
            return int(float(value))
        except:
            return 0
    
    if key in ['weight_kg', 'logistics_cost', 'revenue', 'promise_days', 'delivery_days']:
        try:
            return round(float(value), 2)
        except:
            return 0.0
    
    # 国家代码映射
    if key == 'country_code':
        return COUNTRY_MAP.get(value, 'OTHER')
    
    # 仓库代码映射
    if key == 'warehouse_code':
        return WAREHOUSE_MAP.get(value, 'jiaxing')
    
    # 速度类型映射
    if key == 'speed_type_code':
        return SPEED_MAP.get(value, '慢')
    
    # 产品 L1 自动推断
    if key == 'product_l1' and value in ['', None]:
        return 'Standard'
    
    return value

def convert_csv_to_json(csv_path, json_path):
    """CSV 转 JSON"""
    result = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            record = {}
            
            for json_key, csv_key in COLUMN_MAPPING.items():
                # 如果 CSV 中有这个列
                if csv_key in row:
                    value = row[csv_key].strip() if row[csv_key] else ''
                else:
                    value = ''
                
                # 特殊处理：产品 L1 自动推断
                if json_key == 'product_l1' and value in ['', None]:
                    product_l3 = row.get('product_l3', '')
                    value = get_product_l1(product_l3.strip() if product_l3 else '')
                
                record[json_key] = convert_value(json_key, value)
            
            result.append(record)
    
    # 写入 JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 转换完成！")
    print(f"   输入：{csv_path}")
    print(f"   输出：{json_path}")
    print(f"   记录数：{len(result)}")
    
    return len(result)

if __name__ == '__main__':
    import sys
    
    # 默认路径
    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'shipping_fee_list.csv'
    json_file = sys.argv[2] if len(sys.argv) > 2 else 'demo_data_real.json'
    
    convert_csv_to_json(csv_file, json_file)
