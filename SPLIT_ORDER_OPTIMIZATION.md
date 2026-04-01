# 分单逻辑优化建议

## 📋 当前实现 vs 用户建议

### 当前实现（v3.17.7）
```javascript
// 使用 is_split 字段
const splitOrders = filteredData.filter(o => 
  o.is_split === '是' || o.is_split === 'Y' || o.is_split === true
).length
```

**问题：**
- 依赖 `is_split` 字段，可能存在数据不准确
- 无法验证实际分单情况

---

## ✅ 优化方案

### 方案 1：包裹数差值法（推荐）
**逻辑：** 分单数 = 总包裹数 - 去重订单数

```javascript
function calculateSplitOrders(filteredData) {
  const totalPackages = filteredData.length  // 总行数=总包裹数
  const uniqueOrders = new Set(filteredData.map(d => d.order_no)).size
  const splitPackages = totalPackages - uniqueOrders  // 分单的包裹数
  
  // 分单的订单数（包裹数>1 的订单）
  const orderPackageCount = {}
  filteredData.forEach(d => {
    orderPackageCount[d.order_no] = (orderPackageCount[d.order_no] || 0) + 1
  })
  const splitOrderCount = Object.values(orderPackageCount).filter(count => count > 1).length
  
  return {
    totalPackages,      // 总包裹数
    uniqueOrders,       // 去重订单数
    splitPackages,      // 分单包裹数
    splitOrderCount,    // 分单订单数
    totalOrders: Object.keys(orderPackageCount).length  // 总订单数
  }
}
```

**优点：**
- 不依赖 `is_split` 字段
- 直接计算，逻辑清晰
- 可同时获得分单包裹数和分单订单数

---

### 方案 2：包裹号后缀判定法
**逻辑：** 包裹号末尾 `b1`=第一个包裹，`b2`=第二个包裹...

```javascript
function calculateSplitOrdersByShipNo(filteredData) {
  // 统计每个订单的包裹号
  const orderShips = {}
  filteredData.forEach(d => {
    if (!orderShips[d.order_no]) orderShips[d.order_no] = []
    if (d.ship_no) orderShips[d.order_no].push(d.ship_no)
  })
  
  // 判断是否分单：存在 b2,b3...后缀
  let splitOrderCount = 0
  let splitPackages = 0
  
  Object.values(orderShips).forEach(ships => {
    if (ships.length > 1) {
      splitOrderCount++
      splitPackages += ships.length - 1  // 减去第一个包裹
    }
  })
  
  return { splitOrderCount, splitPackages }
}
```

**优点：**
- 利用包裹号规则，更直观
- 可以识别具体哪些订单分单了

**前提：**
- 包裹号必须遵循 `XXXb1`, `XXXb2` 格式
- 需要验证数据中包裹号的规范性

---

### 方案 3：混合法（最可靠）
```javascript
function calculateSplitOrders(filteredData) {
  // 方法 1：包裹数差值
  const totalPackages = filteredData.length
  const uniqueOrders = new Set(filteredData.map(d => d.order_no)).size
  const splitPackagesByDiff = totalPackages - uniqueOrders
  
  // 方法 2：包裹号判定
  const orderShips = {}
  filteredData.forEach(d => {
    if (!orderShips[d.order_no]) orderShips[d.order_no] = []
    if (d.ship_no) orderShips[d.order_no].push(d.ship_no)
  })
  
  let splitOrderCount = 0
  let splitPackagesByShipNo = 0
  
  Object.values(orderShips).forEach(ships => {
    if (ships.length > 1) {
      splitOrderCount++
      splitPackagesByShipNo += ships.length - 1
    }
  })
  
  // 交叉验证
  if (splitPackagesByDiff !== splitPackagesByShipNo) {
    console.warn('分单数计算不一致:', {
      byDiff: splitPackagesByDiff,
      byShipNo: splitPackagesByShipNo
    })
  }
  
  return {
    splitPackages: splitPackagesByDiff,  // 优先使用差值法
    splitOrderCount,
    validated: splitPackagesByDiff === splitPackagesByShipNo
  }
}
```

**优点：**
- 双重验证，确保准确性
- 不一致时告警，便于发现数据问题

---

## 📊 更新后的 KPI 计算逻辑

### 分单数
```javascript
// 订单下单时间落在筛选期的总包裹数 - 订单下单时间落在筛选期的去重订单数
const totalPackages = filteredData.length
const uniqueOrders = new Set(filteredData.map(d => d.order_no)).size
const splitOrders = totalPackages - uniqueOrders
```

### 分单占比
```javascript
// 分单的订单数 = 该订单号下包裹数大于 1 的订单数
const orderPackageCount = {}
filteredData.forEach(d => {
  orderPackageCount[d.order_no] = (orderPackageCount[d.order_no] || 0) + 1
})

const splitOrderCount = Object.values(orderPackageCount).filter(count => count > 1).length
const totalOrders = Object.keys(orderPackageCount).length
const splitRatio = (splitOrderCount / totalOrders) * 100
```

---

## 🔍 包裹号判定规则验证

### 示例数据
```
order_no | ship_no    | 判定
---------|------------|------
A001     | SHIP001b1  | 第 1 个包裹
A001     | SHIP001b2  | 第 2 个包裹 → 分单
A002     | SHIP002b1  | 第 1 个包裹
A003     | SHIP003b1  | 第 1 个包裹
A003     | SHIP003b2  | 第 2 个包裹 → 分单
A003     | SHIP003b3  | 第 3 个包裹 → 分单
```

### 正则表达式
```javascript
// 匹配 b2, b3, b4...（第二个及以后的包裹）
const isSplitPackage = /b[2-9]$/.test(ship_no)

// 匹配 b1（第一个包裹）
const isFirstPackage = /b1$/.test(ship_no)

// 提取包裹序号
const packageIndex = ship_no.match(/b(\d+)$/)?.[1]
```

---

## ✅ 推荐实施方案

1. **立即实施：** 使用方案 1（包裹数差值法）替换当前的 `is_split` 逻辑
2. **验证数据：** 用方案 2（包裹号判定）验证数据质量
3. **长期优化：** 如果包裹号规则稳定，可采用方案 3（混合法）

---

## 📝 待确认问题

1. **包裹号格式是否统一？**
   - 是否所有包裹都遵循 `XXXb1`, `XXXb2` 格式？
   - 是否有其他格式（如 `-1`, `_1` 等）？

2. **筛选期判定依据？**
   - 分单数统计按 `order_date`（下单时间）还是 `ship_date`（发货时间）？
   - 当前代码使用 `ship_date`，需确认是否正确

3. **历史数据兼容性？**
   - 旧数据是否有 `is_split` 字段缺失的情况？
   - 是否需要向后兼容？

---

*创建时间：2026-04-01*
*版本：v3.17.7 优化建议*
