var socketConnected = false;
var socketUrl = "";

function webSocketConnect(){

	if ("WebSocket" in window) {
	   if (socketUrl == "")
	        socketUrl = sessionStorage.getItem("websocket_url");
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

function ws_Closed(){
	document.getElementById("imgStatus").src="./static/images/red_button.png";

	console.log("Websocket closed.");

	// TODO: Manage reconnect, since the first URL will not be valid anymore...
	// Must make a new "login" request?
	/*
	// Retry to connect...
	WebSocketConnect();
	*/

	// Redirect to login for now...
	// window.location.replace("login");

}

function ws_MessageReceived(evt){
	var received_msg = evt.data;
    console.log("Websocket message: " + received_msg);
}