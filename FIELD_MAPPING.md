# 物流分析仪表板 v3.17.7 - 完整字段映射文档

## 📋 数据源信息

- **源文件**: 3.16 测试 - Sheet1.csv
- **总字段数**: 34 个
- **数据行数**: 1087 条
- **筛选依据**: 发货时间（ship_date）

---

## 🗂️ 字段映射表

| 分类 | 中文字段名 | 建议英文字段名 | 数据类型 | 示例值 | 用途说明 |
|------|-----------|--------------|---------|--------|---------|
| **基础信息** |
|  | `订单号` | `order_no` | String | `B1` | 订单唯一标识 |
|  | `发货单号` | `ship_no` | String | `A1` | 包裹唯一标识 |
|  | `站点` | `site_code` | String | `M` | 站点代码 |
|  | `订单发货状态` | `shipping_status` | String | `已发货` | 订单状态筛选 |
| **时间相关** |
|  | `发货时间` | `ship_date` | DateTime | `2026/2/12 4:28` | **主要筛选依据** |
|  | `承诺最晚发货时间` | `promise_ship_date` | Date | `2026/1/29` | 时效计算 |
|  | `承诺最晚收货时间` | `promise_delivery_date` | Date | `2026/2/10` | 时效计算 |
|  | `妥投时间` | `delivery_date` | DateTime | `2026/2/13 15:02` | 妥投时效计算 |
| **产品信息** |
|  | `一级产品` | `product_l1` | String | `Standard` | 产品筛选 L1 |
|  | `二级产品` | `product_l2` | String | `JC` | 产品筛选 L2 |
|  | `三级产品` | `product_l3` | String | `JC-USPS` | 产品筛选 L3 |
|  | `商品数量` | `item_count` | Number | `3` | 件数/包裹计算 |
| **物流信息** |
|  | `客户选择的运送方式` | `customer_shipping_method` | String | `中` | 客户选择 |
|  | `物流方式` | `actual_shipping_method` | String | `Standard Shipping` | 实际发货 |
|  | `实际/预估重量` | `weight_kg` | Number | `0.855` | 单价/KG 计算 |
| **仓库信息** |
|  | `发货地` | `warehouse_code` | String | `美国仓` | 仓库筛选 |
|  | `收货地` | `country_code` | String | `美国` | 国家筛选 |
| **金额相关** |
|  | `订单收入` | `revenue` | Number | `107.89` | 物流费占比计算 |
|  | `其他收入` | `other_revenue` | Number | `0` | - |
|  | `运费` | `freight` | Number | `0` | 运费补偿率计算 |
|  | `保价费` | `insurance_fee` | Number | `0` | 保价订单统计 |
|  | `运保费收入` | `freight_insurance_revenue` | Number | `0` | = 运费 + 保价费 |
|  | `实际运费` | `actual_freight` | Number | `41.47` | - |
|  | `物流运费 (实际运费/预估运费)` | `logistics_cost` | Number | `41.47` | **核心 KPI 计算** |
|  | `合单前物流运费` | `pre_merge_logistics_cost` | Number | `` | - |
| **分单相关** |
|  | `是否分单` | `is_split` | Boolean | `否` | 分单统计 |
|  | `分单原因` | `split_reason` | String | `` | - |
|  | `手动分单原因` | `manual_split_reason` | String | `` | - |
| **订单属性** |
|  | `预售订单` | `is_presale` | Boolean | `否` | - |
|  | `红人订单` | `is_influencer` | Boolean | `否` | - |
|  | `发货合单` | `is_merged` | Boolean | `否` | - |
|  | `预售合单` | `is_presale_merged` | Boolean | `否` | - |
|  | `售后` | `after_sales` | String | `` | - |

---

## 📊 核心 KPI 计算公式

### 顶部 6 个 KPI 卡片

| KPI | 公式 | 数据源字段 |
|-----|------|-----------|
| 单价/KG | `SUM(logistics_cost) / SUM(weight_kg)` | 物流运费、实际/预估重量 |
| 单价/包裹 | `SUM(logistics_cost) / COUNT(DISTINCT ship_no)` | 物流运费、发货单号 |
| 件数/包裹 | `SUM(item_count) / COUNT(DISTINCT ship_no)` | 商品数量、发货单号 |
| KG/包裹 | `SUM(weight_kg) / COUNT(DISTINCT ship_no)` | 实际/预估重量、发货单号 |
| 物流费占收入比 | `SUM(logistics_cost) / SUM(revenue) × 100%` | 物流运费、订单收入 |
| 累计物流费 | `SUM(logistics_cost)` | 物流运费 |

### 运费 BI KPI（5 个）

| KPI | 公式 | 数据源字段 |
|-----|------|-----------|
| 保价费收入 | `SUM(freight) + SUM(insurance_fee)` | 运费、保价费 |
| 保价订单占比 | `COUNT(insurance_fee > 0) / COUNT(order_no) × 100%` | 保价费、订单号 |
| 运费补偿率 | `SUM(freight) / SUM(logistics_cost) × 100%` | 运费、物流运费 |
| 分单数 | `COUNT(is_split = '是')` | 是否分单 |
| 分单占比 | `COUNT(is_split = '是') / COUNT(order_no) × 100%` | 是否分单、订单号 |

---

## 🔍 筛选条件字段

| 筛选器 | 中文字段 | 英文字段 | 示例值 |
|--------|---------|---------|--------|
| 国家筛选 | `收货地` | `country_code` | 美国、英国、加拿大、澳大利亚 |
| 仓库筛选 | `发货地` | `warehouse_code` | 美国仓、嘉兴仓、英国仓 |
| 产品 L1 | `一级产品` | `product_l1` | Standard、Expedited |
| 产品 L2 | `二级产品` | `product_l2` | JC、JS |
| 产品 L3 | `三级产品` | `product_l3` | JC-USPS、JS clothing line |
| 订单类型 | `订单发货状态` | `shipping_status` | 已发货、未发货 |
| 时间筛选 | `发货时间` | `ship_date` | 2026/2/12 4:28 → 2026-02-12 |

---

## ⚠️ 关键字段说明

### 1. 物流运费字段
- **中文字段名**: `物流运费 (实际运费/预估运费)`
- **注意**: 括号前**无空格**
- **用途**: 所有物流成本相关 KPI 的计算基础

### 2. 运费 vs 实际运费
- **`运费`**: 客户支付的运费（S 列）
- **`实际运费`**: 实际产生的运费（V 列）
- **`物流运费 (实际运费/预估运费)`**: 用于 KPI 计算（W 列）

### 3. 时间字段格式
- **原始格式**: `2026/2/12 4:28`
- **转换后**: `2026-02-12`
- **用途**: 时间筛选、趋势图 X 轴

### 4. 布尔字段
- **值**: `是` / `否`
- **字段**: `是否分单`、`预售订单`、`红人订单`、`发货合单`

---

## ✅ 数据验证规则

1. **必填字段**: 订单号、发货单号、发货时间、物流运费
2. **数值字段**: 不能为负数（除了 promise_days）
3. **日期格式**: 必须能转换为有效日期
4. **分单逻辑**: `is_split = '是'` 时，该订单号下应该有多个发货单号

---

## 📝 代码实现注意事项

### 1. 字段名必须完全匹配
```javascript
// ❌ 错误：有空格
d['物流运费 (实际运费/预估运费)']

// ✅ 正确：无空格
d['物流运费 (实际运费/预估运费)']
```

### 2. 数值字段需要转换
```javascript
// 所有金额和数量字段都需要 parseFloat 或 parseInt
logistics_cost: parseFloat(d['物流运费 (实际运费/预估运费)']) || 0
item_count: parseInt(d['商品数量']) || 1
```

### 3. 日期字段需要格式化
```javascript
// 发货时间：2026/2/12 4:28 → 2026-02-12
ship_date: d['发货时间'] ? d['发货时间'].split(' ')[0].replace(/\//g, '-') : ''
```

### 4. 筛选数据使用 filterData()
```javascript
// ✅ 正确：所有图表都应该使用筛选后的数据
const chartData = filterData();

// ❌ 错误：不要直接使用 rawData（除非确实需要全量数据）
rawData.forEach(...)
```

---

*文档版本：v3.17.7*
*创建时间：2026-04-01*
*数据源：3.16 测试 - Sheet1.csv (1087 条)*
