let timerId = -1;
let timeout = 0;

function doParticipantLogin(backend_url, backend_port, participant_token){
    timeout++;
	if (timerId === -1){
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

function loginParticipantError(event, status){
	clearInterval(timerId);
	timerId=-1;
	//console.log("loginError: " + status.status + " : " + status.responseText + " / " + status.statusText);

	// Redirect to error page
	document.getElementById('mainview').src = "participant_error?token=" +
		sessionStorage.getItem("participant_token") + "&error=Impossible de se connecter. " +
		"Votre accès est peut-être désactivé ou vous êtes déjà connecté sur un autre appareil.";
}

function doLogout(backend_url, backend_port){
    // Important: OpenTera.js must be included for this to work.
    // TODO Handle participant logout as well
    doGetRequest(backend_url, backend_port, '/api/user/logout', logoutSuccess, logoutError);
}

function logoutSuccess(response, status, request){
    // Redirect to login page
    /*if (sessionStorage.getItem("is_participant") === "false")
    {
        window.location.replace("login");
    }
    else
    {*/
        window.location.replace("participant_endpoint?token=" + sessionStorage.getItem("participant_token"));
    //}
}

function logoutError(event, status){
    console.log("logoutError: " + status.status + " : " + status.responseText);
}