# 物流分析仪表板

## 📦 项目简介

本项目包含多个版本的物流分析仪表板，支持正向物流和逆向物流的数据可视化分析。

---

## 🚀 在线访问

### GitHub Pages
**https://joye686.github.io/QQ/**

---

## 📊 仪表板版本

### 正向物流分析

| 版本 | 文件 | 说明 |
|------|------|------|
| v3.17.3 | `logistics-dashboard-v3.17.html` | **最新版** - 升档降档流向分析，支持 6 条曲线对比（5 国家 + 全量） |
| v3.16 | `logistics-dashboard-v3.16.html` | 升档降档流向分析 |
| v3.15 | `logistics-dashboard-v3.15.html` | 修复国家联动/平均线/百分比显示 |
| v3.14 | `logistics-dashboard-v3.14.html` | 新增升档降档流向分析图 |
| v3.13 | `logistics-dashboard-v3.13.html` | 产品维度三级展示 |
| v3.12 | `logistics-dashboard-v3.12.html` | 表格列对齐优化 |
| v3.11 | `logistics-dashboard-v3.11.html` | 详细表联动修复 |
| v3.10 | `logistics-dashboard-v3.10.html` | 完整真实数据版 |

### 逆向物流分析

| 版本 | 文件 | 说明 |
|------|------|------|
| P0+P1+P2 | `reverse-logistics-dashboard.html` | 逆向物流分析仪表板 |

### 其他版本

- `logistics-dashboard-v3.2.html` - 简化测试版
- `logistics-dashboard-v5.html` - T 字型流向分析
- `package-split-dashboard.html` - 分包分析看板

---

## 🔧 v3.17.3 功能特性

### 核心功能
- ✅ **升档降档流向分析** - 桑基图展示客户选择 vs 实际发出
- ✅ **多仓库对比** - 嘉兴仓 vs 海外仓
- ✅ **多维度筛选** - 时间、仓库、国家、产品（三级联动）、订单类型
- ✅ **智能仓库识别** - 自动识别 jiaxing、us_warehouse、ca_warehouse 等
- ✅ **全量数据曲线** - 选择"全部"时显示 6 条曲线（5 国家 + 全量汇总）
- ✅ **数据标签** - 所有折线图数据点上方显示数值

### 指标卡片
- 单价/KG
- 单价/包裹
- 发货包裹数
- 订单数
- 包单件
- 每包裹重量
- 物流占收入比
- 累计物流费

### 图表分析
- 嘉兴仓 vs 海外仓折线图（按天/周/月/年）
- 订单结构分析（全部发货/部分发货/未发货）
- 发货仓库占比（嘉兴仓/海外仓）
- 流向分析桑基图
- 升档/降档/保持率指标

---

## 📁 数据文件

| 文件 | 说明 | 大小 |
|------|------|------|
| `demo_data_real.min.json` | 压缩版真实数据 | ~1.4MB |
| `demo_data_sample.json` | 示例数据（100 条） | ~74KB |

---

## 💻 本地运行

### 方法 1：直接打开
```bash
# 直接用浏览器打开 HTML 文件
open logistics-dashboard-v3.17.html
```

### 方法 2：本地服务器
```bash
# Python 3
python3 -m http.server 8000

# 访问 http://localhost:8000/logistics-dashboard-v3.17.html
```

---

## 📝 更新日志

### v3.17.3 (2026-03-17)
- ✅ 选择"全部"时显示 6 条曲线（美国、英国、加拿大、澳大利亚、其他、全部）
- ✅ 所有折线图数据点上方显示数值标签
- ✅ "全部"曲线用黑色显示，字体稍大

### v3.17.2 (2026-03-17)
- ✅ 修复全量数据图表同步更新问题
- ✅ 修复海外仓 Excel 表格空值问题

### v3.17.1 (2026-03-17)
- ✅ 智能识别仓库类型（支持多种命名变体）

### v3.17 (2026-03-17)
- ✅ 使用正确的物流费列名
- ✅ 新增全量数据折线图
- ✅ 基于 v3.16 完整版本修改

---

## 🛠️ 技术栈

- **图表库**: ECharts 5.4.3
- **日期选择**: Flatpickr
- **数据处理**: 原生 JavaScript
- **样式**: CSS3 + Flexbox/Grid

---

## 📞 问题反馈

如有问题或建议，请提交 Issue 或直接联系。

---

## 📄 License

MIT License
