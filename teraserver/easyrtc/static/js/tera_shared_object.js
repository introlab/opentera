var SharedObject = undefined;
var teraConnected = false;
let socket = undefined;

var currentConfig = {'currentVideoSourceIndex': -1,
                        'currentAudioSourceIndex': -1,
                        'currentVideoSource2Index': -1,
                        'currentAudioSource2Index': -1,
                        'video1Mirror': true,
                        'video1Blur': false,
                        'screenAudio': false};

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
        SharedObject.setPageReady();
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
    if (channel.objects.SharedObject.setLocalBlurSignal !== undefined)
        channel.objects.SharedObject.setLocalBlurSignal.connect(setLocalBlur);

    if (channel.objects.SharedObject.videoSourceRemoved !== undefined)
        channel.objects.SharedObject.videoSourceRemoved.connect(removeVideoSource);
    if (channel.objects.SharedObject.startRecordingRequested !== undefined)
        channel.objects.SharedObject.startRecordingRequested.connect(startRecordingRequest);
    if (channel.objects.SharedObject.stopRecordingRequested !== undefined)
        channel.objects.SharedObject.stopRecordingRequested.connect(stopRecordingRequest);
    if (channel.objects.SharedObject.pauseRecordingRequested !== undefined)
        channel.objects.SharedObject.pauseRecordingRequested.connect(pauseRecordingRequest);

    //Request settings from client
    channel.objects.SharedObject.getAllSettings(function(settings) {
        settings = JSON.parse(settings);
        // console.log(settings);
        updateContact(settings.contactInfo);
        selectAudioSource(settings.audio);
        selectVideoSource(settings.video);
        setLocalMirror(settings.mirror);
        if (settings.blur !== undefined)
            setLocalBlur(settings.blur);
        selectSecondarySources(settings.secondAudioVideo);
        ptz = JSON.parse(settings.ptz);
        setPTZCapabilities(localContact.uuid, ptz.zoom, ptz.presets, ptz.settings, ptz.camera);
        if (settings.screenControl !== undefined){
            setCapabilities("0", localCapabilities.video2, settings.screenControl, true);
        }

        // Connect to signaling server now that we got all the settings
        connect();
    });
}

function updateContact(contact)
{
    //Contact should be a JSON object
    console.log("Update contact : " + contact);
    let receivedContact = JSON.parse(contact);
    localContact = {...localContact, ...receivedContact}; // Merge values
    //localContact.peerid = local_peerid;

    localPTZCapabilities.uuid = localContact.uuid;
    setTitle(true, 1, localContact.name);
    setTitle(true, 2, localContact.name);
}

function setLocalMirror(mirror){
    setMirror(mirror, true, 1);
}

function setLocalBlur(blur_value){
    console.log("setLocalBlur = " + blur_value);
    currentConfig["video1Blur"] = blur_value;
}

function startRecordingRequest(){
    if (!streamRecorder)
        streamRecorder = new TeraVideoRecorder();

    streamRecorder.startRecording();
    setRecordingStatus(true,1,true);
    broadcastRecordingStatus(true);
}

function stopRecordingRequest(){
    if (!streamRecorder)
        return;

    streamRecorder.stopRecording();
    streamRecorder = null;
    setRecordingStatus(true,1,false);
    broadcastRecordingStatus(false);
}

function pauseRecordingRequest(){
    if (!streamRecorder)
        return;

    streamRecorder.pauseRecording();
    let isPaused = streamRecorder.paused;
    setRecordingStatus(true,1,!isPaused);
    broadcastRecordingStatus(!isPaused);

}
