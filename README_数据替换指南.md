# 📦 运费数据替换指南 (V3.14)

## 快速开始

### 步骤 1：准备你的 CSV 文件

你的 CSV 文件应该包含以下列（列名可以不同，但需要有这些数据）：

**必填字段：**
- `order_no` - 订单号
- `ship_no` - 发货单号
- `ship_date` - 发货日期 (YYYY-MM-DD)
- `warehouse` - 仓库名称 (嘉兴仓/美国仓等)
- `country` - 国家 (美国/英国等)
- `logistics_cost` - 物流费用
- `weight_kg` - 重量 (KG)
- `item_count` - 商品数量

**可选字段：**
- `product_l3` - 三级产品 (如 JC-USPS, HABIT POST delivery 等)
- `order_date` - 订单日期
- `delivery_date` - 妥投日期
- `tracking_no` - 追踪号
- `revenue` - 订单收入

### 步骤 2：放置文件

把你的 CSV 文件放到这个目录：
```
/home/tardis/.openclaw/workspace/qq-repo/shipping_fee_list.csv
```

### 步骤 3：运行转换脚本

```bash
cd /home/tardis/.openclaw/workspace/qq-repo
python3 convert_csv_to_json.py shipping_fee_list.csv demo_data_real.json
```

### 步骤 4：刷新仪表板

在浏览器中打开 `logistics-dashboard-v3.14.html`，数据已自动更新！

---

## 如果你的 CSV 列名不同

编辑 `convert_csv_to_json.py`，修改 `COLUMN_MAPPING`：

```python
COLUMN_MAPPING = {
    'order_no': '你的订单号列名',
    'ship_no': '你的发货单号列名',
    'ship_date': '你的发货日期列名',
    # ... 其他字段
}
```

---

## 国家/仓库自动映射

脚本会自动识别以下名称：

**国家：**
- 美国/US/USA → US
- 英国/UK/GB → UK
- 加拿大/CA → CA
- 澳大利亚/AU → AU
- 其他 → OTHER

**仓库：**
- 嘉兴仓/嘉兴/中国仓 → jiaxing
- 美国仓/海外仓/海外 → overseas

---

## 需要帮助？

把你的 CSV 前几行发给助手，我可以帮你调整映射配置！
