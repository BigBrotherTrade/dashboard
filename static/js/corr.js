// 基于准备好的dom，初始化echarts实例
var myChart = echarts.init(document.getElementById('main'));

option = {
    tooltip: {
        position: 'top'
    },
    grid: {
        top: '8%',
        left: '11%',
        right: '1%',
        bottom: '1%'
    },
    xAxis: {
        type: 'category',
        position: 'top',
        axisLabel: {
            interval: 0,
            rotate: -45
        },
        data: []
    },
    yAxis: {
        type: 'category',
        axisLabel: {interval: 0},
        inverse: true,
        data: []
    },
    visualMap: {
        type: 'piecewise',
        min: -1,
        max: 1,
        calculable: true,
        precision: 0.01,
        splitNumber: 8,
        orient: 'vertical',
        left: 'right',
        bottom: '19%',
        inRange: {
            color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
            // color: ['#216506', '#4ef833','#ecf833','#f4a33a','#ef4a1d']
        }
    },
    series: [
        {
            name: '相关性系数',
            type: 'heatmap',
            data: []
        },
        {
            name: '投资组合评分',
            title: {offsetCenter: [0, '20%']},
            type: 'gauge',
            axisLine: {
                lineStyle: {
                    color: [[0.2, '#be201f'], [0.4, '#f99a27'], [0.6, '#fade00'], [0.8, '#8bc536'], [1, '#009f47']]
                }
            },
            splitLine: {show: false},
            min: 0,
            max: 100,
            center: ['75%', '31%'],
            radius: '45%',
            data: []
        }
    ]
};

// 使用刚指定的配置项和数据显示图表。
myChart.setOption(option);

$.get('/corr_data?year=' + $('#main').data('year'), function (rst) {
    myChart.setOption({
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
            },
            {
                name: '投资组合评分',
                data: [{value: rst.score, name: '投资组合评分'}]
            }
        ]
    });
});

$(window).on('resize', function () {
    myChart.resize();
});

$(".chosen-select").chosen({include_group_label_in_selected: true});
