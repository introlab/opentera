function connectToNextParticipant(service_hostname, service_port){
    doGetRequest(service_hostname, service_port, '/videodispatch/api/videodispatch/sessiondispatch', connectSuccess, connectError);
}

function connectSuccess(response, status, request){
    console.log("Starting videoconferencing session with " + response['participant_name'] + " at " +
    response['session_url']);
}

function connectError(event, status){
    console.error("connectError: " + event.status + " : " + event.responseText);

}