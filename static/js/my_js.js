// Fadeout function for all flashed messages
setTimeout(function () {
    $(".flashed_messages").fadeOut("slow");
}, 5000); // <-- time in milliseconds

// Display tables functionality
$(document).ready(function () {
    $(".display_table").DataTable();
});
