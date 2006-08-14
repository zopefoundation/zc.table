function onSortClickStandalone(column_name, sort_on_name) {
    window.location = addFieldToUrl(
            window.location.href, sort_on_name+':list='+column_name);
}

function addFieldToUrl(url, field) {
    if (url.indexOf('?') == -1)
        sep = '?';
    else
        sep = '&';
    return url + sep + field;
}

function onSortClickForm(column_name, sort_on_name) {
    field = document.getElementById(sort_on_name);
    if (field.value) field.value += ' ';
    field.value += column_name;
    field.form.submit();
}
