function show_current_dtype_of_column() {
    change_column_value = $("#change_column")[0].value;
    new_column_type = $("#new_column_type")[0];
    // console.log(change_column_value);
    // console.log(new_column_type.value);
    if (change_column_value != "None") {
        $.ajax({
            method: "GET",
            url: "/data_preparation/return_ajax_dtype_value_of_column",
            cache: false,
            data: {
                column_name: change_column_value,
            },
        }).done(function (data) {
            // console.log("Received: " + data);
            new_column_type.value = data;
        });
    } else {
        new_column_type.value = "None";
        // console.log("Doing nothing for None as a value of change_column.");
    }
}

$(document).ready(function () {
    show_current_dtype_of_column();
    $("#add_row_div").toggle();
    $("#show_add_row").click(function () {
        $("#add_row_div").toggle();
    });
});
