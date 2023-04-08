function construct_before_and_after(
    column_prepare_value,
    graph_type_value = "violin"
) {
    console.log(column_prepare_value);
    $.getJSON({
        url: "/data_preparation/return_ajax_construct_before",
        data: {
            column_prepare: column_prepare_value,
            graph_type: graph_type_value,
        },
        success: function (result) {
            Plotly.react("chart_before", result, {});
        },
    });
    $.getJSON({
        url: "/data_preparation/return_ajax_construct_after",
        data: {
            column_prepare: column_prepare_value,
            graph_type: graph_type_value,
        },
        success: function (result) {
            Plotly.react("chart_after", result, {});
        },
    });
}

function construct_new_graph(
    column_prepare_value,
    graph_type_value = "violin"
) {
    $.getJSON({
        url: "/data_preparation/return_ajax_construct_before",
        data: {
            column_prepare: column_prepare_value,
            graph_type: graph_type_value,
        },
        success: function (result) {
            Plotly.react("chart_before", result, {});
        },
    });
}

// Initialise the empty graph
$(document).ready(function () {
    construct_new_graph("None");
});
