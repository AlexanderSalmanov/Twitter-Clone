// password hide-reveal portion
function passwordTrigger(){
    $('.passwordVisibility').toggleClass('fa-eye fa-eye-slash someElement')
    if ($('#id_password').attr('type') === 'password') {
        $('#id_password').attr('type', 'text');
        $('#id_password_2').attr('type', 'text');
    } else {
        $('#id_password').attr('type', 'password')
        $('#id_password_2').attr('type', 'password')
    }
}

// refresh character count in textarea
function charCountRefresh() {
    $(".actual").text(0);
}
