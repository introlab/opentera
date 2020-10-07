var SharedObject = undefined;
var teraConnected = false;
let socket = undefined;

var currentConfig = {'currentVideoSourceIndex': -1,
                     'currentAudioSourceIndex': -1,
                     'currentVideoSource2Index':-1,
                     'currentAudioSource2Index':-1,
                     'video1Mirror': true};

function connectSharedObject() {
    let baseUrl = "ws://localhost:12345";
    console.log("Connecting SharedObject socket at " + baseUrl + ".");
    socket = new WebSocket(baseUrl);

    socket.onclose = sharedObjectSocketClosed;
    socket.onerror = sharedObjectSocketError;
    socket.onopen = sharedObjectSocketOpened;
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

    //Request contact info...
    channel.objects.SharedObject.getContactInformation();

    // Request current audio source
    channel.objects.SharedObject.getCurrentAudioSource();

    // Request current camera
    channel.objects.SharedObject.getCurrentVideoSource();

    // Request secondary sources
    channel.objects.SharedObject.getSecondSources();

    // Mirror effect
    if (channel.objects.SharedObject.getLocalMirror){
        channel.objects.SharedObject.setLocalMirrorSignal.connect(setLocalMirror);
        channel.objects.SharedObject.getLocalMirror();
    }else
        console.log("No mirror settings.");

}

function updateContact(contact)
{
    //Contact should be a JSON object
    console.log("Update contact : " + contact);
    localContact = JSON.parse(contact);
    //localContact.peerid = local_peerid;

    localPTZCapabilities.uuid = localContact.uuid;
    setTitle(local, 1, localContact.name);
    setTitle(local, 2, localContact.name);
}

function setLocalMirror(mirror){
    setMirror(mirror, true, 1);
}