
function validateInput(inputId){
	var rval = ($(inputId).val() != "");
	if (!rval){
		$(inputId).css('background-color','#e05c5c');
		$(inputId).css('color','black');
	}else{
		$(inputId).css('background-color','');
		$(inputId).css('color','');
	}

	return rval;
}

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

function doGetRequest(request_url, request_port, request_path, success_response, error_response, scheme){
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
            if (sessionStorage.getItem("is_participant") === false)
                xhr.setRequestHeader('Authorization', 'OpenTera ' + getCookie('VideoDispatchToken'));
            else
                xhr.setRequestHeader('Authorization', 'OpenTera ' + getCookie('VideoDispatchTokenParticipant'));
            }
        });

     // Refresh cookies
     /*if (getCookie('VideoDispatchToken'))
        setCookie('VideoDispatchToken', getCookie('VideoDispatchToken', 30));
     if (getCookie('VideoDispatchTokenParticipant'))
        setCookie('VideoDispatchTokenParticipant', getCookie('VideoDispatchTokenParticipant', 30));*/
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