function construct_before_and_after() {
    $.getJSON({
        url: "/data_preparation/return_ajax_construct_before",
        data: { column_prepare: $("#column_prepare")[0].value },
        success: function (result) {
            Plotly.react("chart_before", result, {});
        },
    });
    $.getJSON({
        url: "/data_preparation/return_ajax_construct_after",
        data: { column_prepare: $("#column_prepare")[0].value },
        success: function (result) {
            Plotly.react("chart_after", result, {});
        },
    });
}

function construct_new_graph() {
    $.getJSON({
        url: "/data_preparation/return_ajax_construct_before",
        data: { column_prepare: $("#column_prepare")[0].value },
        success: function (result) {
            Plotly.react("chart_before", result, {});
        },
    });
}

// Initialise the empty graph
$(document).ready(function () {
    construct_new_graph();
});
