function cbb() {
    graph_type_value = $("#graph_type")[0].value;
    column_1_value = $("#column_1")[0].value;
    column_2_value = $("#column_2")[0].value;

    console.log(graph_type_value);

    if (column_1_value == "None") {
        url_end = "return_empty_plot";
    } else {
        url_end = "return_plot_active_ajax_data";
    }

    $.getJSON({
        url: "/data_exploration/" + url_end,
        data: {
            graph_type: graph_type_value,
            column_1: column_1_value,
            column_2: column_2_value,
        },
        success: function (result) {
            Plotly.react("chart", result, {});
        },
    });
}

function cb(selection) {
    // console.log("Inside: " + selection);
    if (selection == "None") {
        url_end = "return_empty_plot";
    } else {
        url_end = "return_plot_active_ajax_data";
    }

    $.getJSON({
        url: "/data_exploration/" + url_end,
        data: { column_1: selection },
        success: function (result) {
            Plotly.react("chart", result, {});
        },
    });
}

cb("None");
