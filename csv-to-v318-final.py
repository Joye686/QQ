#!/usr/bin/env python3
"""将物流 CSV 转换为 v3.18 LocalStorage 格式"""
import csv
import json
import sys

def convert_csv_to_v318(input_file, output_file):
    mapped_data = []
    
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # 获取字段名列表（避免字段名包含特殊字符的问题）
            keys = list(row.keys())
            
            # 物流运费字段是第 24 个（索引 23）
            logistics_key = keys[23] if len(keys) > 23 else None
            logistics_cost = float(row[logistics_key]) if logistics_key and row.get(logistics_key) else 0.0
            
            warehouse_code = row.get('发货地', '')
            warehouse_type = 'jiaxing'
            if any(x in warehouse_code for x in ['英国', '美国', '加拿大']):
                warehouse_type = 'overseas'
            
            status = row.get('订单发货状态', '')
            order_type = 'unshipped'
            if '已发货' in status:
                order_type = 'shipped'
            elif '部分' in status:
                order_type = 'partial'
            
            mapped_row = {
                "order_no": row.get('订单号', ''),
                "ship_no": row.get('发货单号', ''),
                "site_code": row.get('站点', ''),
                "customer_shipping_method": row.get('客户选择的运送方式', ''),
                "product_l1": row.get('一级产品', ''),
                "product_l2": row.get('二级产品', ''),
                "product_l3": row.get('三级产品', ''),
                "actual_shipping_method": row.get('实际物流方式', ''),
                "warehouse_code": warehouse_code,
                "country_code": row.get('收货地', ''),
                "item_count": float(row.get('商品数量', 0) or 0),
                "shipping_status": status,
                "ship_date": row.get('发货时间', ''),
                "delivery_date": row.get('妥投时间', ''),
                "actual_days": float(row.get('妥投时效', 0) or 0),
                "weight_kg": float(row.get('实际/预估重量', 0) or 0),
                "revenue": float(row.get('订单收入', 0) or 0),
                "other_revenue": float(row.get('其他收入', 0) or 0),
                "freight": float(row.get('运费', 0) or 0),
                "insurance_fee": float(row.get('保价费', 0) or 0),
                "freight_insurance_revenue": float(row.get('运保费收入', 0) or 0),
                "actual_freight": 0,
                "logistics_cost": logistics_cost,
                "is_split": row.get('是否分单', ''),
                "split_reason": row.get('分单原因', ''),
                "manual_split_reason": row.get('手动分单原因', ''),
                "is_presale": "",
                "is_influencer": "",
                "is_merged": "",
                "is_presale_merged": "",
                "pre_merge_logistics_cost": 0,
                "after_sales": "",
                "warehouse_type": warehouse_type,
                "order_type": order_type
            }
            mapped_data.append(mapped_row)
    
    # 输出
    output = {
        "data": mapped_data,
        "count": len(mapped_data),
        "exchange_rates": {
            "2026-01": 7.15,
            "2026-02": 7.20,
            "2026-03": 6.9236
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    # 统计
    total_cost = sum(d['logistics_cost'] for d in mapped_data)
    avg_cost = total_cost / len(mapped_data) if mapped_data else 0
    
    print(f"✅ 转换成功！")
    print(f"   数据条数：{len(mapped_data)}")
    print(f"   物流运费样例：{mapped_data[0]['logistics_cost']}")
    print(f"   物流运费平均：{avg_cost:.2f}")
    print(f"   输出文件：{output_file}")
    print(f"\n📋 导入方法：")
    print(f"1. 打开 v3.18 仪表板页面")
    print(f"2. 按 F12 打开开发者工具，进入 Console")
    print(f"3. 执行:")
    print(f"   fetch('v318-data.json')")
    print(f"     .then(r => r.json())")
    print(f"     .then(d => {{")
    print(f"       localStorage.setItem('logistics_rawData', JSON.stringify(d.data));")
    print(f"       localStorage.setItem('logistics_exchangeRates', JSON.stringify(d.exchange_rates));")
    print(f"       location.reload();")
    print(f"     }})")

if __name__ == '__main__':
    input_file = sys.argv[1] if len(sys.argv) > 1 else '未命名表格_-_Sheet1_1---4de41371-060e-4bcf-94eb-84c5a84cdea8'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'v318-data.json'
    convert_csv_to_v318(input_file, output_file)
