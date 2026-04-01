# 物流分析仪表板 v3.17.7 - 数据计算逻辑说明

## 📊 顶部 KPI 指标卡（6 个）

### 1. 单价/KG
- **公式：** `物流运费合计 / 总重量 KG`
- **数据源：** `filteredData`（当前筛选条件下的数据）
- **计算：** `totalCost / totalWeight`
- **显示：** `$XX.XX`（保留 2 位小数）

### 2. 单价/包裹
- **公式：** `物流运费合计 / 发货包裹数`
- **数据源：** `filteredData`
- **计算：** `totalCost / totalPackages`
- **显示：** `$XX.XX`（保留 2 位小数）

### 3. 件数/包裹
- **公式：** `总商品件数 / 发货包裹数`
- **数据源：** `filteredData`
- **计算：** `totalItems / totalPackages`
- **显示：** `XX.X`（保留 1 位小数）

### 4. KG/包裹
- **公式：** `总重量 KG / 发货包裹数`
- **数据源：** `filteredData`
- **计算：** `totalWeight / totalPackages`
- **显示：** `X.XXX kg`（保留 3 位小数）

### 5. 物流费占收入比
- **公式：** `(物流运费合计 / 订单收入合计) × 100%`
- **数据源：** `filteredData`
- **计算：** `(totalCost / totalRevenue) × 100`
- **显示：** `XX.X%`（保留 1 位小数）

### 6. 累计物流费
- **公式：** `SUM(物流运费)`
- **数据源：** `filteredData`
- **计算：** `filteredData.reduce((sum, d) => sum + d.logistics_cost, 0)`
- **显示：** `$XXX,XXX`（千分位，2 位小数）

---

## 📈 运费 BI KPI 指标（5 个）

### 1. 保价费收入
- **公式：** `SUM(运保费)`
- **数据源：** `filteredData`
- **计算：** `filteredData.reduce((sum, o) => sum + o.insurance_fee, 0)`
- **显示：** `$XXX,XXX`（取整）

### 2. 保价订单占比
- **公式：** `(购买保价的订单数 / 总订单数) × 100%`
- **数据源：** `filteredData`
- **计算：** `insuranceOrders / filteredData.length × 100`
- **条件：** `has_insurance === 'Y' || has_insurance === 'y' || has_insurance === true`
- **显示：** `XX.X%`（保留 1 位小数）

### 3. 补偿率
- **公式：** `(运保费收入 / 物流运费) × 100%`
- **数据源：** `filteredData`
- **计算：** `(totalInsurance / totalLogistics) × 100`
- **显示：** `XX.X%`（保留 1 位小数）

### 4. 分单数
- **公式：** `总包裹数 - 去重订单数`
- **数据源：** `filteredData`
- **计算：** 
  ```javascript
  const totalPackages = filteredData.length  // 总包裹数（每行一个包裹）
  const uniqueOrders = new Set(filteredData.map(d => d.order_no)).size  // 去重订单数
  const splitOrders = totalPackages - uniqueOrders  // 分单数
  ```
- **备选逻辑（包裹号判定）：**
  ```javascript
  // 包裹号末尾 b1=第一个包裹，b2=第二个包裹...
  // 如果存在 ship_no 以 b2,b3...结尾的订单，即为分单
  const splitOrders = filteredData.filter(d => 
    d.ship_no && /b[2-9]$/.test(d.ship_no)  // 匹配 b2,b3,b4...结尾的包裹号
  ).length
  ```
- **显示：** `XXX,XXX`（千分位）

### 5. 分单占比
- **公式：** `(分单的订单数 / 总订单数) × 100%`
- **数据源：** `filteredData`
- **计算：** 
  ```javascript
  // 分单的订单数 = 该订单号下包裹数大于 1 的订单数
  const orderPackageCount = {}
  filteredData.forEach(d => {
    orderPackageCount[d.order_no] = (orderPackageCount[d.order_no] || 0) + 1
  })
  const splitOrderCount = Object.values(orderPackageCount).filter(count => count > 1).length
  const totalOrders = Object.keys(orderPackageCount).length
  const splitRatio = (splitOrderCount / totalOrders) × 100
  ```
- **显示：** `XX.X%`（保留 1 位小数）

---

## 📊 第一行图表（4 个）

### 1. 🌍 各国订单数及占比（饼图）
**数据源：** `rawData`（全量数据，不受筛选影响）

**计算逻辑：**
```javascript
// 按国家分组统计
countryData[country] = { revenue: 0, orders: 0 }
countryData[country].revenue += d.revenue
countryData[country].orders++

// 取前 10 个国家
countries = Object.keys(countryData).slice(0, 10)

// 饼图显示：订单数和占比
value: countryData[c].orders
tooltip: '{b}: {c}单 ({d}%)'
```

**显示：** 每个国家的订单数和百分比

---

### 2. 💰 各国客单价（柱状图）
**数据源：** `rawData`（全量数据）

**计算逻辑：**
```javascript
// 客单价 = 收入 / 订单数
aovData = countries.map(c => 
  countryData[c].orders > 0 ? 
  (countryData[c].revenue / countryData[c].orders).toFixed(0) : 0
)
```

**显示：** `$XXX`（取整）

---

### 3. 📊 订单结构 - 订单口径（条形图）
**数据源：** `filteredData`（受筛选影响）

**分类逻辑：**
- **全部发货：** `package_count === 1` 或 `shipping_status === '已发货'`
- **部分发货：** `package_count > 1` 且存在未发货
- **未发货：** `shipping_status !== '已发货'`

**显示：** 各状态的订单数和占比

---

### 4. 🏭 发货仓库占比 - 发货口径（条形图）
**数据源：** `filteredData`（受筛选影响）

**分类逻辑：**
```javascript
// 嘉兴仓
wh.includes('jiaxing') || wh.includes('嘉兴')

// 海外仓
wh.includes('us') || wh.includes('ca') || wh.includes('uk') ||
wh.includes('america') || wh.includes('canada') || wh.includes('britain') ||
wh.includes('overseas') || wh.includes('海外')
```

**显示：** 各仓库的发货单数和占比

---

## 📊 第二行图表（4 个）

### 1. 📊 各运费区间订单占比（环形图）
**数据源：** `rawData` 中筛选 `country_code IN ['US', 'GB', 'CA', 'AU']`

**区间划分：**
- `$0-30`: `0 <= logistics_cost < 30`
- `$30-60`: `30 <= logistics_cost < 60`
- `$60-100`: `60 <= logistics_cost < 100`
- `$100-200`: `100 <= logistics_cost < 200`
- `$200+`: `logistics_cost >= 200`

**计算逻辑：**
```javascript
rangeData[i].count++  // 统计各区间订单数
// 环形图显示订单数和占比
```

---

### 2. 💰 各运费区间客单价（柱状图，支持币种切换）
**数据源：** 同区间占比图表

**计算逻辑：**
```javascript
// 各区间收入合计
rangeData[i].revenue += d.revenue

// 客单价 = 区间收入 / 区间订单数
r.aov = r.count > 0 ? r.revenue / r.count : 0
```

**币种切换：** 目前仅显示本国币种（USD），币种筛选功能已预留但未实现

**显示：** `$XXX`（取整）

---

### 3. 📦 分单次数分布（柱状图）
**数据源：** `rawData`（全量数据）

**分类逻辑：**
```javascript
isSplit = d.is_split === '是' || d.is_split === 'Y' || d.is_split === true
splitData[0] = 未分单数量
splitData[1] = 已分单数量
```

**显示：** 未分单和已分单的订单数

---

### 4. 📈 分单占比趋势（折线图）
**数据源：** `rawData`（全量数据）

**计算逻辑：**
```javascript
// 按发货日期分组
dateMap[date] = { total: 0, split: 0 }
dateMap[date].total++
if (isSplit) dateMap[date].split++

// 取最近 14 天
sortedDates = Object.keys(dateMap).sort().slice(-14)

// 计算每日分单占比
trendData = sortedDates.map(date => 
  (dateMap[date].split / dateMap[date].total * 100).toFixed(1)
)
```

**显示：** 最近 14 天每天的分单占比趋势（%）

---

## 🔍 数据筛选逻辑

### filterData() 函数
所有标记为 `filteredData` 的指标都受以下筛选条件影响：

1. **国家筛选** - `d.country_code`
2. **仓库筛选** - `d.warehouse_code`（支持智能识别海外仓）
3. **产品 L1 筛选** - `d.product_l1`
4. **产品 L2 筛选** - `d.product_l2`
5. **产品 L3 筛选** - `d.product_l3`
6. **订单类型筛选** - `d.order_type`
7. **发货时间筛选** - `d.ship_date` 在开始和结束日期之间

### rawData vs filteredData
- **rawData：** 全量数据，不受筛选器影响（用于各国数据、分单相关图表）
- **filteredData：** 当前筛选条件下的数据（用于 KPI 指标、订单结构、仓库占比）

---

## ⚠️ 特殊说明

### 1. 保价相关字段
- `has_insurance`: 是否购买保价（'Y'/'y'/true）
- `insurance_fee`: 运保费金额

### 2. 分单相关字段
- `is_split`: 是否分单（'是'/'Y'/true）
- `split_reason`: 分单原因（目前未使用）

### 3. 仓库智能识别
```javascript
// 海外仓识别
wh.includes('us') || wh.includes('ca') || wh.includes('uk') ||
wh.includes('america') || wh.includes('canada') || wh.includes('britain') ||
wh.includes('overseas') || wh.includes('海外')

// 嘉兴仓识别
wh.includes('jiaxing') || wh.includes('嘉兴')
```

### 4. 物流运费字段映射
```javascript
logistics_cost: d['物流运费 (实际运费/预估运费)'] || d.logistics_cost || 0
```
支持 Excel 列名和 JSON 列名两种格式

---

## 📋 数据来源字段清单

### 基础字段
- `order_no`: 订单号
- `ship_no`: 发货单号
- `ship_date`: 发货日期
- `country_code`: 国家代码
- `warehouse_code`: 仓库代码
- `package_count`: 包裹数
- `shipping_status`: 发货状态

### 金额字段
- `logistics_cost`: 物流运费
- `revenue`: 订单收入
- `insurance_fee`: 运保费
- `weight_kg`: 重量 KG
- `item_count`: 商品件数

### 产品字段
- `product_l1`: 产品一级分类
- `product_l2`: 产品二级分类
- `product_l3`: 产品三级分类

### 标记字段
- `has_insurance`: 是否保价
- `is_split`: 是否分单
- `order_type`: 订单类型

---

*文档版本：v3.17.7*
*最后更新：2026-04-01*
