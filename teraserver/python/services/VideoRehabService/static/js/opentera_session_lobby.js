function startSession(backend_url, backend_port, token, session_uuid){
    data = {"session_manage": {
        "action": "start",
        "session_uuid": session_uuid
    }};

    console.log('Starting session ' + session_uuid + '...');

    doPostRequest(backend_url, backend_port, '/api/user/sessions/manager', token, JSON.stringify(data),
    startSessionSuccess, startSessionError);
}

function startSessionSuccess(response, status, request){
    console.log('Session about to start...');
    showElement('dialogWait');
}

function startSessionError(event, status){
    console.error("startSession error: " + event.statusText);
}