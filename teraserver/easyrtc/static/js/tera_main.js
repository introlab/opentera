function initSystem(){
    console.log("Initializing system...");
    let urlParams = new URLSearchParams(window.location.search);
    isWeb = (urlParams.get('source') === 'web');

    let port = getTeraPlusPort(); // This function is rendered in the main html document
    let websocket_path =  "/websocket/" + port
    easyrtc.setSocketUrl(window.location.origin, {path: websocket_path});

    deviceEnumCompleted = false;
    initialSourceSelect	=false;

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

    // Initialize
    if (!isWeb){
        // Connect Shared Object websocket
        include("qrc:///qtwebchannel/qwebchannel.js");
        connectSharedObject();
    }

    fillDefaultSourceList().then(connect).catch(err => {
        showStatusMsg("Impossible de continuer. Veuillez réessayer.")
    })
}