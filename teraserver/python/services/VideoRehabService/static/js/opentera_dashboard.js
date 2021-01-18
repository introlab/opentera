var service_hostname;
var service_port;

var current_session_url;

function init_dashboard(serv_hostname, serv_port){
    service_hostname = serv_hostname;
    service_port = serv_port;
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
                    error
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
