// CSRF token script
$(document).ready(function () {
    $(".browse").on('click', function () {
       $(".input_upload").click();
    });

    $(".input_upload").change(function (e) {
        var filename = e.target.files[0].name;

        $(".label_for_file_input").text(filename);
    });

});
