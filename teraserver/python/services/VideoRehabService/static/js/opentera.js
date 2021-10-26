function setCookie(cname, cvalue, exminutes) {
  var d = new Date();
  d.setTime(d.getTime() + (exminutes*60*1000));
  var expires = "expires="+ d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/;secure;";
}

function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function deleteCookie(cname){
    document.cookie = cname + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;secure;";
}

function doGetRequest(request_url, request_port, request_path, token, success_response, error_response, scheme){
    if (success_response === undefined){
        success_response = getRequestSuccess;
    }
    if (error_response === undefined){
        error_response = getRequestError;
    }
    if (scheme === undefined){
        scheme = 'https';
    }

    $.ajax({
          type: "GET",
          url: scheme + '://' + request_url + ':' + request_port + request_path ,
          success: success_response,
          error: error_response,
          beforeSend: function (xhr) {
              xhr.setRequestHeader('Authorization', 'OpenTera ' + token);
          }
        });
}

function doPostRequest(request_url, request_port, request_path, token, data, success_response, error_response, scheme = 'https'){
    if (success_response === undefined){
        success_response = getRequestSuccess;
    }
    if (error_response === undefined){
        error_response = getRequestError;
    }
    if (scheme === undefined){
        scheme = 'https';
    }

    $.ajax({
          type: "POST",
          url: scheme + '://' + request_url + ':' + request_port + request_path,
          data: data,
          dataType: "json",
          contentType: "application/json; charset=utf-8",
          success: success_response,
          error: error_response,
          beforeSend: function (xhr) {
              xhr.setRequestHeader('Authorization', 'OpenTera ' + token);
          }
        });
}

function getRequestSuccess(response, status, request){
    console.log("getRequestSuccess: " + JSON.stringify(response));
}

function getRequestError(event, status){
    console.log("getRequestError: " + event.status + " : " + event.responseText);
}

function hideElement(id){
	document.getElementById(id).style.display = "none";
}

function showElement(id){
	document.getElementById(id).style.display = "inline";
}

function isBrowserSupported(){
    return browser.satisfies({
        chrome: ">55",
        firefox: ">50",
        safari: ">=11",
        edge: ">79"
    });
}

function showError(err_context, err_msg, ui_display, show_retry=true){
    console.error(err_context + ": " + err_msg);

    if (ui_display === true){
        $('#errorDialogText')[0].innerHTML = err_msg;
        $('#errorDialog').modal('show');
        (show_retry) ? $('#errorRefresh').show() : $('#errorRefresh').hide();
    }
}