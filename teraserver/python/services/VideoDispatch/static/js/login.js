var timerId = -1;
var timeout = 0;

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

function loginReply(response, status, request){
	// request.statusCode().status // Status code

	if (request.statusCode().status == 200){
		$('#txtmessage').text('Bienvenue!');
		$('#messages').css('display','block');
		$('#txtmessage').css('color','green');
		clearInterval(timerId);
		timerId=-1;
		// Set cookie with the access token for 30 minutes
        setCookie("VideoDispatchToken", response["user_token"], 30);

		// Redirect to location
		window.location.replace("/index");
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
	console.log("loginError: " + status.status + " : " + status.responseText);
	$('#txtmessage').css('color','red');
	$('#txtmessage').text(status.responseText);
	$('#messages').css('display','block');
	//$("#loginform :input").prop("disabled", false);
}

