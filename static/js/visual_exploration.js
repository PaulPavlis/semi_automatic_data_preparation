function cb(selection) {
    $.getJSON({
        url: "/data_exploration/return_plot_active_ajax_data",
        data: { data: selection },
        success: function (result) {
            Plotly.react("chart", result, {});
        },
    });
}

cb("1");
console.log("Hi");
