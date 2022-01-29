// 基于准备好的dom，初始化echarts实例
const myChart = echarts.init(document.getElementById('main'));

// 指定图表的配置项和数据
let option = {
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
        data: ['单位净值', '累计净值']
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
    // dataZoom: [
    //     {   // 这个dataZoom组件，默认控制x轴。
    //         type: 'slider', // 这个 dataZoom 组件是 slider 型 dataZoom 组件
    //         start: 50,      // 左边在 10% 的位置。
    //         end: 100         // 右边在 60% 的位置。
    //     }
    // ],
    series: [{
        name: '单位净值',
        type: 'line',
        data: []
    },{
        name: '累计净值',
        type: 'line',
        data: []
    }]
};

// 使用刚指定的配置项和数据显示图表。
myChart.setOption(option);

$.get('/nav_data?strategy=' + getUrlParameter('strategy'), function (rst) {
    myChart.setOption({
        series: [{
            name: '单位净值',
            data: rst.nav
        },{
            name: '累计净值',
            data: rst.accu
        }]
    });
});

$(window).on('resize', function () {
    myChart.resize();
});