var service_hostname;
var service_port;

var current_session_key;
var current_session_url;

function init_dashboard(serv_hostname, serv_port){
    service_hostname = serv_hostname;
    service_port = serv_port;
}

function startStatusUpdates(){
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
        current_session_key = response['session_key'];
        current_session_url = response['session_url'];
        window.parent.document.getElementById('btnLogout').style.display="none";
        window.parent.document.getElementById('btnStopSession').style.display="inline";
        window.parent.document.getElementById('btnStopSession').name = response['session_key'];

        //window.location.replace(response['session_url']);
        window.parent.document.getElementById('mainview').contentWindow.document.getElementById("lblParticipantName").innerHTML = response['participant_name'];
        window.parent.document.getElementById('mainview').contentWindow.document.getElementById("dialogWait").style.display="inline";

        testCurrentSessionUrlValid();

    }else{
        console.log('No participant waiting!');
    }
}

function connectError(event, status){
    console.error("connectError: " + event.status + " : " + event.responseText);

}


var sessionUrlTries = 0;
function testCurrentSessionUrlValid(){
    //console.log("testCurrentSessionUrlValid");
    var request = new XMLHttpRequest();
    request.open('GET', current_session_url, true);
    request.onreadystatechange = function(){
        if (request.readyState === 4){
            if (request.status != 200) {
                // Not started yet... try again...
                sessionUrlTries++;
                if (sessionUrlTries >= 12){
                    window.parent.document.getElementById('mainview').contentWindow.document.getElementById("dialogWait").style.display="none";
                    alert("Error - Can't start session!");
                }else{
                    setTimeout(testCurrentSessionUrlValid, 250);
                }
            }else{
                sessionUrlTries = 0;
                if (sessionStorage.getItem("is_participant") == "false")
                    window.location.replace(current_session_url);
                else
                    document.getElementById('mainview').src = current_session_url;
            }
        }
    };
    request.send();
}

function updateStatus(){
    //console.log("Updating status...");
    doGetRequest(service_hostname, service_port, '/videodispatch/api/videodispatch/status', statusSuccess);
}

function statusSuccess(response, status, request){
    //console.log(response);
    if (response['online_count'] !== undefined){
        document.getElementById('lblOnlineCount').innerHTML = response['online_count'];
        document.getElementById('lblInSessionCount').innerHTML = response['in_session_count'];
        document.getElementById('lblDoneCount').innerHTML = response['done_count'];

         document.getElementById('btnConnect').disabled = (response['online_count'] === 0);
    }else{
        if (response['rank'] !== undefined){
            if (response['rank'] < 1){
                hideElement('cardRank');
            }else{
                document.getElementById('cardRank').style.display="block";
            }
            document.getElementById('lblRank').innerHTML = response['rank'];
        }
    }
}

function doStopCurrentSession(session_key){
    if (session_key === undefined)
        session_key = current_session_key;

    if (session_key !== undefined){
        doGetRequest(service_hostname, service_port, '/videodispatch/api/videodispatch/sessionmanage?session_key=' +
        session_key + "&session_stop=true", sessionStopSuccess);
    }else{
        console.error('No session to stop!');
        window.parent.document.getElementById('btnLogout').style.display="inline";
        window.parent.document.getElementById('btnStopSession').style.display="none";
    }
}

function sessionStopSuccess(response, status, request){
    if (response == 200){
        window.parent.document.getElementById('btnLogout').style.display="inline";
        window.parent.document.getElementById('btnStopSession').style.display="none";
        current_session_key = undefined;
        current_session_url = undefined;
        top.mainview.src = 'dashboard_main';
    }
}

function hideMainViewElement(element_id){
    document.getElementById('mainview').contentWindow.document.getElementById(element_id).style.display='none';
}

function showMainViewElement(element_id){
    document.getElementById('mainview').contentWindow.document.getElementById(element_id).style.display='inline';
}
