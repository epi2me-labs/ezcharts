const update_charts_on_tab_change = () => {
    ['shown.bs.tab'].forEach(function(evt) {
        document.addEventListener(evt, function(e) {
            if (e.type === 'shown.bs.tab') {
                const charts = document.querySelectorAll('.echarts-chart-container');
                [...charts].forEach(chart => {
                    const chart_dom = document.getElementById(chart.id)
                    echarts.getInstanceByDom(chart_dom).resize()
                });
            }
        });
    });
}
update_charts_on_tab_change();

const update_dropdown_title = () => {
    for (let dropDownHeader of document.getElementsByClassName("dropdown-toggle")) {
        // only change title if the element has the attribute to request it
        if (! dropDownHeader.hasAttribute("data-ezc-updateDropDownTitle")) {
            continue;
        }
        // get the associated dropdown items
        const dropDownLi = dropDownHeader.parentElement;
        const dropDownItems = dropDownLi.getElementsByClassName("dropdown-item");
        // change dropdown tab title to display name of first item if this tab is active
        if (dropDownItems[0].classList.contains('active')) {
            dropDownHeader.innerHTML = dropDownItems[0].innerHTML;
        }
        // add listener to each dropdown item to update the tab header when clicked
        for (let dropDownItem of dropDownItems) {
            dropDownItem.onclick = () => {
                dropDownHeader.innerHTML = dropDownItem.innerHTML;
                console.log(dropDownItem.id);
            };
        }
    }
};
window.addEventListener("load", update_dropdown_title);
