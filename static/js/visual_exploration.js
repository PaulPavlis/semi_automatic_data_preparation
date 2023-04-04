graphs_one_column = ["Histogram", "Pie Chart"];

function make_column_selects_available() {
    graph_type_value = $("#graph_type")[0].value;

    // $("#column_2")[0].disabled = graphs_one_column.includes(graph_type_value);

    if (graphs_one_column.includes(graph_type_value)) {
        $("#column_2")[0].disabled = true;
        $("#column_2")[0].value = "Not available for this graph type";
    } else {
        $("#column_2")[0].disabled = false;
        $("#column_2")[0].value = "None";
    }
}

function construct_new_graph() {
    graph_type_value = $("#graph_type")[0].value;
    column_1_value = $("#column_1")[0].value;
    column_2_value = $("#column_2")[0].value;

    // console.log(graph_type_value);

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

// Initialise the empty graph
$(document).ready(function () {
    construct_new_graph();
    make_column_selects_available();
});
