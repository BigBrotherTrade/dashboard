// 基于准备好的dom，初始化echarts实例
const myChart = echarts.init(document.getElementById('main'));

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
myChart.showLoading();
myChart.setOption(option);

function load_chart() {
    myChart.showLoading();
    var $checked = $("input[type=checkbox]:checked");
    if ($checked.length == 0) {
        return;
    }
    var ids = [];
    $checked.each(function () {
        ids.push($(this).val());
    });
    $.get('/corr_data?strategy='+getUrlParameter('strategy')+'&year='+getUrlParameter('year')+'&insts='+JSON.stringify(ids), function (rst) {
        myChart.hideLoading();
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
}

$(window).on('resize', function () {
    myChart.resize();
});

$(function () {
    $('.button-checkbox').each(function () {
        // Settings
        var $widget = $(this),
            $button = $widget.find('button'),
            $checkbox = $widget.find('input:checkbox'),
            color = $button.data('color'),
            settings = {
                on: {
                    icon: 'glyphicon glyphicon-check'
                },
                off: {
                    icon: 'glyphicon glyphicon-unchecked'
                }
            };
        // Event Handlers
        $button.on('click', function () {
            $checkbox.prop('checked', !$checkbox.is(':checked'));
            var checks = $('#div'+$(this).data('sec')+' > span > input:checked').length;
            $('#'+$(this).data('sec')+' > b').text(checks);
            load_chart();
            $checkbox.triggerHandler('change');
            updateDisplay();
        });
        $checkbox.on('change', function () {
            updateDisplay();
        });
        // Actions
        function updateDisplay() {
            var isChecked = $checkbox.is(':checked');
            // Set the button's state
            $button.data('state', (isChecked) ? "on" : "off");
            // Set the button's icon
            $button.find('.state-icon')
                .removeClass()
                .addClass('state-icon ' + settings[$button.data('state')].icon);
            // Update the button's color
            if (isChecked) {
                $button
                    .removeClass('btn-default')
                    .addClass('btn-' + color + ' active');
            }
            else {
                $button
                    .removeClass('btn-' + color + ' active')
                    .addClass('btn-default');
            }
        }
        // Initialization
        function init() {
            updateDisplay();
            // Inject the icon if applicable
            if ($button.find('.state-icon').length == 0) {
                $button.prepend('<i class="state-icon ' + settings[$button.data('state')].icon + '"></i>');
            }
        }
        init();
    });
    load_chart();
});