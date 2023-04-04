graphs_one_column = ["Histogram", "Pie Chart", "Box Plot", "Violin Plot"];
graphs_two_column = ["Scatter Plot", "Bar Chart", "Density Heatmap"];

function make_column_selects_available() {
    graph_type_value = $("#graph_type")[0].value;
    // $("#column_2")[0].disabled = graphs_one_column.includes(graph_type_value);
    column_1 = $("#column_1")[0];
    column_2 = $("#column_2")[0];

    if (graphs_one_column.includes(graph_type_value)) {
        column_1.disabled = false;
        if (column_1.value == "Not available for this graph type") {
            column_1.value = "None";
        }
        column_2.disabled = true;
        column_2.value = "Not available for this graph type";
    } else if (graphs_two_column.includes(graph_type_value)) {
        column_1.disabled = false;
        if (column_1.value == "Not available for this graph type") {
            column_1.value = "None";
        }
        column_2.disabled = false;
        column_2.value = "None";
    } else {
        column_1.disabled = true;
        column_1.value = "Not available for this graph type";
        column_2.disabled = true;
        column_2.value = "Not available for this graph type";
    }
}

function construct_new_graph() {
    graph_type_value = $("#graph_type")[0].value;
    column_1_value = $("#column_1")[0].value;
    column_2_value = $("#column_2")[0].value;

    // console.log(graph_type_value);

    if (graph_type_value == "None") {
        url_end = "return_empty_plot";
    } else {
        url_end = "return_plot_active_ajax_data";
    }

    column_1_value = column_1_value == "None" ? "" : column_1_value;
    column_2_value = column_2_value == "None" ? "" : column_2_value;
    column_1_value =
        column_1_value == "Not available for this graph type"
            ? ""
            : column_1_value;
    column_2_value =
        column_2_value == "Not available for this graph type"
            ? ""
            : column_2_value;

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
