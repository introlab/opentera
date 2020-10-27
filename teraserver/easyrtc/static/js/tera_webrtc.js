// WebRTC ids
var local_peerid = "0";

// Contact cards
var localContact = {}; // {uuid, name, peerid}
var remoteContacts = []; // Used to store information about everyone that has connected (contactinfos)
                            // {uuid, name, peerid}
let remoteStreams = []; // {peerid, streamname, stream: MediaStream}, order is important as it is linked to each view!
let localStreams = []; // {peerid, streamname, stream: MediaStream}, order is important as it is linked to each local view!

// Status / controls variables
var connected = false;
var needToCallOtherUsers = false;

function connect() {

    console.log("Connecting...");
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
    easyrtc.setRoomEntryListener(function(entry, roomName) {
        needToCallOtherUsers = true;
    });
    easyrtc.setDisconnectListener(disconnectedFromSignalingServer);

    easyrtc.setStreamAcceptor(newStreamStarted);
    easyrtc.setOnStreamClosed(streamDisconnected);
    easyrtc.setPeerListener(dataReception);

    //Post-connect Event listeners
    //easyrtc.setOnHangup(streamDisconnected);
    //easyrtc.setOnCall(newStreamStarted);

    connected = true;
    updateLocalAudioVideoSource(1);

    showLayout(true);
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
        for (let i=1; i<=4; i++){
            let video_widget = getVideoWidget(false, i);
            video_widget.prop('muted', !new_state);
        }

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

function setPrimaryView(peer_id, streamname){
    primaryView = {peerid: peer_id, streamName: streamname};

    // Send request to everyone for the update
    let request = {"primaryView": primaryView};
    if (easyrtc.webSocketConnected){
        easyrtc.sendDataWS({targetRoom: "default"}, 'updateStatus', request,
            function (ackMesg) {
                if (ackMesg.msgType === 'error') {
                    console.error(ackMesg.msgData.errorText);
                }
            });
    }
}

function updateLocalAudioVideoSource(streamindex){
    if (connected === true){
        let streamname = "localStream" + streamindex;
        if (streamindex === 1) // Default stream = no name.
            streamname = "";
        if (streamindex < localStreams.length){
            console.log("Updating audio/video source: " + streamname);

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
        easyrtc.enableAudio(true);
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

    }else{
        console.log("Updated audio/video source - not connected, selection will take effect when connected.");
    }
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
                easyrtc.connect("TeraPlus", signalingLoginSuccess, signalingLoginFailure);

            }else{
                // Other stream - must add to call
                console.log("Adding stream to session...");
                local_index = 1; // Secondary stream in the call
                for (let i=0; i<remoteStreams.length; i++){
                    easyrtc.addStreamToCall(remoteStreams[i].peerid, stream.streamName, function (caller, streamName) {
                        //console.log("Added stream to " + caller + " - " + streamName);
                        updateUserLocalViewLayout(localStreams.length, remoteStreams.length);
                    });
                }
            }

        }
        easyrtc.setVideoObjectSrc(getVideoWidget(true, local_index+1)[0], stream);

        // Clear status icons
        updateStatusIconState(true, true, local_index+1, 'Mic');
        updateStatusIconState(true, true, local_index+1, 'Video');

    }else{
        console.log("Got local stream - waiting for it to become active...");
    }
}

function localVideoStreamError(errorCode, errorText){
    showError("initMediaSource", "Error #" + errorCode + ": " + errorText, true);
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
    let request = localCapabilities;

    if (easyrtc.webSocketConnected){
        easyrtc.sendDataWS({"targetRoom":"default"}, 'updateCapabilities', request, function(ackMesg) {
            //console.error("ackMsg:",ackMesg);
            if( ackMesg.msgType === 'error' ) {
                console.error(ackMesg.msgData.errorText);
            }
        });
    }
}

function broadcastlocalPTZCapabilities(){
    let request = localPTZCapabilities;
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
                    null
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
        if (remoteStreams.length+1 > 4) {
            showError("newStreamStarted", "New stream received, but not slot available!", true);
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
        if (title === undefined) title = "Participant #" + (contact_index+1);
        if (streamname === 'ScreenShare') {
            title = "Écran de " + title;
        }
        setTitle(false, slot, title);
    }

    // Enable-disable status controls
    if (streamname !== "default"){
        if (streamname === "ScreenShare"){
            // Screen sharing = no controls
            showStatusControls(false, slot, false);
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
    updateUserRemoteViewsLayout(remoteStreams.length);
    updateUserLocalViewLayout(localStreams.length, remoteStreams.length);
    refreshRemoteStatusIcons(callerid);

    if (streamname === "default"){
        // Send self contact card
        sendContactInfo(callerid);

        // Update video
        //var videoId = getVideoId(0);
        /*var videoId = getVideoId(slot);
        var video = document.getElementById(videoId);

        // Send status update to all
        var micEnabled = "false";
        //if (video.micEnabled || video.micEnabled==undefined)
        if (isMicActive(0,0))
            micEnabled="true";
        var mic2Enabled = "false";
        if (isMicActive(0,1))
            mic2Enabled="true";

        var spkEnabled = "false";
        if (video.volume=="1")
            spkEnabled = "true";*/

        // Sends PTZ capabilities
        broadcastlocalPTZCapabilities();

        // Sends other capabilities
        broadcastlocalCapabilities();

        sendStatus(callerid);
    }

    // Add second video, if present
    if (localStreams.length>1){
        console.log("Adding secondary video...");
        easyrtc.addStreamToCall(callerid, localStreams[1].streamname);
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
    if (typeof(currentLayoutId) !== 'undefined'){
        if (currentLayoutId === layouts.LARGEVIEW){
            if (getVideoViewId(false, slot) === currentLargeViewId){
                setCurrentUserLayout(layouts.GRID, false);
            }
        }
    }

    // Stop chronos if it's the default stream that was stopped
    if (streamName === 'default'){
        stopChrono(isParticipant, slot+1);
        playSound("audioDisconnected");
    }

    // Remove stream
    for (let i=0; i<remoteStreams.length; i++){
        if (remoteStreams[i].peerid === callerid && remoteStreams[i].streamname === streamName){
            remoteStreams.splice(i,1);
            break;
        }
    }

    // Remove contact info
    // Keep them all for now...
    /*let contact_index = getContactIndexForPeerId(callerid);
    if (contact_index !== undefined){
        remoteContacts.splice(contact_index, 1);
    }*/

    // Update views
    for (let i=0; i<remoteStreams.length; i++){
        easyrtc.setVideoObjectSrc(getVideoWidget(false,i+1)[0], remoteStreams[i].stream);
        refreshRemoteStatusIcons(remoteStreams[i].peerid);
        setTitle(false, i+1, remoteContacts[i].name)
    }

    updateUserRemoteViewsLayout(remoteStreams.length);
    updateUserLocalViewLayout(localStreams.length, remoteStreams.length);
}

function disconnectedFromSignalingServer(){
    showError("disconnectedFromSignalingServer", "Disconnected from signaling server... Trying to reconnect.", false);
    showStatusMsg("Connexion perdue... Reconnexion en cours...");
    localStreams = [];
    remoteStreams = [];
    remoteContacts = [];
    connected = false;
    connect();
}

function getUuidForPeerId(peerid){
    remoteContacts.forEach( contact =>
        {
            if (contact.peerid === peerid){
                return contact.uuid;
            }
        }
    )
    return undefined;
}

function getPeerIdForUuid(uuid){
    remoteContacts.forEach( contact =>
        {
            if (contact.uuid === uuid){
                return contact.peerid;
            }
        }
    )
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

function getStreamIndexForPeerId(peerid, streamname = 'default'){
    for (let i=0; i<remoteStreams.length; i++){
        if (remoteStreams[i].peerid === peerid && remoteStreams[i].streamname === streamname)
            return i;
    }
    return undefined;
}


function sendStatus(target_peerid){
    let request = {"peerid": local_peerid,
        "micro": isStatusIconActive(true, 1, "Mic"),
        "micro2":isStatusIconActive(true, 2, "Mic"),
        "speaker": isStatusIconActive(true, 1, "Speaker"),
        "video": isStatusIconActive(true, 1, "Video"),
        "primaryView": primaryView};

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
        if (stream_index !== undefined) {
            setTitle(false, stream_index+1, msgData.name);
        }
    }

    if (msgType === "PTZRequest"){
        //console.error("PTZRequest");
        //console.error(msgData);
        if (teraConnected)
            SharedObject.imageClicked(localContact.uuid, msgData.x, msgData.y, msgData.w, msgData.h);
        else
            console.error("Not connected to client.");
    }

    if (msgType === "ZoomRequest"){
        //console.error("ZoomRequest");
        //console.error(msgData);
        if (teraConnected){
            if (msgData.value === "in")
                SharedObject.zoomInClicked(localContact.uuid);
            if (msgData.value === "out")
                SharedObject.zoomOutClicked(localContact.uuid);
            if (msgData.value === "min")
                SharedObject.zoomMinClicked(localContact.uuid);
            if (msgData.value === "max")
                SharedObject.zoomMaxClicked(localContact.uuid);
        }else
            console.error("Not connected to client.");
    }

    if (msgType === "PresetRequest"){
        let event =[];

        if (msgData.set === true){
            event.shiftKey = true;
            event.ctrlKey = true;
        }
        gotoPreset(event, 0, msgData.preset);
    }

    if (msgType === "CamSettingsRequest"){
        if (teraConnected){
            let uuid = getUuidForPeerId(sendercid);
            if (uuid){
                SharedObject.camSettingsClicked(uuid);
            }else{
                showError("dataReception/CamSettingsRequest", "Uuid not found.", false);
            }

        }else
            showError("dataReception/CamSettingsRequest", "Not connected to client.", false);
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
        showVideoMirror(true, msgData.index, msgData.mirror); // TODO: handle index
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
        setCapabilities(sendercid, msgData.video2);
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
        }
    }

    if (msgType === "Chrono"){
        // Start - stop local chrono
        if (msgData.state === true){
            startChrono(true, 1, msgData.duration, msgData.title);
        }else{
            stopChrono(true, 1);
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
    broadcastlocalCapabilities();

    clearStatusMsg();
    stopSounds();

}

function signalingLoginFailure(errorCode, message) {

    showError("signalingLoginFailure", "Can't connect to signaling server! Code: " + errorCode +" - " + message);
    //easyrtc.showError(errorCode, message);

    clearStatusMsg();
}

async function shareScreen(local, start){
    if (start === true){
        // Start screen sharing
        let screenStream = undefined;
        try {
            screenStream = await navigator.mediaDevices.getDisplayMedia({video: true});
            easyrtc.register3rdPartyLocalMediaStream(screenStream, 'ScreenShare');

            console.log("Starting screen sharing...");

            // Then to add to existing connections
            for (let i=0; i<remoteStreams.length; i++){
                easyrtc.addStreamToCall(remoteStreams[i].peerid, 'ScreenShare', function (caller, streamName) {
                    //console.log("Started screen sharing with " + caller + " - " + streamName);
                });
            }
            easyrtc.setVideoObjectSrc(getVideoWidget(true,2)[0], screenStream);
            localStreams.push({"peerid": local_peerid, "streamname": "ScreenShare", "stream":screenStream});

        } catch(err) {
            showError("shareScreen", "Impossible de partager l'écran.<br/><br/>Le message d'erreur est le suivant: <br/>" + err, true, false);
            return Promise.Reject(err)
        }

    }else{
        // Stop screen sharing
        for (let i=0; i<remoteStreams.length; i++) {
            easyrtc.removeStreamFromCall(remoteStreams[i].peerid, "ScreenShare");
        }
        console.log("Stopping screen sharing...");
        //easyrtc.closeLocalMediaStream("ScreenShare");

        // Stop local stream
        localStreams[1].stream.getVideoTracks()[0].stop();   // Screen sharing is always index 1 of localStreams,
                                                             // video track index = 0, since we always have just one.
        easyrtc.setVideoObjectSrc(getVideoWidget(true,2)[0], null);

        // Remove stream
        localStreams.pop();
    }

    updateUserLocalViewLayout(localStreams.length, remoteStreams.length);
}

function share2ndStream(local, start){

    if (connected !== true) {
        showError("share2ndStream", "Impossible de démarrer une deuxième source: non-connecté", true, false);
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

    updateUserLocalViewLayout(localStreams.length, remoteStreams.length);
}

function enableAllTracks(stream, enable){
    let videoTracks = stream.getVideoTracks();
    let audioTracks = stream.getAudioTracks();

    for (let i=0; i<videoTracks.length; i++)
        videoTracks[i].enabled = enable;

    for (let i=0; i<audioTracks.length; i++)
        audioTracks[i].enabled = enable;
}

function sendChronoMessage(target_peerids, state, msg = undefined, duration=undefined){

    let request = {"state": state};
    if (msg !== undefined)
        request.title = msg;

    if (duration !== undefined)
        request.duration = duration;

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