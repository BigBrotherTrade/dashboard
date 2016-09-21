// 基于准备好的dom，初始化echarts实例
var myChart = echarts.init(document.getElementById('main'));

// 指定图表的配置项和数据
var option = {
    title: {
        text: '操盘大哥v2.0'
    },
    tooltip: {
        trigger: 'axis'
    },
    toolbox: {
        feature: {
            saveAsImage: {}
        }
    },
    legend: {
        data: ['单位净值']
    },
    xAxis: {
        type: 'time',
        splitLine: {
            show: false
        }
    },
    yAxis: {
        type: 'value',
        splitLine: {
            show: false
        },
        scale: true,
        boundaryGap: ['10%', '10%']
    },
    series: [{
        name: '单位净值',
        type: 'line',
        smooth: 'true',
        data: []
    }]
};

// 使用刚指定的配置项和数据显示图表。
myChart.setOption(option);

$.get('/nav_data', function (rst) {
    myChart.setOption({
        series: [{
            name: '单位净值',
            type: 'line',
            smooth: 'true',
            data: rst
        }]
    });
});