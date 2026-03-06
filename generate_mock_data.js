// 生成模拟测试数据
const fs = require('fs');

// 配置
const ORDER_COUNT = 1000;
const WAREHOUSES = ['嘉兴仓', '美国仓', '英国仓', '加拿大仓'];
const COUNTRIES = ['美国', '英国', '加拿大', '澳大利亚', '其他'];
const SHIPPING_METHODS = ['快', '普通'];
const SITES = ['M', 'W', 'R'];
const PRODUCTS = {
  level1: ['Standard Shipping', 'Express Shipping', 'Quickship'],
  level2: ['海贝拓', '极速', '六脉', '燕文', '云途', 'MP', 'JC-USPS', 'liumai L01'],
  level3: ['HABIT POST delivery', 'JS EXPRESS', 'JS clothing line', 'HABIT Commercial delivery', '']
};

// 随机数生成器
function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randomChoice(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function randomDate(start, end) {
  const date = new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
  return date.toISOString().split('T')[0].replace(/-/g, '');
}

function generateOrder(index) {
  // 仓库分布：嘉兴仓 70%, 美国仓 15%, 英国仓 10%, 加拿大仓 5%
  const warehouseRand = Math.random();
  let warehouse;
  if (warehouseRand < 0.70) warehouse = '嘉兴仓';
  else if (warehouseRand < 0.85) warehouse = '美国仓';
  else if (warehouseRand < 0.95) warehouse = '英国仓';
  else warehouse = '加拿大仓';
  
  // 国家分布（根据仓库）
  let country;
  if (warehouse === '嘉兴仓') {
    const countryRand = Math.random();
    if (countryRand < 0.50) country = '美国';
    else if (countryRand < 0.75) country = '英国';
    else if (countryRand < 0.88) country = '加拿大';
    else if (countryRand < 0.96) country = '澳大利亚';
    else country = '其他';
  } else {
    // 海外仓发往对应国家
    if (warehouse === '美国仓') country = '美国';
    else if (warehouse === '英国仓') country = '英国';
    else if (warehouse === '加拿大仓') country = '加拿大';
  }
  
  // 运送方式：80% 普通，20% 快
  const customerChoice = Math.random() < 0.80 ? '普通' : '快';
  
  // 实际发出（保持率 90%, 降档 4%, 提档 1%, 其他 5%）
  let actualShip;
  const shipRand = Math.random();
  if (customerChoice === '快') {
    if (shipRand < 0.90) actualShip = '快';  // 保持
    else if (shipRand < 0.94) actualShip = '普通';  // 降档
    else actualShip = '快';  // 保持
  } else {
    if (shipRand < 0.99) actualShip = '普通';  // 保持
    else actualShip = '快';  // 提档
  }
  
  // 订单状态
  const statusRand = Math.random();
  let status;
  if (statusRand < 0.85) status = '已发货';
  else if (statusRand < 0.95) status = '部分发货';
  else status = '未发货';
  
  // 时间
  const orderDate = new Date(2025, 11, 1 + randomInt(0, 30));
  const shipDate = new Date(orderDate);
  shipDate.setDate(shipDate.getDate() + randomInt(0, 3));
  
  // 产品
  const level1 = randomChoice(PRODUCTS.level1);
  const level2 = randomChoice(PRODUCTS.level2);
  const level3 = randomChoice(PRODUCTS.level3);
  
  // 数值
  const qty = randomInt(1, 10);
  const weight = (Math.random() * 2 + 0.1).toFixed(3);
  const fee = (Math.random() * 100 + 10).toFixed(2);
  const promiseTime = (Math.random() * 15 + 5).toFixed(2);
  const deliveryTime = status === '已发货' ? (Math.random() * 10 + 2).toFixed(1) : 0;
  
  // 是否超期
  const isLate = Math.random() < 0.05 ? '是' : '否';
  const isDeliveryLate = status === '已发货' ? (Math.random() < 0.08 ? '超期' : '未超期') : '未妥投';
  
  return {
    orderNo: `M${Date.now()}${index}`,
    shipNo: `M${Date.now()}${index}b1`,
    orderTime: orderDate.toISOString().split('T')[0].replace(/-/g, ''),
    site: randomChoice(SITES),
    customerChoice: customerChoice,
    actualShip: actualShip,
    level1: level1,
    level2: level2,
    level3: level3,
    origin: warehouse,
    dest: country,
    qty: qty,
    status: status,
    shipTime: shipDate.toISOString().split('T')[0],
    deliveryTime: parseFloat(deliveryTime),
    weight: parseFloat(weight),
    fee: parseFloat(fee),
    promiseTime: parseFloat(promiseTime),
    isLate: isLate,
    isDeliveryLate: isDeliveryLate
  };
}

// 生成数据
const mockData = [];
for (let i = 0; i < ORDER_COUNT; i++) {
  mockData.push(generateOrder(i));
}

// 统计
const stats = {
  total: mockData.length,
  byWarehouse: {},
  byCountry: {},
  byShipping: {},
  byStatus: {},
  keepRate: { fast: { keep: 0, downgrade: 0 }, slow: { keep: 0, upgrade: 0 } }
};

mockData.forEach(order => {
  // 仓库
  if (!stats.byWarehouse[order.origin]) stats.byWarehouse[order.origin] = 0;
  stats.byWarehouse[order.origin]++;
  
  // 国家
  if (!stats.byCountry[order.dest]) stats.byCountry[order.dest] = 0;
  stats.byCountry[order.dest]++;
  
  // 运送方式
  if (!stats.byShipping[order.customerChoice]) stats.byShipping[order.customerChoice] = 0;
  stats.byShipping[order.customerChoice]++;
  
  // 状态
  if (!stats.byStatus[order.status]) stats.byStatus[order.status] = 0;
  stats.byStatus[order.status]++;
  
  // 保持率/降档/提档
  if (order.customerChoice === '快') {
    if (order.actualShip === '快') stats.keepRate.fast.keep++;
    else stats.keepRate.fast.downgrade++;
  } else {
    if (order.actualShip === '普通') stats.keepRate.slow.keep++;
    else stats.keepRate.slow.upgrade++;
  }
});

// 计算保持率
const totalFast = stats.keepRate.fast.keep + stats.keepRate.fast.downgrade;
const totalSlow = stats.keepRate.slow.keep + stats.keepRate.slow.upgrade;
const keepRate = ((stats.keepRate.fast.keep + stats.keepRate.slow.keep) / mockData.length * 100).toFixed(1);
const downgradeRate = (stats.keepRate.fast.downgrade / mockData.length * 100).toFixed(1);
const upgradeRate = (stats.keepRate.slow.upgrade / mockData.length * 100).toFixed(1);

console.log('=== 模拟数据生成完成 ===');
console.log('总订单数:', stats.total);
console.log('\n按仓库:');
Object.entries(stats.byWarehouse).forEach(([k, v]) => console.log(`  ${k}: ${v} (${(v/stats.total*100).toFixed(1)}%)`));
console.log('\n按国家:');
Object.entries(stats.byCountry).forEach(([k, v]) => console.log(`  ${k}: ${v} (${(v/stats.total*100).toFixed(1)}%)`));
console.log('\n按运送方式:');
Object.entries(stats.byShipping).forEach(([k, v]) => console.log(`  ${k}: ${v} (${(v/stats.total*100).toFixed(1)}%)`));
console.log('\n按订单状态:');
Object.entries(stats.byStatus).forEach(([k, v]) => console.log(`  ${k}: ${v} (${(v/stats.total*100).toFixed(1)}%)`));
console.log('\n流向分析:');
console.log(`  保持率：${keepRate}%`);
console.log(`  降档率：${downgradeRate}%`);
console.log(`  提档率：${upgradeRate}%`);

// 保存数据
fs.writeFileSync('mock_data_1000.json', JSON.stringify(mockData, null, 2));
console.log('\n✅ 数据已保存到 mock_data_1000.json');
