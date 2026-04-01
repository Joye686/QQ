# 物流分析仪表板开发经验总结

## ⚠️ 常见错误与解决方案

### 1. 变量未定义错误
**问题：** `ReferenceError: globalData is not defined`
**原因：** 使用了未定义的变量 `globalData`
**解决：** 使用 `const filteredData = filterData()` 获取筛选后的数据
**教训：** 
- 始终使用已定义的变量
- 优先使用 `filterData()` 获取当前筛选条件下的数据
- 不要假设变量存在

### 2. 重复函数定义
**问题：** `updateCharts()` 函数被定义两次，后者覆盖前者
**原因：** 代码复制粘贴时没有删除旧函数
**解决：** 搜索所有函数定义，确保唯一性
**教训：**
- 修改前先用 `grep -n "function 函数名"` 检查是否有重复定义
- 合并函数时确保删除旧定义
- 提交前检查关键函数是否只定义一次

### 3. 调用未定义的函数
**问题：** `renderClaimCharts is not defined`
**原因：** 调用了不存在的函数
**解决：** 注释掉或移除未定义函数的调用
**教训：**
- 添加新函数调用前先确认函数已定义
- 用 `grep -n "function 函数名"` 确认函数存在
- 不确定时先注释掉

### 4. HTML 元素 ID 重复
**问题：** 同一个 ID 被多个元素使用，导致图表渲染失败
**原因：** 复制 HTML 结构时忘记修改 ID
**解决：** 确保每个图表容器有唯一的 ID
**教训：**
- 修改 HTML 布局时仔细检查所有 ID
- 使用搜索确认 ID 唯一性
- 图表 ID 命名规范：`xxx-chart`

### 5. GitHub Pages 缓存问题
**问题：** 推送后页面仍显示旧版本
**原因：** GitHub Pages 和浏览器缓存
**解决：**
- 修改版本号和 Build 时间戳
- 使用新版本号创建新文件（如 v3.17.7）
- 告诉用户强制刷新（Ctrl+F5）
**教训：**
- 每次修改都更新版本号和 Build 时间
- 大改动时用新版本号创建新文件
- 在回复中明确告知用户强制刷新

### 6. 标题不一致
**问题：** `<title>` 和 `<h1>` 版本号不一致
**原因：** 只修改了一处
**解决：** 同时修改两处
**教训：**
- 更新版本号时同时修改：
  - `<title>` 标签
  - `<h1>` 标题
  - Build 时间戳（注释）
- 用搜索确认所有位置都已更新

### 7. 图表渲染函数调用顺序
**问题：** 图表空白，因为渲染函数未被调用
**原因：** 忘记在 `updateCharts()` 中添加调用
**解决：** 确保所有图表渲染函数都在 `updateCharts()` 中被调用
**教训：**
- 新增图表后，立即在 `updateCharts()` 中添加调用
- 检查调用顺序：先渲染数据依赖少的，再渲染依赖多的
- 用注释标记每个函数的作用

---

## 📋 开发检查清单

### 修改 HTML 布局时
- [ ] 检查所有图表容器 ID 是否唯一
- [ ] 确认图表容器 ID 与 JS 中 `document.getElementById()` 匹配
- [ ] 更新 `<title>` 和 `<h1>` 版本号
- [ ] 更新 Build 时间戳

### 修改 JavaScript 时
- [ ] 用 `grep -n "function 函数名"` 检查函数是否重复定义
- [ ] 确认所有调用的函数都已定义
- [ ] 确认所有图表渲染函数都在 `updateCharts()` 中被调用
- [ ] 检查变量是否已定义（特别是 `globalData` vs `filteredData`）

### 提交前
- [ ] 本地打开 HTML 文件测试
- [ ] 检查控制台是否有错误（F12）
- [ ] 确认版本号一致（title、h1、文件名）
- [ ] 更新 Build 时间戳

### 推送后
- [ ] 确认 GitHub 上的文件已更新
- [ ] 检查 GitHub Pages 是否同步
- [ ] 告知用户强制刷新（Ctrl+F5）
- [ ] 提供带缓存清除参数的链接（如 `?v=3.17.7`）

---

## 🔧 常用命令

```bash
# 检查函数定义
grep -n "function 函数名" logistics-dashboard-v3.17.7.html

# 检查函数调用
grep -n "函数名 ()" logistics-dashboard-v3.17.7.html

# 检查变量使用
grep -n "变量名" logistics-dashboard-v3.17.7.html

# 检查 ID 使用
grep -n "id=\"xxx-chart\"" logistics-dashboard-v3.17.7.html

# 检查版本号
grep -n "v3.17" logistics-dashboard-v3.17.7.html | head -10

# 推送
git add logistics-dashboard-v3.17.7.html
git commit -m "fix(v3.17.7): 描述修改内容"
git push origin main
```

---

## 📊 图表布局规范（v3.17.7）

### 第一行（top-charts-row）
1. 各国订单数及占比 (`country-orders-chart`)
2. 各国客单价 (`country-aov-chart`)
3. 订单结构 - 订单口径 (`order-structure-chart`)
4. 发货仓库占比 - 发货口径 (`warehouse-ratio-chart`)

### 第二行（second-charts-row）
1. 各运费区间订单占比 (`range-ratio-chart`)
2. 各运费区间客单价 (`range-aov-chart`)
3. 分单次数分布 (`split-dist-chart`)
4. 分单占比趋势 (`split-trend-chart`)

### 渲染函数调用顺序（updateCharts 中）
```javascript
updateStats();
renderSecondRowCharts();  // 6 个图表
renderOrderStructure();
renderWarehouseRatio();
renderJiaxingTChart();
renderOverseasTChart();
renderTotalTChart();
renderDetailTable();
renderFlowChart();
// renderClaimCharts();  // 未定义，已注释
renderRangeCharts();
```

---

## 💡 核心原则

1. **先检查，后修改** - 用 grep 确认现有代码结构
2. **小步迭代** - 每次只改一个地方，测试后再继续
3. **版本一致** - title、h1、文件名版本号保持一致
4. **强制刷新** - 总是告知用户 Ctrl+F5
5. **注释标记** - 用注释说明每个函数的作用和状态

---

*最后更新：2026-04-01 v3.17.7*
