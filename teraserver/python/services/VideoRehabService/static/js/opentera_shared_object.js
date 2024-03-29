var SharedObject = undefined;
var teraConnected = false;
let socket = undefined;
let connected_callback = undefined;

function connectSharedObject(callback) {
    connected_callback = callback
    let baseUrl = "ws://localhost:12345";
    console.log("Connecting SharedObject socket at " + baseUrl + ".");
    socket = new WebSocket(baseUrl);
    socket.onopen = sharedObjectSocketOpened;
    socket.onerror = sharedObjectSocketError;
    socket.onclose = sharedObjectSocketClosed;
}
function sharedObjectSocketClosed(){
    showError("sharedObjectSocketClosed", "Shared object socket closed", false);
    teraConnected = false;
}

function sharedObjectSocketError(error){
    showError("sharedObjectSocketError", error, false);
}

function sharedObjectSocketOpened(){
    console.log("SharedObject socket connected.");

    new QWebChannel(socket, function(channel) {
        SharedObject = channel.objects.SharedObject;
        setupSharedObjectCallbacks(channel);
        SharedObject.setPageReady();
    });
    teraConnected = true;
}

function setupSharedObjectCallbacks(channel){

    //connect to a signal
    channel.objects.SharedObject.newContactInformation.connect(updateContact);
    //channel.objects.SharedObject.newVideoSource.connect(selectVideoSource);
    channel.objects.SharedObject.setLocalMirrorSignal.connect(setLocalMirror);

    /*if (channel.objects.SharedObject.videoSourceRemoved !== undefined)
        channel.objects.SharedObject.videoSourceRemoved.connect(removeVideoSource);*/

    //Request settings from client
    channel.objects.SharedObject.getAllSettings(function(settings) {
        settings = JSON.parse(settings);
        //console.log(settings);
        updateContact(settings.contactInfo);
        //selectAudioSource(settings.audio);
        let video = JSON.parse(settings.video);
        //selectVideoSource(video.name);
        currentConfig.currentVideoName = video.name;
        setLocalMirror(settings.mirror);
        //selectSecondarySources(settings.secondAudioVideo);
        let ptz = JSON.parse(settings.ptz);
        setPTZCapabilities(ptz.zoom, ptz.presets, ptz.settings, ptz.camera);

        // Call callback function when we got all the settings
        if (connected_callback !== undefined)
            connected_callback();
    });
}

function updateContact(contact)
{
    //Contact should be a JSON object
    console.log("Update contact : " + contact);
    localContact = JSON.parse(contact);
    //localContact.peerid = local_peerid;

    localPTZCapabilities.uuid = localContact.uuid;
    /*setTitle(true, 1, localContact.name);
    setTitle(true, 2, localContact.name);*/
}
