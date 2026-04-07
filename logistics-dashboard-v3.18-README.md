# 物流仪表板 v3.18 - 数据导入说明

## v3.18 变更说明

### ✅ 保留的功能
- 汇率计算（自动根据发货日期应用对应月份的汇率）
- LocalStorage 数据持久化（刷新页面数据不丢失）
- 所有图表和 KPI 指标

### ❌ 删除的功能
- 文件上传功能（CSV/Excel 上传界面）
- 手动保存/清除数据按钮

### 📦 数据格式
v3.18 起，数据直接保存在浏览器 LocalStorage 中，格式为**已映射的标准化数据**。

## 如何导入数据

### 方法 1：直接修改 LocalStorage（推荐）
1. 打开浏览器开发者工具（F12）
2. 进入 Console 标签
3. 执行以下代码导入数据：

```javascript
// 导入数据（替换为你的实际数据）
const yourData = [
  {
    "order_no": "MM2602280030525207",
    "ship_no": "MM2602280030525207b1",
    "site_code": "M",
    "warehouse_code": "英国仓",
    "country_code": "英国",
    "ship_date": "2026/3/3",
    "revenue": 33.98,
    "freight": 0,
    "logistics_cost": 17.58,
    // ... 其他字段
  }
  // ... 更多数据
];

// 保存到 LocalStorage
localStorage.setItem('logistics_rawData', JSON.stringify(yourData));

// 设置汇率（可选）
const rates = {
  "2026-01": 7.15,
  "2026-02": 7.20,
  "2026-03": 6.9236
};
localStorage.setItem('logistics_exchangeRates', JSON.stringify(rates));

// 刷新页面
location.reload();
```

### 方法 2：使用浏览器的 Storage 编辑器
1. 打开开发者工具（F12）
2. 进入 Application → Local Storage → 你的域名
3. 手动添加/编辑 `logistics_rawData` 和 `logistics_exchangeRates`

## 数据字段说明

### 必填字段
- `order_no`: 订单号
- `ship_no`: 发货单号
- `warehouse_code`: 仓库代码（如"英国仓"、"美国仓"、"嘉兴仓_IDP"）
- `country_code`: 国家（如"英国"、"美国"）
- `ship_date`: 发货日期（格式：YYYY/M/D）
- `revenue`: 订单收入（原始值，会自动乘以汇率）
- `logistics_cost`: 物流运费（原始值，会自动乘以汇率）

### 可选字段
- `freight`: 向客户收取的运费
- `insurance_fee`: 保价费
- `weight_kg`: 重量
- `is_split`: 是否分单（是/否）
- `product_l1/2/3`: 产品分级
- 等等...

## 清除数据
在浏览器 Console 执行：
```javascript
localStorage.removeItem('logistics_rawData');
localStorage.removeItem('logistics_exchangeRates');
location.reload();
```

## 注意事项
1. LocalStorage 容量限制约 5-10MB，数据量过大可能导致保存失败
2. 数据仅保存在当前浏览器，更换设备需要重新导入
3. 建议定期备份重要数据
