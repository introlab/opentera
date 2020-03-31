var service_hostname;
var service_port;

function init_dashboard(serv_hostname, serv_port){
    service_hostname = serv_hostname;
    service_port = serv_port;
    setInterval(updateStatus, 5000);
    updateStatus();
}

function connectToNextParticipant(){
    doGetRequest(service_hostname, service_port, '/videodispatch/api/videodispatch/sessiondispatch', connectSuccess, connectError);
}

function connectSuccess(response, status, request){
    if (response['session_url'] !== undefined){
        console.log("Starting videoconferencing session with " + response['participant_name'] + " at " +
        response['session_url']);
        window.location.replace(response['session_url']);
    }else{
        console.log('No participant waiting!');
    }
}

function connectError(event, status){
    console.error("connectError: " + event.status + " : " + event.responseText);

}

function updateStatus(){
    console.log("Updating status...");
    doGetRequest(service_hostname, service_port, '/videodispatch/api/videodispatch/status', statusSuccess);
}

function statusSuccess(response, status, request){
    // console.log(response);
    if (response['online_count'] !== undefined){
        document.getElementById('lblOnlineCount').innerHTML = response['online_count'];
        document.getElementById('lblInSessionCount').innerHTML = response['in_session_count'];
        document.getElementById('lblDoneCount').innerHTML = response['done_count'];

         document.getElementById('btnConnect').disabled = (response['online_count'] === 0);
    }else{
        if (response['rank'] !== undefined){
            if (response['rank'] < 1){
                response['rank'] = 1000;
            }
            document.getElementById('lblRank').innerHTML = response['rank'];
        }
    }
}