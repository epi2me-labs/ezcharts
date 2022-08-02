const update_charts_on_tab_change = () => {
    ['shown.bs.tab'].forEach(function(evt) {
        document.addEventListener(evt, function(e) {
            if (e.type === 'shown.bs.tab') {
                const charts = document.querySelectorAll('.chart-container');
                [...charts].forEach(chart => {
                    const chart_dom = document.getElementById(chart.id)
                    console.log(echarts.getInstanceByDom(chart_dom));
                    echarts.getInstanceByDom(chart_dom).resize()
                });
            }
        });
    });
}
update_charts_on_tab_change();
