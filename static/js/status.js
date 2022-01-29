// 基于准备好的dom，初始化echarts实例
const secChart = echarts.init(document.getElementById('section'));
const posChart = echarts.init(document.getElementById('position'));
secChart.setOption({
    aria: {enabled: true, decal: {show: true}},
    title: {text: '持仓合约分类'},
    tooltip: {trigger: 'axis'},
    series: [{type: 'pie', roseType: 'area', tooltip: {trigger: 'item'}}]
});
posChart.setOption({
    aria: {enabled: true, decal: {show: true}},
    title: {text: '持仓方向对比', x: 'center'},
    color: ['#ab4340', '#3a773a'],
    tooltip: {trigger: 'item', formatter: "{a} <br/>{b} : {c} ({d}%)"},
    series: [{type: 'pie', tooltip: {trigger: 'item'}}]
});
$.get('/status_data?strategy=' + getUrlParameter('strategy'), function (rst) {
    secChart.setOption({series: [{ data: rst.section }]});
    posChart.setOption({series: [{ data: rst.direct  }]});
});
$(window).on('resize', function () {
    secChart.resize();
    posChart.resize();
});
