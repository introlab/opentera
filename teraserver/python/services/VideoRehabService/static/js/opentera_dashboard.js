let service_hostname;
let service_port;

let current_session_url;
let currentLang = 'fr';

let clientSource = 'web';

function init_dashboard(serv_hostname, serv_port){
    service_hostname = serv_hostname;
    service_port = serv_port;
}

function init_system(){
    if (isBrowserSupported()){
        // Check source
        let urlParams = new URLSearchParams(window.location.search);
        let sourceParam = urlParams.get('source');
        if (sourceParam !== null){
            clientSource = sourceParam;
            if (sourceParam === 'openteraplus'){
                // Connected to OpenTeraPlus - hide logout button
                hideElement('btnLogout');
            }
        }

        loginParticipant();
    }
    else{
        let browser_infos = browser.getBrowser().name + " " + browser.getBrowser().version;
        showError(str_unsupported_browser_title,str_unsupported_browser + ".<br><br><u>" + str_your_browser + "</u>: <strong>" + browser_infos +
            "</strong><br><br><u>" + str_supported_browsers + "</u>: <strong>Chrome (version 55+), Firefox (version 50+), Safari (version 11+)</strong>", true, false);
    }
}

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

let sessionUrlTries = 0;
function joinSession(){
    let request = new XMLHttpRequest();
    request.open('GET', current_session_url, true);
    request.onreadystatechange = function(){
        if (request.readyState === 4){
            if (request.status !== 200) {
                // Not started yet... try again...
                sessionUrlTries++;
                if (sessionUrlTries >= 12){
                    hideMainViewElement("dialogWait");
                }else{
                    setTimeout(joinSession, 250);
                }
            }else{
                sessionUrlTries = 0;
                document.getElementById('mainview').src = current_session_url;
            }
        }
    };
    request.send();
}

function hideMainViewElement(element_id){
    document.getElementById('mainview').contentWindow.document.getElementById(element_id).style.display='none';
}

function showMainViewElement(element_id){
    document.getElementById('mainview').contentWindow.document.getElementById(element_id).style.display='inline';
}
