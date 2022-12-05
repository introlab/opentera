let socketUrl = "";
let ws = undefined;

function webSocketConnect(){
	if ("WebSocket" in window) {
	   if (socketUrl === "")
	        socketUrl = sessionStorage.getItem("websocket_url");

	   if (!socketUrl){
            console.error('No websocket url - redirecting to login.')
            window.location.replace("login");
            return;
	   }
	   console.log("Opening websocket at " + socketUrl);
	   ws = new WebSocket(socketUrl);

	   ws.onopen = ws_Opened;
	   ws.onmessage = ws_MessageReceived;
	   ws.onclose = ws_Closed;
	   ws.onerror = ws_Error;

	} else {
	  document.getElementById("imgStatus").src="./static/images/red_button.png";
	   // The browser doesn't support WebSocket
	   alert("WebSocket NOT supported by your Browser!");
	}

}

function ws_Opened(){
    console.log("Websocket opened");
	document.getElementById("imgStatus").src="./static/images/green_button.png";
	sessionStorage.removeItem("websocket_url");
}

function ws_Error(error){
	console.error('Websocket Error: ' + JSON.stringify(error));
}

function ws_Closed(event){
	document.getElementById("imgStatus").src="./static/images/red_button.png";

	console.log("Websocket closed.", event);

    // Close forced by server, will not login
    if (event.code !== 4000)
    {
        // Must make a new "login" request?
        // Retry to connect in 2 seconds...
        setTimeout(function(){ doParticipantLogin(backend_hostname, backend_port, participant_token); }, 2000);

        // Redirect to login for now...
        //window.location.replace("login");
    }
    else {
        window.location.replace("participant_endpoint?token=" + sessionStorage.getItem("participant_token"));
    }
}

function ws_MessageReceived(evt){
	let received_msg = evt.data;
    console.log("Websocket message: " + received_msg);

    let json_msg = JSON.parse(received_msg);

    let msg_type = json_msg.message.events[0]["@type"];

    // Join session
    if (msg_type === "type.googleapis.com/opentera.protobuf.JoinSessionEvent"){
        hideElement('btnLogout');
        hideElement('logos');
        $('#mainview').removeClass('iframe-with-footer');
        $('#mainview').addClass('iframe-without-footer');
        // Join video session event - redirect to session url
        showMainViewElement("dialogWait");
        hideMainViewElement("messages");
        current_session_url = json_msg.message.events[0]["sessionUrl"];
        // Append name and uuid
        current_session_url += "&name=" + participant_name.replace("#", "") + "&uuid=" + participant_uuid;

        // Append source if available
        current_session_url += "&source=" + clientSource;

        console.log ("About to join session: " + current_session_url)
        setTimeout(waitDialogTimeout, 3000);
    }

    // Stop or leave session
    if (msg_type === "type.googleapis.com/opentera.protobuf.StopSessionEvent" ||
    (msg_type === "type.googleapis.com/opentera.protobuf.LeaveSessionEvent") &&
    json_msg.message.events[0]["leavingParticipants"].includes(participant_uuid))
    {
        if (clientSource === "web")
            showElement('btnLogout');
        showElement('logos');
        $('#mainview').removeClass('iframe-with-footer');
        $('#mainview').addClass('iframe-without-footer');
        //window.location.replace("participant_endpoint?token=" + sessionStorage.getItem("participant_token"));
        document.getElementById('mainview').src = "participant_localview?token=" + sessionStorage.getItem("participant_token") +
        "&message=" + str_session_complete + ".&message_type=light&source=" + clientSource;
    }
}

function waitDialogTimeout(){
    console.log("Joining session now!");
    joinSession();
}