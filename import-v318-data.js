// 📦 v3.18 数据导入脚本
// 使用方法：在浏览器 Console 中粘贴并执行此代码

(async function importV318Data() {
    console.log('🚀 开始导入 v3.18 数据...');
    
    try {
        // 从 GitHub 加载数据
        const response = await fetch('https://raw.githubusercontent.com/Joye686/QQ/main/v318-data.json');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        console.log(`✅ 数据加载成功！`);
        console.log(`   记录数：${data.count} 条`);
        console.log(`   汇率配置：`, data.exchange_rates);
        
        // 保存到 LocalStorage
        localStorage.setItem('logistics_rawData', JSON.stringify(data.data));
        localStorage.setItem('logistics_exchangeRates', JSON.stringify(data.exchange_rates));
        localStorage.setItem('logistics_saveTime', new Date().toLocaleString('zh-CN'));
        
        console.log(`✅ 数据已保存到 LocalStorage`);
        console.log(`   数据大小：${(JSON.stringify(data.data).length / 1024 / 1024).toFixed(2)} MB`);
        
        // 验证
        const saved = localStorage.getItem('logistics_rawData');
        if (saved) {
            console.log(`✅ 验证成功，数据已保存`);
        } else {
            throw new Error('保存后验证失败');
        }
        
        console.log(`\n🎉 导入完成！正在刷新页面...`);
        
        // 1 秒后刷新页面
        setTimeout(() => {
            location.reload();
        }, 1000);
        
    } catch (error) {
        console.error('❌ 导入失败:', error);
        console.log('\n💡 请检查：');
        console.log('   1. 网络连接是否正常');
        console.log('   2. GitHub 是否可以访问');
        console.log('   3. 浏览器是否允许 LocalStorage');
    }
})();
