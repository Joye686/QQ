# 字段映射表 v3.17.11

## 用户底稿中文字段 → 代码英文字段映射

| 中文字段 | 英文字段 | 说明 |
|---------|---------|------|
| 订单号 | order_no | |
| 发货单号 | ship_no | |
| 站点 | site_code | M 等 |
| 客户选择的运送方式 | customer_shipping_method | 快/中/慢 |
| 物流方式 | product_l3 | 物流产品线 |
| 实际物流方式 | actual_shipping_method | Standard Shipping 等 |
| 物流单号 | ship_no | 复用发货单号 |
| 发货地 | warehouse_code | 嘉兴仓_IDP/美国仓等 |
| 收货地 | country_code | 美国/英国等（中文） |
| 州郡 | state | 可选 |
| 邮编 | zip_code | 可选 |
| 商品数量 | item_count | |
| 订单发货状态 | shipping_status | 已发货/部分发货/未发货 |
| 承诺最晚发货时间 | promise_ship_date | |
| 发货时间 | ship_date | |
| 承诺最晚收货时间 | promise_delivery_date | |
| 妥投时间 | delivery_date | |
| 妥投时效 | actual_days | |
| 商品成本 | product_cost | 可选 |
| 实际/预估重量 | weight_kg | |
| 订单收入 | revenue | |
| 其他收入 | other_revenue | |
| 运费 | freight | 向客户收取的运费 |
| 保价费 | insurance_fee | |
| 运保费收入 | freight_insurance_revenue | freight + insurance_fee |
| 实际运费 | actual_freight | 实际支付的运费 |
| 物流运费 (实际运费/预估运费) | logistics_cost | 用于计算成本 |
| 是否分单 | is_split | 是/否 |
| 分单原因 | split_reason | |
| 手动分单原因 | manual_split_reason | |
| 预售订单 | is_presale | 是/否 |
| 红人订单 | is_influencer | 是/否 |
| 发货合单 | is_merged | 是/否 |
| 预售合单 | is_presale_merged | 是/否 |
| 合单前物流运费 | pre_merge_logistics_cost | |
| 售后 | after_sales | |

## 核心修改

### 1. 数据加载时统一字段名
```javascript
// 支持中文和英文字段名，自动映射
function normalizeData(row) {
    return {
        order_no: row['订单号'] || row['order_no'],
        ship_no: row['发货单号'] || row['ship_no'],
        site_code: row['站点'] || row['site_code'],
        customer_shipping_method: row['客户选择的运送方式'] || row['customer_shipping_method'],
        product_l3: row['物流方式'] || row['product_l3'],
        actual_shipping_method: row['实际物流方式'] || row['actual_shipping_method'],
        warehouse_code: row['发货地'] || row['warehouse_code'],
        country_code: row['收货地'] || row['country_code'],
        item_count: parseFloat(row['商品数量'] || row['item_count'] || 0),
        shipping_status: row['订单发货状态'] || row['shipping_status'],
        promise_ship_date: row['承诺最晚发货时间'] || row['promise_ship_date'],
        ship_date: row['发货时间'] || row['ship_date'],
        promise_delivery_date: row['承诺最晚收货时间'] || row['promise_delivery_date'],
        delivery_date: row['妥投时间'] || row['delivery_date'],
        actual_days: parseFloat(row['妥投时效'] || row['actual_days'] || 0),
        weight_kg: parseFloat(row['实际/预估重量'] || row['weight_kg'] || 0),
        revenue: parseFloat(row['订单收入'] || row['revenue'] || 0),
        other_revenue: parseFloat(row['其他收入'] || row['other_revenue'] || 0),
        freight: parseFloat(row['运费'] || row['freight'] || 0),
        insurance_fee: parseFloat(row['保价费'] || row['insurance_fee'] || 0),
        freight_insurance_revenue: parseFloat(row['运保费收入'] || row['freight_insurance_revenue'] || 0),
        actual_freight: parseFloat(row['实际运费'] || row['actual_freight'] || 0),
        logistics_cost: parseFloat(row['物流运费 (实际运费/预估运费)'] || row['logistics_cost'] || 0),
        is_split: row['是否分单'] || row['is_split'],
        split_reason: row['分单原因'] || row['split_reason'],
        manual_split_reason: row['手动分单原因'] || row['manual_split_reason'],
        is_presale: row['预售订单'] || row['is_presale'],
        is_influencer: row['红人订单'] || row['is_influencer'],
        is_merged: row['发货合单'] || row['is_merged'],
        is_presale_merged: row['预售合单'] || row['is_presale_merged'],
        pre_merge_logistics_cost: parseFloat(row['合单前物流运费'] || row['pre_merge_logistics_cost'] || 0),
        after_sales: row['售后'] || row['after_sales']
    };
}
```

### 2. 国家代码保持中文
不再将"美国"转为"US"，直接用"美国"作为 country_code

### 3. 仓库代码保持中文
直接用"嘉兴仓_IDP"、"美国仓"等中文名称

## 修改清单

- [x] 数据加载函数支持中文字段
- [x] 筛选器使用中文字段值
- [x] 图表渲染使用中文字段
- [x] 移除英文代码映射逻辑
- [x] 更新所有字段引用
