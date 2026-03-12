#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V3.14 数据底稿 CSV 转 JSON 转换器
自动识别列名映射，支持 GBK 编码
"""

import csv
import json
import sys

# 列名映射（中文 → 目标字段）
COLUMN_MAP = {
    '订单号': 'order_no',
    '发货单号': 'ship_no',
    '站点': 'site',
    '客户选择的运送方式': 'speed_type',
    '物流方式': 'product_l3',
    '实际物流方式': 'product_l3_actual',
    '物流单号': 'tracking_no',
    '发货地': 'warehouse',
    '收货地': 'country',
    '商品数量': 'item_count',
    '订单发货状态': 'order_status',
    '承诺最晚发货时间': 'promise_ship_date',
    '发货时间': 'ship_date',
    '承诺最晚收货时间': 'promise_delivery_date',
    '妥投时间': 'delivery_date',
    '妥投时效': 'delivery_days',
    '商品成本': 'cost',
    '实际/预估重量': 'weight_kg',
    '订单收入': 'revenue',
    '其他收入': 'other_revenue',
    '运费': 'shipping_fee',
    '保价费': 'insurance_fee',
    '运保费收入': 'shipping_insurance_revenue',
    '实际运费': 'actual_shipping_fee',
    '物流运费 (实际运费/预估运费)': 'logistics_cost',
    '是否分单': 'is_split',
    '分单原因': 'split_reason',
    '一级产品': 'product_l1',
    '二级产品': 'product_l2',
    '三级产品': 'product_l3',
}

# 国家代码映射
COUNTRY_MAP = {
    '美国': 'US', 'US': 'US', 'USA': 'US',
    '英国': 'UK', 'UK': 'UK', 'GB': 'UK',
    '加拿大': 'CA', 'CA': 'CA', 'Canada': 'CA',
    '澳大利亚': 'AU', 'AU': 'AU', 'Australia': 'AU',
}

# 仓库代码映射（从发货地提取）
def get_warehouse_code(warehouse):
    if '嘉兴' in warehouse or '中国' in warehouse:
        return 'jiaxing'
    return 'overseas'

# 速度类型映射
def get_speed_type_code(speed_type):
    if '快' in speed_type or 'Expedited' in speed_type or 'Express' in speed_type:
        return '快'
    return '慢'

# 产品 L1 标准列表
PRODUCT_L1_STANDARD = [
    'JC-USPS', 'JC-UPS Ground Return', 'HABIT POST delivery', 'HABIT Commercial delivery',
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
    'CK1-usps', 'USPS Return', '4PX-Linkpost Economy'
]

def get_product_l1(product_l3):
    if product_l3 in PRODUCT_L1_STANDARD:
        return 'Standard'
    if product_l3 in ['FedEx Priority', 'FedEx Economy', 'DHL Express', 'AWPHK-DHL MAX']:
        return 'Expedited'
    return 'Standard'

def convert_number(value, default=0):
    if value is None or value == '':
        return default
    try:
        return round(float(value), 2)
    except:
        return default

def convert_date(date_str):
    """转换日期格式：2026-3-12 → 2026-03-12"""
    if not date_str or date_str == '':
        return ''
    # 处理带时间的日期
    if ' ' in date_str:
        date_str = date_str.split(' ')[0]
    parts = date_str.split('-')
    if len(parts) == 3:
        return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
    return date_str

def convert_csv_to_json(csv_path, json_path):
    result = []
    
    # 尝试不同编码读取
    encodings = ['gbk', 'utf-8', 'utf-8-sig']
    data = None
    
    for encoding in encodings:
        try:
            with open(csv_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                data = list(reader)
                print(f"✅ 使用 {encoding} 编码成功读取，共 {len(data)} 行")
                break
        except Exception as e:
            print(f"⚠️  {encoding} 编码读取失败：{e}")
    
    if not data:
        print("❌ 无法读取 CSV 文件")
        return 0
    
    # 显示检测到的列名
    print(f"\n📋 检测到的列名：{list(data[0].keys())[:10]}...")
    
    # 转换数据
    for row in data:
        # 获取字段值（尝试不同列名）
        def get_value(*names):
            for name in names:
                if name in row and row[name]:
                    return row[name].strip()
                # 尝试映射后的列名
                mapped = COLUMN_MAP.get(name)
                if mapped and mapped in row and row[mapped]:
                    return row[mapped].strip()
            return ''
        
        product_l3 = get_value('物流方式', 'product_l3', '实际物流方式')
        country = get_value('收货地', 'country')
        warehouse = get_value('发货地', 'warehouse')
        
        record = {
            'order_no': get_value('订单号', 'order_no'),
            'ship_no': get_value('发货单号', 'ship_no'),
            'order_date': convert_date(get_value('发货时间', 'ship_date').split(' ')[0] if ' ' in get_value('发货时间', 'ship_date') else get_value('发货时间', 'ship_date')),
            'site': get_value('站点', 'site') or 'M',
            'speed_type': get_value('客户选择的运送方式', 'speed_type') or '普通',
            'product_l3': product_l3,
            'tracking_no': get_value('物流单号', 'tracking_no'),
            'warehouse': warehouse,
            'country': country,
            'item_count': convert_number(get_value('商品数量', 'item_count'), 1),
            'order_status': 'shipped' if '已发货' in get_value('订单发货状态', 'order_status') else 'unshipped',
            'promise_ship_date': convert_date(get_value('承诺最晚发货时间', 'promise_ship_date')),
            'ship_date': convert_date(get_value('发货时间', 'ship_date')),
            'promise_delivery_date': convert_date(get_value('承诺最晚收货时间', 'promise_delivery_date')),
            'delivery_date': convert_date(get_value('妥投时间', 'delivery_date')),
            'delivery_days': convert_number(get_value('妥投时效', 'delivery_days'), 0),
            'weight_kg': convert_number(get_value('实际/预估重量', 'weight_kg'), 0),
            'logistics_cost': convert_number(get_value('物流运费 (实际运费/预估运费)', 'logistics_cost'), 0),
            'ship_month': '',  # 可以从 ship_date 提取
            'order_month': '',
            'product_l1': get_value('一级产品', 'product_l1') or get_product_l1(product_l3),
            'is_overdue_ship': '否',
            'is_overdue_delivery': '未超期' if get_value('妥投时间', 'delivery_date') else '未妥投',
            'overdue_days': 0,
            'supplier': '',  # 可以从物流方式推断
            'promise_days': 0,
            'package_count': 1,
            'order_count': 1,
            'revenue': convert_number(get_value('订单收入', 'revenue'), 0),
            'order_type': 'shipped',
            'country_code': COUNTRY_MAP.get(country, 'OTHER'),
            'warehouse_code': get_warehouse_code(warehouse),
            'speed_type_code': get_speed_type_code(get_value('客户选择的运送方式', 'speed_type')),
            'product_l2': get_value('二级产品', 'product_l2'),
        }
        
        # 计算 ship_month
        if record['ship_date']:
            parts = record['ship_date'].split('-')
            if len(parts) >= 2:
                record['ship_month'] = parts[0][2:] + parts[1]
        
        # 计算 promise_days
        if record['promise_ship_date'] and record['ship_date']:
            try:
                from datetime import datetime
                promise = datetime.strptime(record['promise_ship_date'], '%Y-%m-%d')
                ship = datetime.strptime(record['ship_date'], '%Y-%m-%d')
                record['promise_days'] = (promise - ship).days + 1
            except:
                pass
        
        result.append(record)
    
    # 保存 JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 转换完成！")
    print(f"   输出文件：{json_path}")
    print(f"   记录数：{len(result)}")
    
    return len(result)

if __name__ == '__main__':
    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'V3.14 数据底稿.csv'
    json_file = sys.argv[2] if len(sys.argv) > 2 else 'demo_data_real.json'
    
    convert_csv_to_json(csv_file, json_file)
