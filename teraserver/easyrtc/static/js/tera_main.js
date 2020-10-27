let isWeb = true;

function preInitSystem(){
    console.log("Pre-initializing system...");
    let urlParams = new URLSearchParams(window.location.search);
    let sourceParam = urlParams.get('source');
    if (sourceParam !== null)
        isWeb = (sourceParam === 'web');

    if (isWeb === false) {
        // Load QWebChannel library
        include("qrc:///qtwebchannel/qwebchannel.js");
    }

}

function initSystem(){
    console.log("Initializing system...");
    let urlParams = new URLSearchParams(window.location.search);
    let port = getTeraPlusPort(); // This function is rendered in the main html document
    let websocket_path =  "/websocket/" + port
    easyrtc.setSocketUrl(window.location.origin, {path: websocket_path});

    deviceEnumCompleted = false;

    let local_uuid = urlParams.get('uuid');
    if (local_uuid)
        localContact.uuid = local_uuid;

    let local_name = urlParams.get('name');
    if (local_name) {
        localContact.name = local_name;
        // Set names on local videos
        setTitle(true, 1, local_name);
        setTitle(true, 2, local_name);
    }

    // Initialize video and audio sources
    fillDefaultSourceList().then(initSystemDone).catch(err => {
        showStatusMsg("Impossible de continuer. Veuillez réessayer.")
    })
}

function initSystemDone(){

    if (isWeb){
        // Connect to signaling server
        connect();
    }else{
        // Connect Shared Object websocket, which will connect to system when ready
        connectSharedObject();
    }
}