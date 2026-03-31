#!/usr/bin/env python3
# 转换 3.16 测试 CSV 数据为仪表板 JSON 格式

import csv
import json
from datetime import datetime

# 仓库代码映射
WAREHOUSE_MAP = {
    '美国仓': 'us_warehouse',
    '嘉兴仓_IDP': 'jiaxing',
    '加拿大仓': 'ca_warehouse',
    '海外仓': 'overseas',
}

# 国家代码映射
COUNTRY_MAP = {
    '美国': 'US',
    '加拿大': 'CA',
    '澳大利亚': 'AU',
    '英国': 'GB',
    '挪威': 'NO',
    '波多黎各': 'PR',
}

def parse_date(date_str):
    """解析日期字符串"""
    if not date_str or date_str.strip() == '':
        return ''
    try:
        # 处理 2026/1/29 或 2026/2/12 4:28 格式
        date_str = date_str.strip()
        if ' ' in date_str:
            date_part = date_str.split(' ')[0]
        else:
            date_part = date_str
        
        parts = date_part.split('/')
        if len(parts) == 3:
            year, month, day = parts
            return f"{year}-{int(month):02d}-{int(day):02d}"
        return date_str
    except:
        return date_str

def calculate_actual_days(ship_date, delivery_date):
    """计算实际天数"""
    if not ship_date or not delivery_date:
        return 0.0
    try:
        ship = datetime.strptime(ship_date.split(' ')[0], '%Y-%m-%d')
        delivery = datetime.strptime(delivery_date.split(' ')[0], '%Y-%m-%d')
        return (delivery - ship).days + (delivery - ship).seconds / 86400
    except:
        return 0.0

def convert_row(row):
    """转换单行数据"""
    # 提取基础字段
    order_no = row.get('订单号', '')
    ship_no = row.get('发货单号', '')
    site_code = row.get('站点', 'M')
    customer_shipping = row.get('客户选择的运送方式', '')
    actual_shipping = row.get('物流方式', '')
    product_l3 = row.get('三级产品', '')
    warehouse_raw = row.get('发货地', '')
    country_raw = row.get('收货地', '')
    package_count = int(row.get('商品数量', 1) or 1)
    shipping_status = row.get('订单发货状态', '')
    promise_ship_date = row.get('承诺最晚发货时间', '')
    ship_date = row.get('发货时间', '')
    promise_delivery = row.get('承诺最晚收货时间', '')
    delivery_date = row.get('妥投时间', '')
    delivery_days = row.get('妥投时效', '0')
    weight = row.get('实际/预估重量', '0')
    revenue = row.get('订单收入', '0')
    logistics_cost = row.get('物流运费 (实际运费/预估运费)', '0')
    is_split = row.get('是否分单', '否')
    split_reason = row.get('分单原因', '')
    is_presale = row.get('预售订单', '否')
    is_influencer = row.get('红人订单', '否')
    is_merged = row.get('发货合单', '否')
    after_sales = row.get('售后', '')
    product_l1 = row.get('一级产品', 'Standard')
    product_l2 = row.get('二级产品', 'JS')
    
    # 解析日期
    ship_date_parsed = parse_date(ship_date)
    delivery_date_parsed = parse_date(delivery_date)
    promise_delivery_parsed = parse_date(promise_delivery)
    
    # 计算实际天数
    try:
        actual_days = float(delivery_days) if delivery_days else 0.0
    except:
        actual_days = 0.0
    
    # 计算承诺天数
    try:
        if ship_date_parsed and promise_delivery_parsed:
            ship_dt = datetime.strptime(ship_date_parsed, '%Y-%m-%d')
            promise_dt = datetime.strptime(promise_delivery_parsed, '%Y-%m-%d')
            promise_days = (promise_dt - ship_dt).days
        else:
            promise_days = 10
    except:
        promise_days = 10
    
    # 是否超时
    is_overdue = '否'
    if actual_days > 0 and promise_days > 0 and actual_days > promise_days:
        is_overdue = '是'
    
    # 仓库代码映射
    warehouse_code = 'jiaxing'  # 默认
    for key, value in WAREHOUSE_MAP.items():
        if key in warehouse_raw:
            warehouse_code = value
            break
    
    # 国家代码映射
    country_code = 'US'  # 默认
    for key, value in COUNTRY_MAP.items():
        if key in country_raw:
            country_code = value
            break
    
    # 客户运送方式映射
    shipping_method_map = {
        '中': 'Standard Shipping',
        '快': 'Expedited Shipping',
        '普': 'Standard Shipping',
        'Quick': 'QuickShip',
    }
    customer_shipping_mapped = customer_shipping
    for key, value in shipping_method_map.items():
        if key in customer_shipping:
            customer_shipping_mapped = value
            break
    
    # 生成 order_date（发货日期前 1-3 天）
    order_date = ''
    if ship_date_parsed:
        try:
            ship_dt = datetime.strptime(ship_date_parsed, '%Y-%m-%d')
            order_dt = ship_dt  # 简化：订单日期=发货日期
            order_date = order_dt.strftime('%Y%m%d')
        except:
            order_date = ship_date_parsed.replace('-', '')
    
    # year_month
    year_month = ''
    if ship_date_parsed and len(ship_date_parsed) >= 7:
        year = ship_date_parsed[2:4]
        month = ship_date_parsed[5:7]
        year_month = f"{year}{month}"
    
    # 构建记录
    record = {
        'order_no': order_no,
        'ship_no': ship_no,
        'ship_date': ship_date_parsed,
        'site_code': site_code,
        'customer_shipping_method': customer_shipping_mapped,
        'actual_shipping_method': actual_shipping,
        'tracking_no': f"TRK{order_no[-10:]}" if order_no else '',
        'country_code': country_code,
        'province': country_raw,
        'package_count': package_count,
        'shipping_status': shipping_status,
        'promise_days': round(promise_days, 2),
        'order_date': order_date,
        'promise_delivery_date': promise_delivery_parsed,
        'delivery_date': delivery_date_parsed,
        'actual_days': round(actual_days, 2),
        'is_overdue': is_overdue,
        'weight_kg': float(weight) if weight else 0.0,
        'logistics_cost': float(logistics_cost) if logistics_cost else 0.0,
        'year_month': year_month,
        'item_count': package_count,
        'revenue': float(revenue) if revenue else 0.0,
        'product_l1': product_l1,
        'product_l2': product_l2,
        'product_l3': product_l3 if product_l3 else actual_shipping,
        'warehouse_code': warehouse_code,
        'order_type': 'shipped' if '发货' in shipping_status else 'pending',
        'is_split': '是' if is_split == '是' else '否',
        'split_reason': split_reason,
        'is_presale': is_presale,
        'is_influencer': is_influencer,
        'is_merged': is_merged,
        'after_sales': after_sales,
    }
    
    return record

def main():
    # 读取 CSV
    csv_file = "/home/tardis/.openclaw/media/inbound/3.16 测试_-_Sheet1---2ae45242-5cb9-42be-a5e8-421b3399c21e"
    output_json = '/home/tardis/.openclaw/workspace/qq-repo/demo_data_real.min.json'
    
    records = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            record = convert_row(row)
            records.append(record)
    
    # 写入 JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 转换完成！共 {len(records)} 条记录")
    print(f"📁 输出文件：{output_json}")

if __name__ == '__main__':
    main()
