$(document).ready(function () {
    $.ajax({
        method: "GET",
        url: "/data_preparation/return_ajax_data",
        cache: false,
    }).done(function (data) {
        console.log("Hi");
        console.log("Sample of data:", data);
        console.log(Object.keys(data["data"][0]));
        table_keys_list = Object.keys(data["data"][0]);

        table_keys_dict = table_keys_list.map((x) => {
            return { data: x };
        });

        console.log(table_keys_dict);

        $("#data").DataTable({
            ajax: "/data_preparation/return_ajax_data",
            columns: table_keys_dict,
        });
    });
});
