// 基于准备好的dom，初始化echarts实例
var secChart = echarts.init(document.getElementById('section'));
var posChart = echarts.init(document.getElementById('position'));

secChart.setOption({
    title: {
        text: '持仓合约分类'
    },
    tooltip: {
        trigger: 'axis'
    },
    legend: {
        x: 'center',
        data: ['持仓']
    },
    radar: [
        {
            indicator: [
                {text: '农产品', max: 11},
                {text: '工业品', max: 22},
                {text: '股指', max: 10},
                {text: '利率', max: 2},
                {text: '货币', max: 10}
            ]
        }
    ],
    series: [
        {
            type: 'radar',
            tooltip: {
                trigger: 'item'
            },
            itemStyle: {normal: {areaStyle: {type: 'default'}}},
            data: [
                {
                    value: [],
                    name: '持仓'
                }
            ]
        }
    ]
});

posChart.setOption({
    title: {
        text: '持仓方向对比',
        x: 'center'
    },
    tooltip: {
        trigger: 'item',
        formatter: "{a} <br/>{b} : {c} ({d}%)"
    },
    legend: {
        orient: 'vertical',
        left: 'left',
        data: ['多头持仓', '空头持仓']
    },
    series: [
        {
            name: '持仓',
            type: 'pie',
            data: [],
            itemStyle: {
                emphasis: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            }
        }
    ]
});

$.get('/status_data', function (rst) {
    secChart.setOption({
        series: [{
            data: [{
                value: rst.section,
                name: '持仓'
            }]
        }]
    })
    ;
    posChart.setOption({
        series: [
            {
                name: '持仓',
                data: [
                    {value: rst.long, name: '多头持仓'},
                    {value: rst.short, name: '空头持仓'}
                ]
            }
        ]
    });
});

$(window).on('resize', function () {
    secChart.resize();
});
