let timerId = -1;
let timeout = 0;
let loaded = false;

function loginParticipant(){
    document.getElementById('mainview').src = "participant_localview?token=" + participant_token + "&source=" +
        clientSource;
    $('#mainview').on('load', function() {
        if (ws === undefined && !loaded){
            // No websocket connection - login participant
            console.log("Mainview loaded - login participant...")
            loaded = true;
            doParticipantLogin(backend_hostname, backend_port, participant_token);
        }
    });

}

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

                // Set flag to indicate participant login
                sessionStorage.setItem("is_participant", true);

                // Set token
                sessionStorage.setItem("participant_token", participant_token)

                // Clear timer
                clearInterval(timerId);
                timerId=-1;

                console.log("websocket_url", response['websocket_url'])
                if (response['websocket_url'])
                {
                    // Get websocket url
                    sessionStorage.setItem("websocket_url", response["websocket_url"]);

                    // Connect websocket
                    webSocketConnect();
                }
                else
                {
                    console.log("Will call doParticipantForcedLogout");
                    // Token is stored, this will have the effect of disconnecting the websocket
                    // from another login attempt
                    doParticipantForcedLogout(backend_url, backend_port);
                }
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
		sessionStorage.getItem("participant_token") + "&error=" + str_cant_connect + ". " +
		str_cant_connect_reasons + ".";
}

function doParticipantLogout(backend_url, backend_port){
    // Important: OpenTera.js must be included for this to work.
    doGetRequest(backend_url, backend_port, '/api/participant/logout', sessionStorage.getItem('participant_token'),
    participantLogoutSuccess, participantLogoutError);
}

function doParticipantForcedLogout(backend_url, backend_port){
    // Important: OpenTera.js must be included for this to work.
    doGetRequest(backend_url, backend_port, '/api/participant/logout', sessionStorage.getItem('participant_token'),
    participantForcedLogoutSuccess, participantForcedLogoutSuccess);
}

function participantForcedLogoutSuccess(response, status, request){
    // Will retry connecting
    window.location.replace("participant?token=" + sessionStorage.getItem("participant_token"));
}

function participantLogoutSuccess(response, status, request){
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

function participantLogoutError(event, status){
    console.log("Participant logoutError: " + status.status + " : " + status.responseText);
}