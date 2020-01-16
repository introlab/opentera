function setCookie(cname, cvalue, exminutes) {
  var d = new Date();
  d.setTime(d.getTime() + (exminutes*60*1000));
  var expires = "expires="+ d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
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

function doGetRequest(request_url, request_port, request_path){
    $.ajax({
          type: "GET",
          url: 'https://' + request_url + ':' + request_port + request_path,
          success: getRequestSuccess,
          error: getRequestError,
          beforeSend: function (xhr) {
            xhr.setRequestHeader('Authorization', 'OpenTera ' + getCookie('BureauActifToken'));
            }
        });
}

function getRequestSuccess(response, status, request){
    console.log("getRequestSuccess: " + JSON.stringify(response));
}

function getRequestError(event, status){
    console.log("getRequestError: " + status.status + " : " + status.responseText);
}