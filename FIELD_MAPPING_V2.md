# 物流分析仪表板 v3.17.9 - 字段映射（基于 CSV 实际字段名）

## 📋 数据源字段名（来自 CSV）

### 金额相关字段
| 中文字段名 | 字节长度 | 示例值 | 用途 |
|-----------|---------|--------|------|
| `物流运费 (实际运费/预估运费)` | 15 | `36.55` | **核心 KPI 计算** |
| `运费` | 2 | `8.99` | 运费补偿率分子 |
| `保价费` | 3 | `2.67` | 保价订单统计 |
| `实际运费` | 4 | `36.55` | - |
| `订单收入` | 4 | `41.98` | 物流费占比分母 |

### 筛选相关字段
| 中文字段名 | 示例值 | 用途 |
|-----------|--------|------|
| `收货地` | `美国` | 国家筛选 |
| `发货地` | `嘉兴仓_IDP` | 仓库筛选 |
| `一级产品` | `Standard` | 产品 L1 筛选 |
| `二级产品` | `JS` | 产品 L2 筛选 |
| `三级产品` | `JS clothing line` | 产品 L3 筛选 |
| `订单发货状态` | `已发货` | 订单类型筛选 |

### 时间字段
| 中文字段名 | 格式 | 示例值 | 用途 |
|-----------|------|--------|------|
| `发货时间` | `2026/2/12 4:28` | `2026/2/3 14:25` | **时间筛选依据** |

### 其他关键字段
| 中文字段名 | 示例值 | 用途 |
|-----------|--------|------|
| `订单号` | `B2` | 订单唯一标识 |
| `发货单号` | `A2` | 包裹唯一标识 |
| `是否分单` | `否` | 分单统计 |
| `商品数量` | `1` | 件数计算 |
| `实际/预估重量` | `0.247` | 单价/KG 计算 |

---

## ✅ 正确的代码实现

### 1. 数据加载
```javascript
rawData = data.map(d => ({
    ...d,  // 保留所有原始中文字段
    
    // 英文字段映射（用于 KPI 计算）
    logistics_cost: parseFloat(d['物流运费 (实际运费/预估运费)']) || 0,
    freight: parseFloat(d['运费']) || 0,
    insurance_fee: parseFloat(d['保价费']) || 0,
    revenue: parseFloat(d['订单收入']) || 0,
    weight_kg: parseFloat(d['实际/预估重量']) || 0,
    item_count: parseInt(d['商品数量']) || 0,
    is_split: d['是否分单'],
    ship_date: d['发货时间'] ? d['发货时间'].split(' ')[0].replace(/\//g, '-') : '',
}));
```

### 2. 筛选逻辑
```javascript
function filterData() {
    return rawData.filter(d => {
        // 国家筛选
        if (country !== 'all' && d['收货地'] !== country) return false;
        
        // 仓库筛选
        if (warehouse !== 'all') {
            const wh = (d['发货地'] || '').toLowerCase();
            // ... 仓库逻辑
        }
        
        // 产品筛选
        if (productL1 !== 'all' && d['一级产品'] !== productL1) return false;
        if (productL2 !== 'all' && d['二级产品'] !== productL2) return false;
        if (productL3 !== 'all' && d['三级产品'] !== productL3) return false;
        
        // 订单类型筛选
        if (orderType !== 'all' && d['订单发货状态'] !== orderType) return false;
        
        // 时间筛选
        const shipDate = new Date(d.ship_date);
        if (shipDate < startDate || shipDate > endDate) return false;
        
        return true;
    });
}
```

### 3. KPI 计算
```javascript
// 累计物流费
const totalCost = filteredData.reduce((sum, d) => sum + (d.logistics_cost || 0), 0);

// 单价/KG
const totalWeight = filteredData.reduce((sum, d) => sum + (d.weight_kg || 0), 0);
const priceKg = totalWeight > 0 ? totalCost / totalWeight : 0;

// 运费补偿率
const totalFreight = filteredData.reduce((sum, d) => sum + (d.freight || 0), 0);
const compensationRate = totalCost > 0 ? (totalFreight / totalCost * 100) : 0;
```

---

## ⚠️ 常见错误

### ❌ 错误：字段名有空格
```javascript
d['物流运费 (实际运费/预估运费)']  // 16 字符，有空格
```

### ✅ 正确：字段名无空格
```javascript
d['物流运费 (实际运费/预估运费)']  // 15 字符，无空格
```

### ❌ 错误：使用英文字段名
```javascript
d.country_code  // 不存在
d.warehouse_code  // 不存在
```

### ✅ 正确：使用中文字段名
```javascript
d['收货地']  // 存在
d['发货地']  // 存在
```

---

*文档版本：v3.17.9*
*数据源：3.16 测试 - Sheet1.csv*
*创建时间：2026-04-01*
