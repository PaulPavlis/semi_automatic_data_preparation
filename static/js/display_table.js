$(document).ready(function () {
    get_prepared_df = "false";

    if ($("#get_prepared_table")[0]) {
        get_prepared_df = "true";
    }

    $.ajax({
        method: "GET",
        url: "/return_active_ajax_data/" + get_prepared_df,
        cache: false,
    }).done(function (data) {
        column_order = data["column_order"].split("|||");
        column_order.shift();
        // console.log("Hi");
        // console.log("Sample of data:", data);
        // console.log(Object.keys(data["data"][0]));
        // console.log(column_order);
        // table_keys_list = Object.keys(data["data"][0]);
        // table_keys_dict = table_keys_list.map((x) => {
        //     return { data: x };
        // });

        table_keys_dict = column_order.map((x) => {
            return { data: x };
        });

        console.log(table_keys_dict);

        $("#data").DataTable({
            ajax: "/return_active_ajax_data/" + get_prepared_df,
            columns: table_keys_dict,
            scrollX: true,
        });
    });
});
