let timerId = -1;
let timeout = 0;

function loginUser(){
    /*document.getElementById('mainview').src = "user_localview?token=" + user_token + "&source=" +
        clientSource;
    $('#mainview').on('load', function() {
        if (ws === undefined){
            // No websocket connection - login user
            console.log("Mainview loaded - login user...")
            doUserLogin(backend_hostname, backend_port, user_token);
        }
    });*/
    console.warn("loginUser: not implemented yet.");

}

function doUserLogin(backend_url, backend_port, user_token){
    timeout++;
	if (timerId === -1){
		$.ajaxSetup({
		  global: true
		});
		$(document).ajaxError(loginUserError);

		// Start login result connect timer
		timerId = setInterval(doUserLogin, 1000);
		timeout=0;
	}

	if (timeout < 10){

		// Send AJAX POST query
		$.ajax({
          	type: "GET",
          	url: 'https://' + backend_url + ':' + backend_port + '/api/user/login',
          	success: function(response, status, request){
                clearInterval(timerId);
                timerId=-1;

                // Get websocket url
                sessionStorage.setItem("websocket_url", response["websocket_url"]);

                // Set flag to indicate user login
                sessionStorage.setItem("is_user", true);

                // Set token
                sessionStorage.setItem("user_token", user_token)

                // Connect websocket
                webSocketConnect();
            },
          beforeSend: function (xhr) {
            xhr.setRequestHeader('Authorization', 'OpenTera ' + user_token);
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

function loginUserError(event, status){
	clearInterval(timerId);
	timerId=-1;
	//console.log("loginError: " + status.status + " : " + status.responseText + " / " + status.statusText);

	// Redirect to error page
	document.getElementById('mainview').src = "user_error?token=" +
		sessionStorage.getItem("user_token") + "&error=" + str_cant_connect + ". " +
		str_cant_connect_reasons + ".";
}

function doUserLogout(backend_url, backend_port){
    // Important: OpenTera.js must be included for this to work.
    doGetRequest(backend_url, backend_port, '/api/user/logout', userLogoutSuccess, userLogoutError);
}

function userLogoutSuccess(response, status, request){
    // Redirect to login page
    /*if (sessionStorage.getItem("is_participant") === "false")
    {
        window.location.replace("login");
    }
    else
    {*/
        window.location.replace("user_endpoint?token=" + sessionStorage.getItem("user_token"));
    //}
}

function participantLogoutError(event, status){
    console.log("User logoutError: " + status.status + " : " + status.responseText);
}