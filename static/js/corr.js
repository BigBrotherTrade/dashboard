// 基于准备好的dom，初始化echarts实例
var myChart = echarts.init(document.getElementById('main'));

option = {
    tooltip: {
        position: 'top'
    },
    grid: {
        left: '4%',
        right: '3%'
    },
    xAxis: {
        type: 'category',
        data: []
    },
    yAxis: {
        type: 'category',
        data: []
    },
    visualMap: {
        type: 'continuous',
        min: -1,
        max: 1,
        calculable: true,
        precision: 0.01,
        orient: 'horizontal',
        left: 'center',
        inRange: {
            color: ['#216506', '#4ef833','#ecf833','#f4a33a','#ef4a1d']
        }
    },
    series: [{
        name: '相关性系数',
        type: 'heatmap',
        data: []
    }]
};

// 使用刚指定的配置项和数据显示图表。
myChart.setOption(option);

$.get('/corr_data', function (rst) {
    myChart.setOption({
        title: {
            text: rst.title
        },
        xAxis: {
            data: rst.index
        },
        yAxis: {
            data: rst.index
        },
        series: [
            {
                name: '相关性系数',
                data: rst.data
            }
        ]
    });
});

$(window).on('resize', function () {
    myChart.resize();
});
