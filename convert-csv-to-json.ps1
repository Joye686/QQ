# CSV 转 JSON 转换器 - 物流仪表板 V3.14
# 使用方法：右键 → "使用 PowerShell 运行"

$ErrorActionPreference = "Stop"

# 配置
$csvFile = "shipping_fee_list_20260311_182918.csv"  # 修改为你的 CSV 文件名
$jsonFile = "demo_data_real.json"

Write-Host "📦 CSV 转 JSON 转换器 - 物流仪表板 V3.14" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查文件是否存在
if (-not (Test-Path $csvFile)) {
    Write-Host "❌ 错误：找不到文件 $csvFile" -ForegroundColor Red
    Write-Host "请确保 CSV 文件和此脚本在同一目录" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "按任意键退出..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "📂 输入文件：$csvFile" -ForegroundColor Green
Write-Host "📂 输出文件：$jsonFile" -ForegroundColor Green
Write-Host ""
Write-Host "⏳ 正在读取 CSV 文件..." -ForegroundColor Yellow

# 读取 CSV
try {
    $data = Import-Csv -Path $csvFile -Encoding UTF8
    Write-Host "✅ 读取完成，共 $($data.Count) 行" -ForegroundColor Green
} catch {
    Write-Host "❌ 读取 CSV 失败：$($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "按任意键退出..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host ""
Write-Host "⏳ 正在转换数据..." -ForegroundColor Yellow

# 国家代码映射
$countryMap = @{
    '美国' = 'US'; 'US' = 'US'; 'USA' = 'US'; 'United States' = 'US'
    '英国' = 'UK'; 'UK' = 'UK'; 'GB' = 'UK'; 'United Kingdom' = 'UK'
    '加拿大' = 'CA'; 'CA' = 'CA'; 'Canada' = 'CA'
    '澳大利亚' = 'AU'; 'AU' = 'AU'; 'Australia' = 'AU'
}

# 仓库代码映射
$warehouseMap = @{
    '嘉兴仓' = 'jiaxing'; '嘉兴' = 'jiaxing'; '中国仓' = 'jiaxing'
    '美国仓' = 'overseas'; '海外仓' = 'overseas'; '海外' = 'overseas'
    '英国仓' = 'overseas'; '加拿大仓' = 'overseas'; '澳大利亚仓' = 'overseas'
}

# 速度类型映射
$speedMap = @{
    '快速' = '快'; '快' = '快'; 'Expedited' = '快'; 'Express' = '快'
    '普通' = '慢'; '慢' = '慢'; 'Standard' = '慢'; 'Regular' = '慢'
}

# 产品 L1 标准列表
$productL1Standard = @(
    'JC-USPS', 'JC-UPS Ground Return', 'HABIT POST delivery', 'HABIT Commercial delivery',
    'Yanwen Airmail Registered', 'Yanwen Huixuan', 'Yanwen Fully-tracked',
    'YUNTU THPHR', 'Yuntu registration', 'yuntu remote', 'Yuntu Commercial delivery',
    'CNE clothing line', 'CNE Global Smart', 'CNE global priority',
    'liumai-USPS', 'Liumai L01 USA', 'liumai L01',
    'JS EXPRESS', 'JS clothing line', 'JS Super Express',
    'MPwarehouse-RM', 'MP-Return-RM',
    'LTWarehouse-CAPOST', 'LTWarehouse-UNIUNI', 'LT-CAPOST Expedited',
    'LTRemote-USPS-K', 'LT-Return-CA', 'LT-Return-USPS',
    'US-UNI', 'US-UNI2', 'Happy Returns',
    'Winit Fulfillment-2D', 'Winit Fulfillment-5D', 'Winit Fulfillment-7D',
    'CK1-usps', 'USPS Return', '4PX-Linkpost Economy'
)

function Get-ProductL1($productL3) {
    if ($productL1Standard -contains $productL3) { return 'Standard' }
    if (@('FedEx Priority', 'FedEx Economy', 'DHL Express', 'AWPHK-DHL MAX') -contains $productL3) { return 'Expedited' }
    return 'Standard'
}

function Convert-Number($value, $default = 0) {
    if ([string]::IsNullOrWhiteSpace($value)) { return $default }
    $result = 0
    if ([decimal]::TryParse($value, [ref]$result)) {
        return [math]::Round($result, 2)
    }
    return $default
}

# 转换数据
$jsonData = @()
$progress = 0

foreach ($row in $data) {
    $progress++
    if ($progress % 5000 -eq 0) {
        Write-Host "   已处理 $progress / $($data.Count) 行..." -ForegroundColor Gray
    }
    
    # 获取字段值（自动检测列名）
    $getValue = {
        param($names)
        foreach ($name in $names) {
            if ($row.PSObject.Properties.Name -contains $name) {
                $val = $row.$name
                if (-not [string]::IsNullOrWhiteSpace($val)) {
                    return $val.ToString().Trim()
                }
            }
        }
        return ''
    }
    
    $productL3 = &$getValue @('product_l3', 'productl3', 'product_3', 'product3')
    $country = &$getValue @('country', 'country_name', 'countryName')
    $warehouse = &$getValue @('warehouse', 'warehouse_name', 'warehouseName')
    $speedType = &$getValue @('speed_type', 'speedtype', 'speed')
    
    $jsonObj = [PSCustomObject]@{
        order_no = &$getValue @('order_no', 'orderno', 'orderNo', '订单号')
        ship_no = &$getValue @('ship_no', 'shipno', 'shipNo', '发货单号')
        order_date = &$getValue @('order_date', 'orderdate', 'orderDate', '订单日期')
        site = (&$getValue @('site', '站点')) -or 'M'
        speed_type = $speedType -or '普通'
        product_l3 = $productL3
        tracking_no = &$getValue @('tracking_no', 'trackingno', 'trackingNo', '追踪号')
        warehouse = $warehouse
        country = $country
        item_count = (Convert-Number (&$getValue @('item_count', 'itemcount', 'itemCount', '商品数量')) 1)
        order_status = (&$getValue @('order_status', 'orderstatus', 'orderStatus', '订单状态')) -or '已发货'
        promise_ship_date = &$getValue @('promise_ship_date', 'promiseshipdate', '承诺发货日期')
        ship_date = &$getValue @('ship_date', 'shipdate', '发货日期')
        promise_delivery_date = &$getValue @('promise_delivery_date', 'promisedeliverydate', '承诺送达日期')
        delivery_date = &$getValue @('delivery_date', 'deliverydate', '妥投日期')
        delivery_days = (Convert-Number (&$getValue @('delivery_days', 'deliverydays', '送达天数')) 0)
        weight_kg = (Convert-Number (&$getValue @('weight_kg', 'weightkg', 'weightKg', '重量', '重量_kg')) 0)
        logistics_cost = (Convert-Number (&$getValue @('logistics_cost', 'logisticscost', '物流费用', '运费')) 0)
        ship_month = &$getValue @('ship_month', 'shipmonth', '发货月份')
        order_month = &$getValue @('order_month', 'ordermonth', '订单月份')
        product_l1 = (&$getValue @('product_l1', 'productl1', 'product_1', 'product1')) -or (Get-ProductL1 $productL3)
        is_overdue_ship = (&$getValue @('is_overdue_ship', 'isoverdueship', '是否超期发货')) -or '否'
        is_overdue_delivery = (&$getValue @('is_overdue_delivery', 'isoverduedelivery', '是否超期送达')) -or '未超期'
        overdue_days = (Convert-Number (&$getValue @('overdue_days', 'overduedays', '超期天数')) 0)
        supplier = &$getValue @('supplier', '供应商')
        promise_days = (Convert-Number (&$getValue @('promise_days', 'promisedays', '承诺天数')) 0)
        package_count = (Convert-Number (&$getValue @('package_count', 'packagecount', '包裹数')) 1)
        order_count = (Convert-Number (&$getValue @('order_count', 'ordercount', '订单数')) 1)
        revenue = (Convert-Number (&$getValue @('revenue', '收入', '销售额')) 0)
        order_type = (&$getValue @('order_type', 'ordertype', '订单类型')) -or 'shipped'
        country_code = $countryMap[$(&$getValue @('country_code', 'countrycode', '国家代码'))] -or $countryMap[$country] -or 'OTHER'
        warehouse_code = $warehouseMap[$(&$getValue @('warehouse_code', 'warehousecode', '仓库代码'))] -or $warehouseMap[$warehouse] -or 'jiaxing'
        speed_type_code = $speedMap[$speedType] -or $speedMap[(&$getValue @('speed_type_code', 'speedtypecode'))] -or '慢'
        product_l2 = &$getValue @('product_l2', 'productl2', 'product_2', 'product2')
    }
    
    $jsonData += $jsonObj
}

Write-Host ""
Write-Host "⏳ 正在保存 JSON 文件..." -ForegroundColor Yellow

# 保存 JSON
try {
    $jsonData | ConvertTo-Json -Depth 10 | Out-File -FilePath $jsonFile -Encoding UTF8
    Write-Host "✅ 转换完成！" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 统计信息:" -ForegroundColor Cyan
    Write-Host "   输入文件：$csvFile" -ForegroundColor White
    Write-Host "   输出文件：$jsonFile" -ForegroundColor White
    Write-Host "   记录数：$($jsonData.Count) 条" -ForegroundColor White
    Write-Host ""
    Write-Host "🎉 下一步操作:" -ForegroundColor Cyan
    Write-Host "   1. 将 $jsonFile 放到仪表板目录" -ForegroundColor White
    Write-Host "   2. 刷新浏览器打开 logistics-dashboard-v3.14.html" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "❌ 保存 JSON 失败：$($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "按任意键退出..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
