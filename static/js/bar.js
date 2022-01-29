// 基于准备好的dom，初始化echarts实例
const myChart = echarts.init(document.getElementById('main'));

option = {
    aria: {
        enabled: true,
        decal: {
            show: true
        }
    },
    backgroundColor: '#000000',
    color: ['#ff0', '#0f0', '#61a0a8', '#d48265', '#91c7ae', '#749f83', '#ca8622', '#bda29a', '#6e7074', '#546570', '#c4ccd3'],
    title: {
        text: '交易信号',
        left: 0,
        textStyle: {
            color: '#ffdf00'
        }
    },
    animation: false,
    grid: {
        left: '4%',
        right: '3%'
    },
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'line'
        }
    },
    legend: {
        data: [
            '日K',
            {
                name: 'UP_LINE'
            },
            {
                name: 'DOWN_LINE'
            }
        ],
        selectedMode: false,
        textStyle: {
            color: '#fff'
        }
    },
    xAxis: {
        type: 'category',
        data: [],
        axisLine: {
            lineStyle: {
                color: '#9c0000'
            }
        },
        boundaryGap: false
    },
    yAxis: {
        type: 'value',
        splitNumber: 3,
        splitLine: {
            lineStyle: {
                color: '#9c0000'
            }
        },
        axisLine: {
            lineStyle: {
                color: '#9c0000'
            }
        },
        scale: true,
        min: 'dataMin',
        max: 'dataMax'
    },
    dataZoom: [
        {
            show: true,
            type: 'slider',
            backgroundColor: '#000',
            fillerColor: '#212421',
            borderColor: '#525152',
            handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
            handleSize: '70%',
            textStyle: {
                color: '#94aede'
            },
            throttle: 0,
            start: 80,
            end: 100
        }
    ],
    series: [
        {
            name: '日K',
            type: 'candlestick',
            data: [],
            itemStyle: {
                normal: {
                    color: '#000000',
                    color0: '#6be7ff',
                    borderColor: '#ff4142',
                    borderColor0: '#6be7ff'
                }
            },
            markLine: {
                symbol: ['none', 'none'],
                label: {
                    normal: {show: false},
                    emphasis: {show: false}
                },
                lineStyle: {
                    normal: {
                        width: 3,
                        type: 'solid',
                        color: '#fff'
                    }
                },
                animation: false,
                data: []
            }
        },
        {
            name: 'UP_LINE',
            type: 'line',
            lineStyle: {normal: {width: 1, color: '#ff0'}},
            showSymbol: false,
            data: []
        },
        {
            name: 'DOWN_LINE',
            type: 'line',
            lineStyle: {normal: {width: 1, color: '#0f0'}},
            showSymbol: false,
            data: []
        }
    ]
};

// 使用刚指定的配置项和数据显示图表。
myChart.setOption(option);

$.get('/bar_data?strategy=' + getUrlParameter('strategy') + '&inst_id=' + getUrlParameter('inst_id'), function (rst) {
    myChart.setOption({
        title: {
            text: rst.title
        },
        xAxis: {
            data: rst.x
        },
        series: [
            {
                name: '日K',
                data: rst.k,
                markLine: {
                    data: rst.trade
                }
            },
            {
                name: 'UP_LINE',
                data: rst.up
            },
            {
                name: 'DOWN_LINE',
                data: rst.down
            }
        ]
    });
});

$(window).on('resize', function () {
    myChart.resize();
});
