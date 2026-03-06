// 仪表板数据处理脚本
const fs = require('fs');

// 读取模拟数据
const mockData = JSON.parse(fs.readFileSync('mock_data_1000.json', 'utf8'));

console.log('处理', mockData.length, '条订单数据...\n');

// 初始化数据结构
const processedData = {
  // 指标卡片
  metrics: {
    pricePerKg: 0,
    pricePerPkg: 0,
    totalPackages: 0,
    totalOrders: 0,
    itemsPerPkg: 0,
    weightPerPkg: 0,
    logisticsRatio: 0,
    totalLogisticsFee: 0
  },
  
  // T 字型图表数据（按国家 + 时间）
  tChartData: {
    countries: ['美国', '英国', '加拿大', '澳大利亚', '其他'],
    timeSeries: [],
    jiaxing: {},
    overseas: {}
  },
  
  // 订单结构（订单口径）
  orderStructure: [],
  
  // 发货仓库占比（发货口径）
  warehouseRatio: [],
  
  // 流向分析数据
  flowData: {
    customerChoice: { fast: 0, slow: 0 },
    actualShip: { fast: 0, slow: 0 },
    flows: [],
    metrics: { keepRate: 0, downgrade: 0, upgrade: 0 }
  },
  
  // Excel 明细表数据（按国家分类）
  productDataByCountry: {}
};

// 基础统计
let totalWeight = 0;
let totalItems = 0;
let totalRevenue = 0; // 假设收入为物流费的 10 倍

// 按仓库分类
const byWarehouse = {
  '嘉兴仓': [],
  '美国仓': [],
  '英国仓': [],
  '加拿大仓': []
};

// 按国家分类
const byCountry = {
  '美国': [],
  '英国': [],
  '加拿大': [],
  '澳大利亚': [],
  '其他': []
};

// 处理每条订单
mockData.forEach(order => {
  // 基础统计
  totalWeight += order.weight;
  totalItems += order.qty;
  totalRevenue += order.fee * 10;
  
  // 按仓库分类
  if (byWarehouse[order.origin]) {
    byWarehouse[order.origin].push(order);
  }
  
  // 按国家分类
  if (byCountry[order.dest]) {
    byCountry[order.dest].push(order);
  }
});

// 计算指标卡片
processedData.metrics.totalOrders = mockData.length;
processedData.metrics.totalPackages = mockData.length;
processedData.metrics.totalLogisticsFee = mockData.reduce((sum, o) => sum + o.fee, 0);
processedData.metrics.pricePerKg = processedData.metrics.totalLogisticsFee / totalWeight;
processedData.metrics.pricePerPkg = processedData.metrics.totalLogisticsFee / processedData.metrics.totalPackages;
processedData.metrics.itemsPerPkg = totalItems / processedData.metrics.totalPackages;
processedData.metrics.weightPerPkg = totalWeight / processedData.metrics.totalPackages;
processedData.metrics.logisticsRatio = processedData.metrics.totalLogisticsFee / totalRevenue * 100;

console.log('指标卡片:');
console.log('  单价/KG:', processedData.metrics.pricePerKg.toFixed(2));
console.log('  单价/包裹:', processedData.metrics.pricePerPkg.toFixed(2));
console.log('  发货包裹数:', processedData.metrics.totalPackages);
console.log('  订单数:', processedData.metrics.totalOrders);
console.log('  包单件:', processedData.metrics.itemsPerPkg.toFixed(1));
console.log('  每包裹重量:', processedData.metrics.weightPerPkg.toFixed(1), 'kg');
console.log('  正向物流占收入比:', processedData.metrics.logisticsRatio.toFixed(1) + '%');
console.log('  累计物流费:', processedData.metrics.totalLogisticsFee.toFixed(2));

// 订单结构（订单口径 - 按国家）
processedData.orderStructure = Object.entries(byCountry).map(([country, orders]) => {
  const total = orders.length;
  const full = orders.filter(o => o.status === '已发货').length;
  const partial = orders.filter(o => o.status === '部分发货').length;
  const unshipped = orders.filter(o => o.status === '未发货').length;
  
  return {
    country: country,
    full: total > 0 ? (full / total * 100) : 0,
    partial: total > 0 ? (partial / total * 100) : 0,
    unshipped: total > 0 ? (unshipped / total * 100) : 0,
    _numbers: { full, partial, unshipped, total }
  };
});

console.log('\n订单结构（订单口径）:');
processedData.orderStructure.forEach(item => {
  console.log(`  ${item.country}: 已发货${item.full.toFixed(1)}%, 部分${item.partial.toFixed(1)}%, 未发货${item.unshipped.toFixed(1)}%`);
});

// 发货仓库占比（发货口径 - 按国家）
processedData.warehouseRatio = Object.entries(byCountry).map(([country, orders]) => {
  const shippedOrders = orders.filter(o => o.status === '已发货' || o.status === '部分发货');
  const total = shippedOrders.length;
  const jiaxing = shippedOrders.filter(o => o.origin === '嘉兴仓').length;
  const overseas = shippedOrders.filter(o => ['美国仓', '英国仓', '加拿大仓'].includes(o.origin)).length;
  
  return {
    country: country,
    jiaxing: total > 0 ? (jiaxing / total * 100) : 0,
    overseas: total > 0 ? (overseas / total * 100) : 0,
    _numbers: { jiaxing, overseas, total }
  };
});

console.log('\n发货仓库占比（发货口径）:');
processedData.warehouseRatio.forEach(item => {
  console.log(`  ${item.country}: 嘉兴仓${item.jiaxing.toFixed(1)}%, 海外仓${item.overseas.toFixed(1)}%`);
});

// 流向分析
let fastKeep = 0, fastDowngrade = 0, slowKeep = 0, slowUpgrade = 0;

mockData.forEach(order => {
  // 客户选择
  if (order.customerChoice === '快') processedData.flowData.customerChoice.fast++;
  else processedData.flowData.customerChoice.slow++;
  
  // 实际发出
  if (order.actualShip === '快') processedData.flowData.actualShip.fast++;
  else processedData.flowData.actualShip.slow++;
  
  // 保持/降档/提档
  if (order.customerChoice === '快' && order.actualShip === '快') fastKeep++;
  else if (order.customerChoice === '快' && order.actualShip === '普通') fastDowngrade++;
  else if (order.customerChoice === '普通' && order.actualShip === '普通') slowKeep++;
  else if (order.customerChoice === '普通' && order.actualShip === '快') slowUpgrade++;
});

const totalFast = processedData.flowData.customerChoice.fast;
const totalSlow = processedData.flowData.customerChoice.slow;
processedData.flowData.metrics.keepRate = ((fastKeep + slowKeep) / mockData.length * 100).toFixed(1);
processedData.flowData.metrics.downgrade = (fastDowngrade / mockData.length * 100).toFixed(1);
processedData.flowData.metrics.upgrade = (slowUpgrade / mockData.length * 100).toFixed(1);

processedData.flowData.flows = [
  { from: 'fast', to: 'fast', value: (fastKeep / totalFast * 100).toFixed(1), type: 'keep' },
  { from: 'fast', to: 'slow', value: (fastDowngrade / totalFast * 100).toFixed(1), type: 'downgrade' },
  { from: 'slow', to: 'slow', value: (slowKeep / totalSlow * 100).toFixed(1), type: 'keep' },
  { from: 'slow', to: 'fast', value: (slowUpgrade / totalSlow * 100).toFixed(1), type: 'upgrade' }
];

console.log('\n流向分析:');
console.log('  客户选择 - 快线:', processedData.flowData.customerChoice.fast, `(${(processedData.flowData.customerChoice.fast/mockData.length*100).toFixed(1)}%)`);
console.log('  客户选择 - 慢线:', processedData.flowData.customerChoice.slow, `(${(processedData.flowData.customerChoice.slow/mockData.length*100).toFixed(1)}%)`);
console.log('  实际发出 - 快线:', processedData.flowData.actualShip.fast);
console.log('  实际发出 - 慢线:', processedData.flowData.actualShip.slow);
console.log('  保持率:', processedData.flowData.metrics.keepRate + '%');
console.log('  降档率:', processedData.flowData.metrics.downgrade + '%');
console.log('  提档率:', processedData.flowData.metrics.upgrade + '%');

// Excel 明细表数据（按国家）
processedData.productDataByCountry = {};

Object.entries(byCountry).forEach(([country, orders]) => {
  // 嘉兴仓数据
  const jiaxingOrders = orders.filter(o => o.origin === '嘉兴仓');
  const jiaxingData = jiaxingOrders.map(order => ({
    shipping: order.customerChoice,
    level1: order.level1,
    level2: order.level2,
    level3: order.level3,
    qty: order.qty,
    ratio: 0,  // 后面计算
    priceKg: order.fee / order.weight,
    promise: order.promiseTime,
    delivery: order.deliveryTime,
    rate: order.deliveryTime > 0 && order.promiseTime > 0 ? Math.min(100, (order.promiseTime / order.deliveryTime * 100)) : 100
  }));
  
  // 计算占比
  const totalJiaxingQty = jiaxingData.reduce((sum, d) => sum + d.qty, 0);
  jiaxingData.forEach(d => {
    d.ratio = totalJiaxingQty > 0 ? (d.qty / totalJiaxingQty * 100) : 0;
  });
  
  // 海外仓数据
  const overseasOrders = orders.filter(o => ['美国仓', '英国仓', '加拿大仓'].includes(o.origin));
  const overseasData = overseasOrders.map(order => ({
    shipping: order.actualShip,
    level1: order.level1,
    level2: order.level2,
    level3: order.level3,
    qty: order.qty,
    ratio: 0,
    priceKg: order.fee / order.weight,
    promise: order.promiseTime,
    delivery: order.deliveryTime,
    rate: order.deliveryTime > 0 && order.promiseTime > 0 ? Math.min(100, (order.promiseTime / order.deliveryTime * 100)) : 100
  }));
  
  const totalOverseasQty = overseasData.reduce((sum, d) => sum + d.qty, 0);
  overseasData.forEach(d => {
    d.ratio = totalOverseasQty > 0 ? (d.qty / totalOverseasQty * 100) : 0;
  });
  
  processedData.productDataByCountry[country] = {
    customerChoice: jiaxingData.slice(0, 20),  // 限制 20 条
    actualShip: overseasData.slice(0, 20)
  };
});

console.log('\nExcel 明细表（按国家）:');
Object.entries(processedData.productDataByCountry).forEach(([country, data]) => {
  console.log(`  ${country}: 嘉兴仓${data.customerChoice.length}条，海外仓${data.actualShip.length}条`);
});

// 保存处理后的数据
fs.writeFileSync('dashboard_data.json', JSON.stringify(processedData, null, 2));
console.log('\n✅ 处理完成！数据已保存到 dashboard_data.json');
