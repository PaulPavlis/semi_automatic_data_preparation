function cb(selection) {
    // console.log("Inside: " + selection);
    if (selection == "None") {
        url_end = "return_empty_plot";
    } else {
        url_end = "return_plot_active_ajax_data";
    }

    $.getJSON({
        url: "/data_exploration/" + url_end,
        data: { data: selection },
        success: function (result) {
            Plotly.react("chart", result, {});
        },
    });
}

cb("None");
