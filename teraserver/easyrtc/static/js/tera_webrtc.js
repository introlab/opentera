// WebRTC ids
var local_peerid = "0";

// Contact cards
var localContact = {}; // {uuid, name, peerid, status}
var remoteContacts = []; // Used to store information about everyone that has connected (contactinfos)
                            // {uuid, name, peerid}
let remoteStreams = []; // {peerid, streamname, stream: MediaStream}, order is important as it is linked to each view!
let localStreams = []; // {peerid, streamname, stream: MediaStream}, order is important as it is linked to each local view!

// Status / controls variables
var connected = false;
var needToCallOtherUsers = false;

let preinitCameras = false;

function connect() {

    console.log("Connecting...");
    if (!preinitCameras)
        playSound("audioCalling");

    /*var localFilter = easyrtc.buildLocalSdpFilter( {
        audioRecvBitrate:20, videoRecvBitrate:30 ,videoRecvCodec:"h264"
    });
    var remoteFilter = easyrtc.buildRemoteSdpFilter({
        audioSendBitrate: 20, videoSendBitrate:30 ,videoSendCodec:"h264"
    });*/

    //easyrtc.setSdpFilters(localFilter, remoteFilter);

    //Pre-connect Event listeners
    easyrtc.setRoomOccupantListener(updateRoomUsers);
    easyrtc.setRoomEntryListener(function(/*entry, roomName*/) {
        needToCallOtherUsers = true;
    });
    easyrtc.setDisconnectListener(disconnectedFromSignalingServer);

    easyrtc.setStreamAcceptor(newStreamStarted);
    easyrtc.setOnStreamClosed(streamDisconnected);
    easyrtc.setPeerListener(dataReception);
    // easyrtc.debugPrinter =function (message){console.log('EASYRTC - ' + message);}

    //Post-connect Event listeners
    //easyrtc.setOnHangup(streamDisconnected);
    //easyrtc.setOnCall(newStreamStarted);
    if (preinitCameras)
        preloadCameras();
    else{
        connected = true;
        updateLocalAudioVideoSource(1);
        showLayout(true);
    }


}

// On some devices, there's a strange bug that delays access to the camera, unless we try to access it at least once...
function preloadCameras(){
    navigator.mediaDevices.enumerateDevices()
        .then(function(devices) {
            let preload_devices = [];
            devices.forEach(function(device) {
                if (device.kind === "videoinput"){
                    if (!device.label.includes(" IR ")) { // Filter "IR" camera, since they won't work.
                        preload_devices.push(device);
                    }
                }
                //console.log(device.kind + ": " + device.label + " id = " + device.deviceId);
            });
            preloadCamera(preload_devices, 0);
        })
        .catch(function(err) {
            console.log(err.name + ": " + err.message);
        });

}

function preloadCamera(devices, current_index){
    if (current_index >= devices.length || current_index < 0){
        return;
    }

    navigator.mediaDevices.getUserMedia({video: {deviceId: { exact: devices[current_index].deviceId }},
        audio: false}).then(async function(stream){
            console.log("Preloaded camera " + devices[current_index].label + "(" + devices[current_index].deviceId + ")");
            stream.getTracks().forEach(track => track.stop());
            // Did we get at least the first stream? If so, start everything!
            //if (current_index === 0){
            if (!connected){
                playSound("audioCalling");
                connected = true;
                updateLocalAudioVideoSource(1);
                showLayout(true);
            }
            preloadCamera(devices, current_index + 1);
    }).catch(async function(err) {
        console.log("Can't preload camera: " + devices[current_index].label + "(" + devices[current_index].deviceId + ") - " + err);
        //await new Promise(resolve => setTimeout(resolve, 5000));
        preloadCamera(devices, current_index+1);
    });
}

function muteMicro(local, index, new_state){
    if (new_state === undefined){ // Toggle is no state specified
        new_state = !isStatusIconActive(local, index, "Mic");
    }

    updateStatusIconState(new_state, local, index, "Mic");

    if (local === true){
        // Send display update request
        let request = {"peerid": local_peerid};
        if (index === 1)
            request.micro = new_state;
        else
            request.micro2 = new_state;

        easyrtc.enableMicrophone(new_state);  // Fix me: doesn't seem to work if specifying stream name....

        localContact.status.microMuted = !new_state;

        //console.log(request);
        if (easyrtc.webSocketConnected) {
            easyrtc.sendDataWS({targetRoom: "default"}, 'updateStatus', request,
                function (ackMesg) {
                if (ackMesg.msgType === 'error') {
                    console.error(ackMesg.msgData.errorText);
                }
            });
        }
    }else{
        // Request mute to someone else
        let request = {"micro": new_state, "index": 1}; // TODO: Manage multiple remote streams??
        if (easyrtc.webSocketConnected){
            easyrtc.sendDataWS( remoteStreams[index-1].peerid, 'muteMicro', request,
                function(ackMesg) {
                //console.error("ackMsg:",ackMesg);
                if( ackMesg.msgType === 'error' ) {
                    console.error(ackMesg.msgData.errorText);
                }
            });
        }
    }
}

function muteVideo(local, index, new_state){
    if (new_state === undefined) { // Toggle is no state specified
        new_state = !isStatusIconActive(local, index, "Video");
    }

    updateStatusIconState(new_state, local, index, "Video");

    if (local === true){
        // Send display update request
        let request = {"peerid": local_peerid, video: new_state};

        if (index <= localStreams.length){
            let videoTracks = localStreams[index-1].stream.getVideoTracks();
            for (let i=0; i<videoTracks.length; i++){
                videoTracks[i].enabled = new_state;
            }
        }else{
            showError("muteVideo", "Trying to mute video on a local stream not present: index = " + (index-1), false);
        }

        localContact.status.videoMuted = !new_state;

        if (easyrtc.webSocketConnected) {
            easyrtc.sendDataWS({targetRoom: "default"}, 'updateStatus', request,
                function (ackMesg) {
                    if (ackMesg.msgType === 'error') {
                        console.error(ackMesg.msgData.errorText);
                    }
                });
        }
    }else{
        // Request video mute to someone else
        let request = {video: new_state, "index": 1}; // TODO: Manage multiple remote streams??
        if (easyrtc.webSocketConnected){
            easyrtc.sendDataWS( remoteStreams[index-1].peerid, 'muteVideo', request,
                function(ackMesg) {
                    //console.error("ackMsg:",ackMesg);
                    if( ackMesg.msgType === 'error' ) {
                        console.error(ackMesg.msgData.errorText);
                    }
                });
        }
    }
}

function muteSpeaker(local, index, new_state){
    if (new_state === undefined) { // Toggle is no state specified
        new_state = !isStatusIconActive(local, index, "Speaker");
    }

    updateStatusIconState(new_state, local, index, "Speaker");

    if (local === true){
        // Send display update request
        let request = {"peerid": local_peerid, speaker: new_state};

        // Mute all remote streams
        for (let i=1; i<=maxRemoteSourceNum; i++){
            let video_widget = getVideoWidget(false, i);
            video_widget.prop('muted', !new_state);
        }

        for (let i=1; i<=remoteStreams.length; i++){
            let video_widget = getVideoWidget(false, i);
            if(new_state)
                video_widget[0].play(); // Make sure all videos are currently playing, useful when sharing music only
        }

        localContact.status.speakerMuted = !new_state;

        if (easyrtc.webSocketConnected) {
            easyrtc.sendDataWS({targetRoom: "default"}, 'updateStatus', request,
                function (ackMesg) {
                    if (ackMesg.msgType === 'error') {
                        console.error(ackMesg.msgData.errorText);
                    }
                });
        }
    }else{
        // Request speaker mute to someone else
        let request = { speaker: new_state, "index": 1}; // TODO: Manage multiple remote streams??
        if (easyrtc.webSocketConnected){
            easyrtc.sendDataWS( remoteStreams[index-1].peerid, 'muteSpeaker', request,
                function(ackMesg) {
                    //console.error("ackMsg:",ackMesg);
                    if( ackMesg.msgType === 'error' ) {
                        console.error(ackMesg.msgData.errorText);
                    }
                });
        }
    }
}

function setMirror(mirror, local, index){
    if (local === true){
        //console.log("setMirror: " + mirror + ", local=" + local + ", index=" + index);
        // Send display update request
        let request = {"peerid": local_peerid, mirror: mirror};

        showVideoMirror(true, index, mirror);

        if (easyrtc.webSocketConnected) {
            easyrtc.sendDataWS({targetRoom: "default"}, 'updateStatus', request,
                function (ackMesg) {
                    if (ackMesg.msgType === 'error') {
                        console.error(ackMesg.msgData.errorText);
                    }
                });
        }

        currentConfig["video" + index + "Mirror"] = mirror;
    }else{
        // Request mirror to someone else
        let request = {"index": 1, "mirror": mirror};
        if (easyrtc.webSocketConnected){
            easyrtc.sendDataWS(remoteStreams[index-1].peerid, 'setMirror', request,
                function(ackMesg) {
                    //console.error("ackMsg:",ackMesg);
                    if( ackMesg.msgType === 'error' ) {
                        console.error(ackMesg.msgData.errorText);
                    }
                });
        }
    }
}

function sendPrimaryView(peer_id, streamname){
    console.log('sendPrimaryView - peer: ' + peer_id + ', stream: ' + streamname);
    primaryView = {peerid: peer_id, streamName: streamname};

    let request = primaryView;
    if (easyrtc.webSocketConnected){
        easyrtc.sendDataWS({targetRoom: "default"}, 'setPrimaryView', request,
            function (ackMesg) {
                if (ackMesg.msgType === 'error') {
                    console.error(ackMesg.msgData.errorText);
                }
            });
    }
}

function setPrimaryView(peer_id, streamname){
    console.log('setPrimaryView - peer: ' + peer_id + ', stream: ' + streamname);
    primaryView = {peerid: peer_id, streamName: streamname};
    if (isParticipant){
        let index = undefined;
        if (primaryView.peerid !== 0){
            if (peer_id !== local_peerid)
                index = getStreamIndexForPeerId(primaryView.peerid, primaryView.streamName);
            else{
                // Local view is primary view - don't do anything!
                index = getLocalStreamIndex(primaryView.streamName);
                enlargeView(true, index+1);
                setPrimaryViewIcon(primaryView.peerid, primaryView.streamName);
                return;
            }
        }

        if (index !== undefined){
            let local = (primaryView.peerid === local_peerid);
            let view_id = getVideoViewId(local, index+1);
            setLargeView(view_id);
        }else{
            // Defaults to first remote user view
            let view_id = getFirstRemoteUserVideoViewId();
            if (view_id === undefined)
                view_id = "remoteView1";
            setLargeView(view_id);
        }
    }
    setPrimaryViewIcon(primaryView.peerid, primaryView.streamName);
}

async function updateLocalAudioVideoSource(streamindex){
    if (connected === true){
        let streamname = "localStream" + streamindex;
        if (streamindex === 1) // Default stream = no name.
            streamname = "";
        if (streamindex <= localStreams.length){
            console.log("Updating audio/video source: " + streamname);
            // Stopping previous stream
            localStreams[streamindex-1].stream.getTracks().forEach(track => track.stop());
        }else {
            console.log("Creating audio/video source: " + streamname);
        }

        // TODO: If using defaults, add constraints for "front" facing
        easyrtc._presetMediaConstraints={audio:{
                deviceId: {
                    exact: audioSources[currentConfig.currentAudioSourceIndex].deviceId
                }},
            video: {
                deviceId: {
                    exact: videoSources[currentConfig.currentVideoSourceIndex].deviceId
                }}
        }
        let microMute = false;
        if (localContact && localContact.status && localContact.status.microMuted){
            microMute = localContact.status.microMuted;
        }
        easyrtc.enableAudio(!microMute);
        easyrtc.enableVideo(true);

        // Disable all tracks before creating, if needed
        if (streamindex <= localStreams.length){
            let stream = localStreams[streamindex-1].stream;
            enableAllTracks(stream, false);
        }

        easyrtc.initMediaSource(
            localVideoStreamSuccess,
            localVideoStreamError,
            streamname);

        broadcastlocalPTZCapabilities();
    }else{
        console.log("Updated audio/video source - not connected, selection will take effect when connected.");
    }

    // Update PTZ status if needed
    showPTZControls(true, 1, localPTZCapabilities.zoom, localPTZCapabilities.presets,
        localPTZCapabilities.settings, localPTZCapabilities.camera);

}

function localVideoStreamSuccess(stream){
    console.log("Got local video stream - " + stream.streamName);
    if (stream.active){
        let local_index = -1;
        for (let i=0; i<localStreams.length; i++){
            if (localStreams[i].streamname === stream.streamName){
                local_index = i;
                break;
            }
        }
        let infos = {'peerid': local_peerid, 'streamname': stream.streamName, 'stream': stream};
        if (local_index>=0){
            // Existing stream
            localStreams[local_index] = infos;
            console.log("Existing stream - updating...");
            let videoTrack = stream.getVideoTracks()[0];
            let audioTrack = stream.getAudioTracks()[0];
            for (let i=0; i<remoteStreams.length; i++){
                let pc = easyrtc.getPeerConnectionByUserId(remoteStreams[i].peerid);
                let video_sender = pc.getSenders().find(function(s) {
                    if (s.track)
                        return s.track.kind === videoTrack.kind;
                    return undefined;
                });
                let audio_sender = pc.getSenders().find(function(s) {
                    if (s.track)
                        return s.track.kind === audioTrack.kind;
                    return undefined;
                });
                if (video_sender !== undefined){
                    video_sender.replaceTrack(videoTrack);
                }else{
                    console.log("No sender for video track found...");

                }
                if (audio_sender !== undefined) {
                    audio_sender.replaceTrack(audioTrack);
                }else{
                    console.log("No sender for audio track found...");
                }
                if (audio_sender === undefined || video_sender === undefined){
                    // Must re-add the stream to the call!
                    easyrtc.addStreamToCall(remoteStreams[i].peerid, stream.streamname);
                }
                easyrtc.renegotiate(remoteStreams[i].peerid);

            }
        }else{
            // New stream
            localStreams.push(infos);
            if (stream.streamName === "default"){
                local_index = 0;
                console.log("Connecting to session...");
                easyrtc.connect("OpenTera", signalingLoginSuccess, signalingLoginFailure);

            }else{
                // Other stream - must add to call
                console.log("Adding stream to session...");
                sendPrimaryView(local_peerid, stream.streamName);
                setPrimaryViewIcon(local_peerid, stream.streamName);
                local_index = 1; // Secondary stream in the call
                for (let i=0; i<remoteStreams.length; i++){
                    easyrtc.addStreamToCall(remoteStreams[i].peerid, stream.streamName, function (/*caller, streamName*/) {
                        //console.log("Added stream to " + caller + " - " + streamName);
                        updateUserLocalViewLayout();
                    });
                }
            }
        }
        easyrtc.setVideoObjectSrc(getVideoWidget(true, local_index+1)[0], stream);

        // Update status icons
        easyrtc.enableMicrophone(!localContact.status.microMuted)
        updateStatusIconState(!localContact.status.microMuted, true, local_index+1, 'Mic');
        updateStatusIconState(true, true, local_index+1, 'Video');
        if (local_index === 0){
            unblurredTrack = undefined;
            blur(currentConfig.video1Blur, false);
        }

    }else{
        console.log("Got local stream - waiting for it to become active...");
    }
}

function localVideoStreamError(errorCode, errorText){
    if (currentConfig.currentVideoSourceIndex + 1 < videoSources.length){
        console.log("initMediaSource - Unable to open current source " + videoSources[currentConfig.currentVideoSourceIndex].label + " - Trying next one..." );
        currentConfig.currentVideoSourceIndex += 1;
        updateLocalAudioVideoSource(1);
    }else{
        showError("initMediaSource", "Error #" + errorCode + ": " + errorText, true);
    }
}

function forwardData(data)
{
    //Contact should be a JSON object
    console.log("Forwarding data : " + data);
    let settings = JSON.parse(data);

    if (settings.uuid !== localContact.uuid){
        let peer_id = getPeerIdForUuid(settings.uuid);
        if (peer_id){
            console.log("Forwarding to peer id" + peer_id);
            if (easyrtc.webSocketConnected) {
                easyrtc.sendDataWS(peer_id, 'DataForwarding', data, function (ackMesg) {
                    //console.error("ackMsg:",ackMesg);
                    if (ackMesg.msgType === 'error') {
                        console.error(ackMesg.msgData.errorText);
                    }
                });
            }
        }else{
            console.warn('Trying to forward data to ' + settings.uuid + ', but not connected.')
        }
    }else{
        showError("forwardData", "Wanted to forward settings to remote user, but received local user instead.", false);
    }
}

function broadcastlocalCapabilities(){
    if (easyrtc.webSocketConnected){
        easyrtc.sendDataWS({"targetRoom":"default"}, 'updateCapabilities', localCapabilities,
            function(ackMesg) {
            //console.error("ackMsg:",ackMesg);
            if( ackMesg.msgType === 'error' ) {
                console.error(ackMesg.msgData.errorText);
            }
        });
    }
}

function broadcastStatus(){
    sendStatus({"targetRoom":"default"});
}

function broadcastlocalPTZCapabilities(){
    let request = Object.assign({}, localPTZCapabilities);

    if (!isCurrentCameraPTZ()){
            // Camera isn't selected and PTZ does not apply to all camera - force values to false
            request.presets = false;
            request.zoom = false;
            request.settings = false;
            request.camera = undefined;
    }

    if (localPTZCapabilities.uuid !== 0 || !teraConnected){
        console.log("Broadcasting PTZ capabilities " + localPTZCapabilities.uuid + " = " + localPTZCapabilities.zoom + " " + localPTZCapabilities.presets + " " + localPTZCapabilities.settings);
        if (easyrtc.webSocketConnected)
            easyrtc.sendDataWS({"targetRoom":"default"}, 'updatePTZCapabilities', request, function(ackMesg) {
                //console.error("ackMsg:",ackMesg);
                if( ackMesg.msgType === 'error' ) {
                    console.error(ackMesg.msgData.errorText);
                }
            });
        else{
            console.log("Didn't broadcast: not connected yet!");
        }

    }else
        showError("broadcastlocalPTZCapabilities", "PREVENTED PTZ capabilities broadcasting : uuid = 0!", false);
}

function sendContactInfo(peerid_target){
    console.log("Sending contact info to :", peerid_target);
    console.log("My uuid: " + localContact.uuid + ", my Name: " + localContact.name);
    //send contact information to other users
    if (easyrtc.webSocketConnected){
        easyrtc.sendDataWS( peerid_target, 'contactInfo', localContact, function(ackMesg) {
            //console.error("ackMsg:",ackMesg);
            if( ackMesg.msgType === 'error' ) {
                console.error(ackMesg.msgData.errorText);
            }
        });
    }
}

function updateRoomUsers(roomName, occupants, isPrimary) {
    console.log("updateRoomUsers: " + JSON.stringify(occupants));
    for(let peerid in occupants) {
        if (peerid !== local_peerid){
            if (needToCallOtherUsers) {
                console.log("Calling " + peerid);
                easyrtc.call(
                    peerid,
                    //newStreamStarted,
                    null,
                    //streamDisconnected,
                    null,
                    //null
                    null,
                    //easyrtc.getLocalMediaIds()
                    localStreams.map(stream => stream.streamname)
                )
            }
        }
    }

    remoteStreams.forEach(remote_stream => {
        if (!(remote_stream.peerid in occupants)) {
            console.log('Peer id ' + remote_stream.peerid + ' left, but still has hanging stream. Cleaning up...');
            streamDisconnected(remote_stream.peerid, remote_stream.stream, remote_stream.streamname);
        }
    });

    needToCallOtherUsers = false;
}

function newStreamStarted(callerid, stream, streamname) {
    console.log("New Stream from " + callerid + " - Stream " + streamname);

    // Check if already have a stream with that name from that source
    let slot = getStreamIndexForPeerId(callerid, streamname);

    // Find first empty slot
    if (slot === undefined){
        if (remoteStreams.length+1 > maxRemoteSourceNum) {
            showError("newStreamStarted", translator.translateForKey("errors.stream-no-slot", currentLang), true);
            return;
        }
        remoteStreams.push({'peerid': callerid, 'streamname': streamname, 'stream': stream})
        slot = remoteStreams.length;
    }else{
        slot += 1; // Since views starts at 1, and arrays at 0
    }

    console.log ("Assigning to slot " + slot);

    // Check if we have a remote contact info already for that source and rename if
    let contact_index = getContactIndexForPeerId(callerid);
    if (contact_index !== undefined){
        let title =  remoteContacts[contact_index].name;
        // console.log('Found remote contact - ' + title + ' for slot ' + slot);
        if (title === undefined) title = "Participant #" + (contact_index+1);
        if (streamname.endsWith('ScreenShare')) {
            title = translator.translateForKey('ui.screenof') + " " + title;
        }
        if (streamname.endsWith('2ndStream')){
            title = translator.translateForKey('ui.cameraof') + " " + title;
        }
        setTitle(false, slot, title, remoteContacts[contact_index].status.isUser);
    }

    // Enable-disable status controls
    if (streamname !== "default"){
        if (streamname.endsWith("ScreenShare")){
            // Screen sharing = no controls
            showStatusControls(false, slot, false);
        }
        if (streamname.endsWith("ScreenShareAudio")){
            // Only sharing audio, video track is always enabled - disable!
            // stream.getVideoTracks()[0].enabled = false;
            setRemoteStatusVideo(slot-1, true); // Display status video for that stream
        }

    }else{
        showStatusControls(false, slot, true);
        playSound("audioConnected");
    }

    //console.log("teraConnected = " + teraConnected);
    if (teraConnected){
        //if (SharedObject.newRemoteConnection != undefined){
        console.log("Sending newRemoteConnection()");
        SharedObject.newRemoteConnection();
        //}
    }

    easyrtc.setVideoObjectSrc(getVideoWidget(false, slot)[0], stream);

    // Update display
    updateUserRemoteViewsLayout();
    updateUserLocalViewLayout();
    refreshRemoteStatusIcons(callerid);

    if (streamname === "default"){
        // Send self contact card
        sendContactInfo(callerid);

        // Sends PTZ capabilities
        broadcastlocalPTZCapabilities();

        // Sends other capabilities
        broadcastlocalCapabilities();

        sendStatus(callerid);

        if (!isParticipant){
            if (streamRecorder !== undefined && streamRecorder !== null){
                broadcastRecordingStatus(true, callerid);
            }
        }

        if (!isParticipant){
            if (primaryView.peerid !== 0){
                sendPrimaryView(primaryView.peerid, primaryView.streamName);
            }
        }
    }

    if (primaryView.peerid === callerid){
        // Select current primary view
        setPrimaryView(primaryView.peerid, primaryView.streamName);
    }
    // Update large view if required to show the last user connected
    if (isParticipant && primaryView.peerid === 0 && contact_index !== undefined
        && remoteContacts[contact_index].status.isUser){
        //setPrimaryView(msgData.peerid, "default");
        setLargeView(getVideoViewId(false, slot));
    }

    // Recorder
    if (!isParticipant){
        if (streamRecorder !== undefined && streamRecorder !== null){
            //console.log("Adding stream to recorder: " + stream.getVideoTracks().length + " video(s), " +
            //stream.getAudioTracks().length + " audio(s).");
            streamRecorder.addVideoToRecorder(stream);
        }
    }

    // Add second video, if present
    if (localStreams.length>1){
        setTimeout(function(){
            console.log("Adding secondary video to " + callerid + ", name: " + localStreams[1].streamname);
            easyrtc.addStreamToCall(callerid, localStreams[1].streamname, function (caller, streamName) {
                console.log("Added secondary stream to " + caller + " - " + streamName);
            });
        }, 1000);
    }

}

function streamDisconnected(callerid, mediaStream, streamName){
    // Find video slot used by that caller
    let slot = getStreamIndexForPeerId(callerid, streamName);

    if (slot === undefined){
        showError("Stream disconnected", callerid  + " currently not displayed. Aborting.", false);
        return;
    }

    console.log ("Stream disconnected: " + callerid + " - Slot " + (slot+1));

    // Is that stream displayed in large view? If so, we must also switch the layout
    if (!isParticipant){
        if (typeof(currentLayoutId) !== 'undefined'){
            if (currentLayoutId === layouts.LARGEVIEW){
                if (getVideoViewId(false, slot+1) === currentLargeViewId){
                    setCurrentUserLayout(layouts.GRID, false);
                }
            }
        }
    }else{
        if (currentLargeViewId === getVideoViewId(callerid === local_peerid, slot+1)){
            // Currently displayed in large view - set next large view
            let new_large_view = getFirstRemoteUserVideoViewId();
            if (new_large_view === undefined)
                new_large_view = "remoteView1";
            setLargeView(new_large_view,false);
        }
    }

    // Stop chronos if it's the default stream that was stopped
    if (streamName === 'default'){
        stopChrono(isParticipant, slot+1, true);
        showCounter(isParticipant, slot+1, false);
        playSound("audioDisconnected");
    }

    // Remove primaryView if it's the stream that was displayed in primary view
    if (!isParticipant){
        if (primaryView.streamName === streamName && callerid === primaryView.peerid){
            primaryView = undefined
            sendPrimaryView(0,"");
            setPrimaryViewIcon(0,"");
        }
    }else{
        if (primaryView.streamName === streamName && callerid === primaryView.peerid){
            // set next large view
            /*let new_large_view = getFirstRemoteUserVideoViewId();
            if (new_large_view === undefined)
                new_large_view = "remoteView1";*/
            setPrimaryView(0, "");
            //setLargeView(new_large_view, false);
        }
    }

    // If that stream used in a status video?
    setRemoteStatusVideo(slot, false);

    // Remove stream
    for (let i=0; i<remoteStreams.length; i++){
        //console.log(remoteStreams[i].peerid + " = " + callerid + " && " + remoteStreams[i].streamname + " = " + streamName + "?");
        if (remoteStreams[i].peerid === callerid && remoteStreams[i].streamname === streamName){
            console.log("Removed stream from remote stream list");
            remoteStreams.splice(i,1);
            // Remove record status
            setRecordingStatus(false, i+1, false);
            break;
        }
    }

    if (!isParticipant){
        if (streamRecorder !== undefined && streamRecorder !== null){
            streamRecorder.refreshVideosInRecorder();
        }
    }

    // Remove contact info if the "default" stream was disconnected
    let contact_index = getContactIndexForPeerId(callerid);
    if (contact_index !== undefined && streamName === 'default'){
        remoteContacts.splice(contact_index, 1);
    }

    // Update views
    for (let i=0; i<remoteStreams.length; i++){
        easyrtc.setVideoObjectSrc(getVideoWidget(false,i+1)[0], remoteStreams[i].stream);
        refreshRemoteStatusIcons(remoteStreams[i].peerid);
        let contact_index = getContactIndexForPeerId(remoteStreams[i].peerid);
        if (contact_index !== undefined) {
            let title = remoteContacts[contact_index].name;
            if (remoteStreams[i].streamname.endsWith('ScreenShare'))
                title = translator.translateForKey('ui.screenof') + " " + title;
            if (remoteStreams[i].streamname.endsWith('2ndStream'))
                title = translator.translateForKey('ui.cameraof') + " " + title;
            setTitle(false, i + 1, title, remoteContacts[contact_index].status.isUser);
        }
    }

    updateUserRemoteViewsLayout();
    updateUserLocalViewLayout();
}

function disconnectedFromSignalingServer(){
    showError("disconnectedFromSignalingServer", "Disconnected from signaling server... Trying to reconnect.", false);
    showStatusMsg(translator.translateForKey("status.lost-connection", currentLang));
    localStreams = [];
    remoteStreams = [];
    remoteContacts = [];
    connected = false;
    connect();
}

function getUuidForPeerId(peerid){
    for (let i=0; i<remoteContacts.length; i++){
        if (remoteContacts[i].peerid === peerid){
            return remoteContacts[i].uuid;
        }
    }
    return undefined;
}

function getPeerIdForUuid(uuid){
    for (let i=0; i<remoteContacts.length; i++){
        if (remoteContacts[i].uuid === uuid){
            return remoteContacts[i].peerid;
        }
    }
    return undefined;
}

function getContactIndexForUuid(uuid){
    for (let i=0; i<remoteContacts.length; i++){
        if (remoteContacts[i].uuid === uuid)
            return i;
    }
    return undefined;
}

function getContactIndexForPeerId(peerid){
    for (let i=0; i<remoteContacts.length; i++){
        if (remoteContacts[i].peerid === peerid)
            return i;
    }
    return undefined;
}

function getContactNameForPeerId(peerid){
    for (let i=0; i<remoteContacts.length; i++){
        if (remoteContacts[i].peerid === peerid)
            return remoteContacts[i].name;
    }
    return undefined;
}

function getContactIndexForName(name){
    for (let i=0; i<remoteContacts.length; i++){
        if (remoteContacts[i].name === name)
            return i;
    }
    return undefined;
}

function getStreamIndexForPeerId(peerid, streamname = 'default'){
    for (let i=0; i<remoteStreams.length; i++){
        if (remoteStreams[i].peerid === peerid && remoteStreams[i].streamname === streamname)
            return i;
    }
    return undefined;
}

function getLocalStreamIndex(streamname = 'default'){
    for (let i=0; i<localStreams.length; i++){
        if (localStreams[i].streamname === streamname)
            return i;
    }
    return undefined;
}

function sendStatus(target_peerid){
    let request = {"peerid": local_peerid,
        "micro": !localContact.status.microMuted,
        "micro2":isStatusIconActive(true, 2, "Mic"),
        "speaker": !localContact.status.speakerMuted,
        "video": !localContact.status.videoMuted,
        "isUser": !isParticipant,
        "videoSrcLength": videoSources.length,
        "secondSource": currentConfig.currentVideoSource2Index > -1,
        "sharing2ndSource": localContact.status.sharing2ndSource,
        "sharingScreen": localContact.status.sharingScreen
    };

    if (easyrtc.webSocketConnected){
        easyrtc.sendDataWS(target_peerid, 'updateStatus', request, function(ackMesg) {
            //console.error("ackMsg:",ackMesg);
            if( ackMesg.msgType === 'error' ) {
                console.error(ackMesg.msgData.errorText);
            }
        });
    }
}

function dataReception(sendercid, msgType, msgData, targeting) {
    console.log("dataReception : src=" + sendercid + " type=" + msgType + " data=" + JSON.stringify(msgData) + " target=" + targeting.targetEasyrtcid);

    if (msgType === "contactInfo"){
        // Save contact info
        let contact_card_index = getContactIndexForPeerId(sendercid);
        if (contact_card_index !== undefined){
            console.log("ContactInfo: Remote contact found - updating!");
            remoteContacts[contact_card_index] = msgData;
        }else{
            console.log("ContactInfo: Remote contact not found - adding!");
            remoteContacts.push(msgData);
        }
        // Update title
        let stream_index = getStreamIndexForPeerId(sendercid, 'default');
        console.log('Found stream index: ' + stream_index);
        if (stream_index !== undefined) {
            setTitle(false, stream_index+1, msgData.name, msgData.status.isUser);
        }
    }

    if (msgType === "PTZRequest"){
        //console.error("PTZRequest");
        //console.error(msgData);
        if (isCurrentCameraPTZ()){
            if (teraConnected) {
                if (currentConfig.video1Mirror){
                    // If we are mirrored, we are not on the other end - correct x.
                    msgData.x = msgData.w - msgData.x;
                }
                SharedObject.imageClicked(localContact.uuid, msgData.x, msgData.y, msgData.w, msgData.h);
            }else
                console.error("Not connected to client.");
        }

    }

    if (msgType === "MouseDownEvent"){
        if (localCapabilities.screenControl === true && msgData.streamname.endsWith('ScreenShare')){
            // Remote control
            if (teraConnected) {
                SharedObject.mouseDownEvent(localContact.uuid, msgData.x, msgData.y, msgData.w, msgData.h);
            }else{
                console.error("Not connected to client");
            }
        }
    }

    if (msgType === "MouseUpEvent"){
        if (localCapabilities.screenControl === true && msgData.streamname.endsWith('ScreenShare')){
            // Remote control
            if (teraConnected) {
                SharedObject.mouseUpEvent(localContact.uuid, msgData.x, msgData.y, msgData.w, msgData.h);
            }else{
                console.error("Not connected to client");
            }
        }
    }

    if (msgType === "MouseMoveEvent"){
        if (localCapabilities.screenControl === true && msgData.streamname.endsWith('ScreenShare')){
            // Remote control
            if (teraConnected) {
                SharedObject.mouseMoveEvent(localContact.uuid, msgData.x, msgData.y, msgData.w, msgData.h);
            }else{
                console.error("Not connected to client");
            }
        }
    }

    if (msgType === "ZoomRequest"){
        //console.error("ZoomRequest");
        //console.error(msgData);
        if (isCurrentCameraPTZ()) {
            if (teraConnected) {
                if (msgData.value === "in")
                    SharedObject.zoomInClicked(localContact.uuid);
                if (msgData.value === "out")
                    SharedObject.zoomOutClicked(localContact.uuid);
                if (msgData.value === "min")
                    SharedObject.zoomMinClicked(localContact.uuid);
                if (msgData.value === "max")
                    SharedObject.zoomMaxClicked(localContact.uuid);
            } else
                console.error("Not connected to client.");
        }
    }

    if (msgType === "PresetRequest"){
        let event =[];

        if (msgData.set === true){
            event.shiftKey = true;
            event.ctrlKey = true;
        }
        gotoPreset(event, true, 1, msgData.preset);
    }

    if (msgType === "CamSettingsRequest"){
        if (isCurrentCameraPTZ()) {
            if (teraConnected) {
                SharedObject.camSettingsClicked(msgData.uuid);
            } else
                showError("dataReception/CamSettingsRequest", "Not connected to client.", false);
        }
    }

    if (msgType === "DataForwarding"){
        if (teraConnected)
            SharedObject.dataForwardReceived(msgData);
        else
            console.error("Not connected to client.");
    }

    if (msgType === "muteMicro"){
        muteMicro(true, msgData.index, msgData.micro);
        /*if (msgData.subindex=="")
            muteMicro(0);
        else
            muteMicro(-1);*/
    }

    if (msgType === "muteSpeaker"){
        muteSpeaker(true, msgData.index, msgData.speaker);
    }

    if (msgType === "muteVideo"){
        muteVideo(true, msgData.index, msgData.video);
    }

    if (msgType === "setMirror"){
        showVideoMirror(true, msgData.index, msgData.mirror);
    }

    if (msgType === "addVideo"){
        //addLocalSource2(0);
        console.warn("dataReception/addVideo - not implemented yet!");
    }

    if (msgType === "removeVideo"){
        //removeLocalSource2(0);
        console.warn("dataReception/removeVideo - not implemented yet!");
    }

    if (msgType === "updatePTZCapabilities"){
        setPTZCapabilities(msgData.uuid, msgData.zoom, msgData.presets, msgData.settings);
    }

    if (msgType === "updateCapabilities"){
        setCapabilities(sendercid, msgData.video2, msgData.screenControl, msgData.screenSharing);
    }

    if (msgType === "setPrimaryView"){
        setPrimaryView(msgData.peerid, msgData.streamName);
    }

    if (msgType === "updateStatus"){
        //console.log(msgData);
        let index = getStreamIndexForPeerId(sendercid, 'default');
        let contact_index = getContactIndexForPeerId(sendercid);
        if (contact_index === undefined){
            console.log("No contact card yet for that peer - creating one.");
            remoteContacts.push({peerid: sendercid});
            contact_index = remoteContacts.length-1;
        }

        //remoteContacts[contact_index].status = msgData;
        remoteContacts[contact_index].status = Object.assign({}, remoteContacts[contact_index].status, msgData);
        if (index === undefined){
            // Got status before stream... must "buf" that status
            console.log("Got updateStatus, but no stream yet - buffering.");

        }else {
            refreshRemoteStatusIcons(sendercid);

            if (msgData.mirror !== undefined){
                showVideoMirror(false, index, msgData.mirror);
            }

            // Update large view if required
            if (isParticipant && primaryView.peerid === 0 && msgData.isUser){
                //setPrimaryView(msgData.peerid, "default");
                setLargeView(getVideoViewId(false, index+1));
            }
            setTitle(false, index+1, remoteContacts[contact_index].name, msgData.isUser);
        }
    }

    if (msgType === "Chrono"){
        // Start - stop local chrono
        if (msgData.state === 1){
            setupChrono(true, 1, msgData.increment, msgData.duration, msgData.title, msgData.value);
            startChrono();
        }
        if (msgData.state === 0){
            stopChrono(true, 1);
        }
        if (msgData.state === 2){
            pauseChrono(true, 1);
        }
    }

    if (msgType === "Counter"){
        if (msgData.state === true){
            setupCounter(true, 1, msgData.value);
        }else{
            showCounter(true, 1, false);
        }
    }

    if (msgType === "queryConfig"){
        // Send audio & video sources, and current config
        // Check if querying peer is a user, otherwise ignore.
        let src_index = getContactIndexForPeerId(sendercid);
        if (src_index === undefined){
            console.warn("Ignoring query - peer querying not in contact list!");
            return;
        }
        if (!remoteContacts[src_index].status.isUser){
            console.warn("Ignoring query - peer is not of 'user' type.");
            return;
        }
        // Send reply
        easyrtc.sendDataWS(sendercid, "currentConfig", {"audios": audioSources,
                                                                        "videos": videoSources,
                                                                        "config": currentConfig}, function(ackMesg) {
            if( ackMesg.msgType === 'error' ) {
                console.error(ackMesg.msgData.errorText);
            }
        });
    }

    if (msgType === "currentConfig"){
        // Display config dialog with values
        showConfigDialog(sendercid, msgData.audios, msgData.videos, msgData.config);
    }

    if (msgType === "updateConfig"){
        let src_index = getContactIndexForPeerId(sendercid);
        if (src_index === undefined){
            console.warn("Ignoring query - peer querying not in contact list!");
            return;
        }
        if (!remoteContacts[src_index].status.isUser){
            console.warn("Ignoring query - peer is not of 'user' type.");
            return;
        }

        updateLocalConfig(msgData);

        broadcastStatus();
    }

    if (msgType === "nextVideoSource"){
        swapVideoSource(true, 1);
    }

    if (msgType === "recordStatus"){
        // Show record icon
        let index = getStreamIndexForPeerId(sendercid, 'default');
        /*if (index === undefined) {
            // Got status before stream... must "buf" that status
            console.log("Got recordStatus, but no stream yet - buffering.");
        }else {*/
            setRecordingStatus(false, index + 1, msgData)
        //}

        // Display status message
        let contact_name = getContactNameForPeerId(sendercid);
        let record_msg = "";
        if (contact_name !== undefined){
            if (msgData === true)
                record_msg = contact_name + translator.translateForKey("status.user-start-recording", currentLang);
            else
                record_msg = contact_name + translator.translateForKey("status.user-stop-recording", currentLang);
        }else{
            if (msgData === true)
                record_msg = translator.translateForKey("status.start-recording", currentLang);
            else
                record_msg = translator.translateForKey("status.stop-recording", currentLang);
        }

        showStatusMsg(record_msg, 5000); // Display for 5 seconds
    }

    if (msgType === "shareSecondSource"){
        if (targeting.targetEasyrtcid === local_peerid){
            // Message sent directly to us
            localContact.status.sharing2ndSource = !msgData;
            btnShow2ndLocalVideoClicked();
            broadcastStatus();
        }
    }
    if (msgType === "shareScreen"){
        if (targeting.targetEasyrtcid === local_peerid){
            // Message sent directly to us
            localContact.status.sharingScreen = !msgData;
            btnShareScreenClicked();
            broadcastStatus();
        }
    }
}

function signalingLoginSuccess(peerid,  roomOwner) {
    console.log("Login success! peerid = " + peerid);
    local_peerid = peerid;
    localContact.peerid = peerid;

    // Ensure id is set correctly on each local stream!
    for (let i=0; i<localStreams.length; i++){
        localStreams[i].peerid = peerid;
    }

    /*easyrtc.getVideoSourceList(fillVideoSourceList);
    easyrtc.getAudioSourceList(fillAudioSourceList);*/

    // Sends PTZ capabilities
    broadcastlocalPTZCapabilities();

    // Sends other capabilities
    // broadcastlocalCapabilities();

    clearStatusMsg();
    stopSounds();

}

function signalingLoginFailure(errorCode, message) {

    showError("signalingLoginFailure", "Can't connect to signaling server! Code: " + errorCode +" - " + message, false);
    //easyrtc.showError(errorCode, message);

    clearStatusMsg();
}

async function shareScreen(local, start, sound_only = false){
    let streamName = localContact.peerid + '_' +'ScreenShare';
    if (sound_only){
        streamName += "Audio";
    }
    if (start === true){
        // Start screen sharing
        let screenStream = undefined;
        try {
            let constraints = {}
            if (sound_only){
                constraints.audio = {sampleRate: 48000,
                                     noiseSuppression: false,
                                     echoCancellation: true,
                                     channelCount: 2,
                                     autoGainControl: false,
                                     voiceActivityDetection: false};
                constraints.video = {frameRate: 1, height: 120, width: 160};
            }else{
                constraints.video = true;
                constraints.audio = currentConfig.screenAudio;
            }
            screenStream = await navigator.mediaDevices.getDisplayMedia(constraints);
            if (sound_only){
                // Video track must be stopped if we want sound only, since it is required to get Display Media to share
                screenStream.getVideoTracks()[0].enabled = false;
                easyrtc.setSdpFilters(undefined, highQualityAudioSdp);
            }
            easyrtc.register3rdPartyLocalMediaStream(screenStream, streamName);
            // TODO: Use easyrtc.setSdpFilters to improve audio quality
            //easyrtc.setSdpFilters()

            console.log("Starting screen sharing - with audio: " + (sound_only || currentConfig.screenAudio));

            // Then to add to existing connections
            for (let i=0; i<remoteContacts.length; i++){
                console.log("Starting screen sharing with " + remoteContacts[i].peerid);
                easyrtc.addStreamToCall(remoteContacts[i].peerid, streamName, function (caller, streamName) {
                    console.log("Started screen sharing with " + caller + " - " + streamName);
                    easyrtc.renegotiate(remoteContacts[i].peerid);
                });
            }
            if (!sound_only){
                easyrtc.setVideoObjectSrc(getVideoWidget(true,2)[0], screenStream);
                sendPrimaryView(local_peerid, streamName);
                setPrimaryViewIcon(local_peerid, streamName);
            }

            localStreams.push({"peerid": local_peerid, "streamname": streamName, "stream":screenStream});

        } catch(err) {
            if (!teraConnected){
                showError("shareScreen", translator.translateForKey("errors.no-sharescreen-access", currentLang)
                    + "<br/><br/>" + translator.translateForKey("errors.error-msg", currentLang) +
                    ": <br/>" + err, true, false);
            }
            return Promise.Reject(err)
        }

    }else{
        // Stop screen sharing
        for (let i=0; i<remoteContacts.length; i++) {
            easyrtc.removeStreamFromCall(remoteContacts[i].peerid, streamName);
        }
        console.log("Stopping screen sharing...");
        //easyrtc.closeLocalMediaStream("ScreenShare");

        // Stop local stream
        localStreams[1].stream.getVideoTracks()[0].stop();   // Screen sharing is always index 1 of localStreams,
                                                             // video track index = 0, since we always have just one.
        if (localStreams[1].stream.getAudioTracks().length > 0)
            localStreams[1].stream.getAudioTracks()[0].stop();
        easyrtc.setVideoObjectSrc(getVideoWidget(true,2)[0], null);

        // Remove stream
        localStreams.pop();
    }

    updateUserLocalViewLayout();
}

function share2ndStream(local, start){

    if (connected !== true) {
        showError("share2ndStream", translator.translateForKey("errors.extrasource-not-connected", currentLang), true, false);
        return;
    }
    let streamname = "2ndStream";

    if (start === true){
        // Start second stream
        let media_constraints = {};

        // Check if we need to add a video track
        if (currentConfig.currentVideoSource2Index >= 0) {
            media_constraints.video = {deviceId: {exact: videoSources[currentConfig.currentVideoSource2Index].deviceId}};
            easyrtc.enableVideo(true);
        }else {
            easyrtc.enableVideo(false);
        }

        // Check if we need to add an audio track
        if (currentConfig.currentAudioSource2Index >= 0) {
            media_constraints.audio = {deviceId: {exact: audioSources[currentConfig.currentAudioSource2Index].deviceId}};
            easyrtc.enableAudio(true);
        }else {
            easyrtc.enableAudio(false);
        }

        //console.log(media_constraints);
        easyrtc._presetMediaConstraints = media_constraints;

        // Disable all tracks before creating, if needed
        if (localStreams.length > 1){
            let stream = localStreams[1].stream;
            enableAllTracks(stream, false);
        }

        easyrtc.initMediaSource(
            localVideoStreamSuccess,
            localVideoStreamError,
            streamname);

        }
    else{
        // Stop 2nd source sharing
        for (let i=0; i<remoteStreams.length; i++) {
            easyrtc.removeStreamFromCall(remoteStreams[i].peerid, streamname);
        }
        console.log("Stopping second local stream...");

        // Stop local stream
        if (localStreams.length > 1){
            let stream = localStreams[1].stream;
            enableAllTracks(stream, false);   // Screen sharing is always index 1 of localStreams,
                                                                 // video track index = 0, since we always have just one.

            easyrtc.setVideoObjectSrc(getVideoWidget(true,2)[0], null);

            // Remove stream
            localStreams.pop();
        }
    }

    updateUserLocalViewLayout();

    // Send status update
    sendStatus({"targetRoom": "default"});
}

function enableAllTracks(stream, enable){
    let videoTracks = stream.getVideoTracks();
    let audioTracks = stream.getAudioTracks();

    for (let i=0; i<videoTracks.length; i++)
        videoTracks[i].enabled = enable;

    for (let i=0; i<audioTracks.length; i++)
        audioTracks[i].enabled = enable;
}

// States: 0 = Stop, 1 = Start, 2 = Pause
function sendChronoMessage(target_peerids, state, msg = undefined, duration=undefined, increment=-1, value= undefined){

    let request = {"state": state};
    if (msg !== undefined)
        request.title = msg;

    if (duration !== undefined)
        request.duration = duration;

    request.increment = increment;

    if (value !== undefined)
        request.value = value;
    else
        request.value = -1;

    if (easyrtc.webSocketConnected){
        for (let i=0; i<target_peerids.length; i++){
            easyrtc.sendDataWS( target_peerids[i], 'Chrono', request,
                function(ackMesg) {
                    //console.error("ackMsg:",ackMesg);
                    if( ackMesg.msgType === 'error' ) {
                        console.error(ackMesg.msgData.errorText);
                    }
                });
        }
    }
}

function sendCounterMessage(target_peerids, state, value){
    let request = {"state": state, "value": value};

    if (easyrtc.webSocketConnected){
        for (let i=0; i<target_peerids.length; i++){
            easyrtc.sendDataWS( target_peerids[i], 'Counter', request,
                function(ackMesg) {
                    //console.error("ackMsg:",ackMesg);
                    if( ackMesg.msgType === 'error' ) {
                        console.error(ackMesg.msgData.errorText);
                    }
                });
        }
    }
}

function sendQueryConfig(peerid_target){
    console.log("Sending config query to :", peerid_target);
    // Query for the remote configuration
    if (easyrtc.webSocketConnected){
        easyrtc.sendDataWS(peerid_target, 'queryConfig', null,function(ackMesg) {
            if( ackMesg.msgType === 'error' ) {
                console.error(ackMesg.msgData.errorText);
            }
        });
    }
}

function sendUpdateConfig(peerid_target, config){
    console.log("Sending config to :", peerid_target);
    if (easyrtc.webSocketConnected){
        easyrtc.sendDataWS(peerid_target, 'updateConfig', config,function(ackMesg) {
            if( ackMesg.msgType === 'error' ) {
                console.error(ackMesg.msgData.errorText);
            }
        });
    }
}

function sendNextVideoSource(peerid_target){
    console.log("Sending next video source request to :", peerid_target);
    if (easyrtc.webSocketConnected){
        easyrtc.sendDataWS(peerid_target, 'nextVideoSource', null,function(ackMesg) {
            if( ackMesg.msgType === 'error' ) {
                console.error(ackMesg.msgData.errorText);
            }
        });
    }
}

function broadcastRecordingStatus(status, peerid_target = -1){
    console.log("Broadcasting recording: " + status);
    if (easyrtc.webSocketConnected){
        if (peerid_target === -1) // Broadcast to all
            peerid_target = {"targetRoom": "default"};
        easyrtc.sendDataWS(peerid_target, 'recordStatus', status, function(ackMesg) {
            //console.error("ackMsg:",ackMesg);
            if( ackMesg.msgType === 'error' ) {
                console.error(ackMesg.msgData.errorText);
            }
        });
    }
    else{
        console.log("Didn't broadcast: not connected yet!");
    }
}

function sendShareSecondSource(peerid_target, status){
    console.log("Sending request to share second source " + status + " to: ", peerid_target);
    if (easyrtc.webSocketConnected){
        easyrtc.sendDataWS(peerid_target, 'shareSecondSource', status,function(ackMesg) {
            if( ackMesg.msgType === 'error' ) {
                console.error(ackMesg.msgData.errorText);
            }
        });
    }
}

function sendShareScreen(peerid_target, status){
    console.log("Sending request to share screen " + status + " to: ", peerid_target);
    if (easyrtc.webSocketConnected){
        easyrtc.sendDataWS(peerid_target, 'shareScreen', status,function(ackMesg) {
            if( ackMesg.msgType === 'error' ) {
                console.error(ackMesg.msgData.errorText);
            }
        });
    }
}

function getVideoStreamsIndexes(streamsList){
    let indexes = [];
    for (let stream_index = 0; stream_index<streamsList.length; stream_index++){
        if (streamsList[stream_index].streamname.endsWith("ScreenShareAudio"))
            continue;
        let videos = streamsList[stream_index].stream.getVideoTracks();
        for (let video_index=0; video_index<videos.length; video_index++){
            if (videos[video_index].enabled){
                indexes.push(stream_index+1);
                break; // No need to continue - we have at least one video!
            }
        }
    }
    return indexes;
}

function highQualityAudioSdp(sdp){
    let modified_sdp = sdp;

    if (sdp.search('useinbandfec=1; stereo=1; maxaveragebitrate') === -1){
        modified_sdp = sdp.replaceAll('useinbandfec=1', 'useinbandfec=1; stereo=1; maxaveragebitrate=64000');
    }
    
    return modified_sdp;
}
