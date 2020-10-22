var SharedObject = undefined;
var teraConnected = false;
let socket = undefined;

var currentConfig = {'currentVideoSourceIndex': -1,
                     'currentAudioSourceIndex': -1,
                     'currentVideoSource2Index': -1,
                     'currentAudioSource2Index': -1,
                     'video1Mirror': true};

function connectSharedObject() {
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
    });
    teraConnected = true;
}

function setupSharedObjectCallbacks(channel){

    //connect to a signal
    channel.objects.SharedObject.newContactInformation.connect(updateContact);
    channel.objects.SharedObject.newVideoSource.connect(selectVideoSource);
    channel.objects.SharedObject.newAudioSource.connect(selectAudioSource);
    channel.objects.SharedObject.newDataForward.connect(forwardData);
    channel.objects.SharedObject.newSecondSources.connect(selectSecondarySources);
    channel.objects.SharedObject.setLocalMirrorSignal.connect(setLocalMirror);

    //Request settings from client
    channel.objects.SharedObject.getAllSettings(function(settings) {
        settings = JSON.parse(settings);
        //console.log(settings);
        updateContact(settings.contactInfo);
        selectAudioSource(settings.audio);
        selectVideoSource(settings.video);
        setLocalMirror(settings.mirror);
        selectSecondarySources(settings.secondAudioVideo);
        ptz = JSON.parse(settings.ptz);
        setPTZCapabilities(localContact.uuid, ptz.zoom, ptz.presets, ptz.settings);

        // Connect to signaling server now that we got all the settings
        connect();
    });
}

function updateContact(contact)
{
    //Contact should be a JSON object
    console.log("Update contact : " + contact);
    localContact = JSON.parse(contact);
    //localContact.peerid = local_peerid;

    localPTZCapabilities.uuid = localContact.uuid;
    setTitle(true, 1, localContact.name);
    setTitle(true, 2, localContact.name);
}

function setLocalMirror(mirror){
    setMirror(mirror, true, 1);
}