function construct_before_and_after(
    column_prepare_value,
    graph_type_value = "violin"
) {
    // console.log(column_prepare_value);
    make_get_json_ajax(
        "/data_preparation/return_ajax_construct_before",
        {
            column_prepare: column_prepare_value,
            graph_type: graph_type_value,
        },
        "chart_before"
    );
    make_get_json_ajax(
        "/data_preparation/return_ajax_construct_after",
        {
            column_prepare: column_prepare_value,
            graph_type: graph_type_value,
        },
        "chart_after"
    );
}

function construct_new_graph(
    column_prepare_value,
    graph_type_value = "violin"
) {
    // console.log(column_prepare_value);
    // console.log(graph_type_value);
    make_get_json_ajax(
        "/data_preparation/return_ajax_construct_before",
        {
            column_prepare: column_prepare_value,
            graph_type: graph_type_value,
        },
        "chart_before"
    );
}

function make_get_json_ajax(url_used, data_sent, div_id) {
    $.getJSON({
        url: url_used,
        data: data_sent,
        success: function (result) {
            Plotly.react(div_id, result, {});
        },
    });
}

// Initialise the empty graph
$(document).ready(function () {
    construct_new_graph("None");
});
