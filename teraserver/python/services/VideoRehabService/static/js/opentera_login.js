var timerId = -1;
var timeout = 0;

function doLogin(backend_url, backend_port){
	timeout++;
	if (timerId == -1){
		$.ajaxSetup({
		  global: true
		});
		$(document).ajaxError(loginError);
		// Validate inputs
		if (!validateInput('#name') || !validateInput('#password'))
			return;

		// Start login result connect timer
		timerId = setInterval(doLogin, 1000);

		timeout=0;

	}

	// Enable form (since serialize() won't work on disabled forms)
	$("#loginform :input").prop("disabled", false);

	if (timeout < 10){

		// Send AJAX POST query
		$.ajax({
          type: "GET",
          url: 'https://' + backend_url + ':' + backend_port + '/api/user/login',
          success: loginReply,
          beforeSend: function (xhr) {
            xhr.setRequestHeader('Authorization', 'Basic ' + btoa($('#name').val() + ':' + $('#password').val()));
            }
        });
		//$.post('https://' + $('#name').val() + ':' + $('#password').val() + '@localhost:4040/api/user/login', $('#loginform').serialize(), loginReply);

		// Disable form
		//$("#loginform :input").prop("disabled", true);
	}else{
		$('#txtmessage').css('color','red');
		clearInterval(timerId);
		timerId=-1;
		$('#txtmessage').text('Impossible de rejoindre le serveur.');
	}

}

function doParticipantLogin(backend_url, backend_port, participant_token){
    timeout++;
	if (timerId == -1){
		$.ajaxSetup({
		  global: true
		});
		$(document).ajaxError(loginParticipantError);

		// Start login result connect timer
		timerId = setInterval(doParticipantLogin, 1000);
		timeout=0;
	}

	if (timeout < 10){

		// Send AJAX POST query
		$.ajax({
          type: "GET",
          url: 'https://' + backend_url + ':' + backend_port + '/api/participant/login',
          success: function(response, status, request){
                clearInterval(timerId);
                timerId=-1;

                // Get websocket url
                sessionStorage.setItem("websocket_url", response["websocket_url"]);

                // Set flag to indicate participant login
                sessionStorage.setItem("is_participant", true);

                // Set token
                sessionStorage.setItem("participant_token", participant_token)

                // Connect websocket
                webSocketConnect();
            },
          beforeSend: function (xhr) {
            xhr.setRequestHeader('Authorization', 'OpenTera ' + participant_token);
            }
        });
		//$.post('https://' + $('#name').val() + ':' + $('#password').val() + '@localhost:4040/api/user/login', $('#loginform').serialize(), loginReply);

		// Disable form
		//$("#loginform :input").prop("disabled", true);
	}else{
		clearInterval(timerId);
		timerId=-1;
	}
}

function loginReply(response, status, request){
	// request.statusCode().status // Status code

	if (request.statusCode().status == 200){
		$('#txtmessage').text('Bienvenue!');
		$('#messages').css('display','block');
		$('#txtmessage').css('color','green');
		clearInterval(timerId);
		timerId=-1;

        // Get websocket url
        sessionStorage.setItem("websocket_url", response["websocket_url"]);

        // Set flag to indicate participant login
        sessionStorage.setItem("is_participant", false);

  		// Redirect to location
		window.location.replace("dashboard");
	}else{
		//clearInterval(timerId);
		console.log("loginReply: " + response);
		$('#txtmessage').text(response);
		$('#messages').css('display','block');
		$('#txtmessage').css('color','');
	}
}

function loginError(event, status){
	clearInterval(timerId);
	timerId=-1;
	console.log("loginError: " + status.status + " : " + status.responseText + " / " + status.statusText);
	$('#txtmessage').css('color','red');
	$('#txtmessage').text(status.responseText);
	$('#messages').css('display','block');
	//$("#loginform :input").prop("disabled", false);
}

function loginParticipantError(event, status){
	clearInterval(timerId);
	timerId=-1;
	console.log("loginError: " + status.status + " : " + status.responseText + " / " + status.statusText);
}

function doLogout(backend_url, backend_port){
    // Important: OpenTera.js must be included for this to work.
    // TODO Handle participant logout as well
    doGetRequest(backend_url, backend_port, '/api/user/logout', logoutSuccess, logoutError);
}

function logoutSuccess(response, status, request){
    // Redirect to login page
    if (sessionStorage.getItem("is_participant") == "false")
    {
        window.location.replace("login");
    }
    else
    {
        window.location.replace("participant_endpoint?token=" + sessionStorage.getItem("participant_token"));
    }
}

function logoutError(event, status){
    console.log("logoutError: " + status.status + " : " + status.responseText);
}