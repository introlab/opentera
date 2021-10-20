let timerId = -1;
let timeout = 0;

function loginParticipant(){
    document.getElementById('mainview').src = "participant_localview?token=" + participant_token + "&source=" +
        clientSource;
    $('#mainview').on('load', function() {
        if (ws === undefined){
            // No websocket connection - login participant
            console.log("Mainview loaded - login participant...")
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
		sessionStorage.getItem("participant_token") + "&error=" + str_cant_connect + ". " +
		str_cant_connect_reasons + ".";
}

function doParticipantLogout(backend_url, backend_port){
    // Important: OpenTera.js must be included for this to work.
    doGetRequest(backend_url, backend_port, '/api/participant/logout', participantLogoutSuccess, participantLogoutError);
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