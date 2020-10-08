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

    easyrtc.setStreamAcceptor(newStreamStarted);
    easyrtc.setOnStreamClosed(streamDisconnected);
    easyrtc.setPeerListener(dataReception);

    //Post-connect Event listeners
    //easyrtc.setOnHangup(streamDisconnected);
    //easyrtc.setOnCall(newStreamStarted);

    connected = true;
    updateLocalAudioVideoSource();


    clearStatusMsg();
    showLayout(true);
}

function muteMicro(local, index, new_state){
    if (new_state === undefined){ // Toggle is no state specified
        new_state = !isStatusIconActive(local, index, "Mic");
    }

    updateStatusIconState(new_state, local, index, "Mic");

    if (local === true){
        // Send display update request
        let request = {"peerid": local_peerid, micro: new_state};
        easyrtc.enableMicrophone(new_state, "localStream" + index);

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

        // TODO
        console.warn('Video Muting not supported yet.');

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
        let request = {"index": 1, "mirror": mirror}; // TODO: Manage multiple remote streams??
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


function updateLocalAudioVideoSource(){
    if (connected === true){
        console.log("Updating local video source...");
        //easyrtc.disconnect();

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

        easyrtc.closeLocalMediaStream("localStream1"); // TODO: Use stream name to close the correct stream in case of multiple sources

        easyrtc.initMediaSource(
            localVideoStreamSuccess,
            localVideoStreamError,
            "localStream1");

    }else{
        console.warn("Not connected to WebRTC... Can't update!");
    }
}

function localVideoStreamSuccess(stream){
    console.log("Got local video stream - " + stream.streamName);
    if (stream.active){
        easyrtc.setVideoObjectSrc(getVideoWidget(true,1)[0], stream);
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

            for (let i=0; i<remoteStreams.length; i++){
                easyrtc.addStreamToCall(remoteStreams[i].peerid, 'localStream1', function () {
                    easyrtc.renegotiate(remoteStreams[i].peerid);
                })
                easyrtc.renegotiate(remoteStreams[i].peerid);
            }
        }else{
            // New stream
            localStreams.push(infos);
            console.log("Connecting to session...");
            easyrtc.connect("TeraPlus", signalingLoginSuccess, signalingLoginFailure);
        }

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
    console.log("Sending contact info to :",peerid_target);
    console.log(localContact.uuid + " - " + localContact.name);
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
    for(let peerid in occupants) {
        if (peerid !== local_peerid){
            if (needToCallOtherUsers) {
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
    needToCallOtherUsers = false;
}

function newStreamStarted(callerid, stream, streamname) {
    console.log("New Stream from " + callerid + " - Stream " + streamname);

    /*if (isWeb){
        // Stops calling sound
        document.getElementById("audioCalling").pause();
    }*/

    // Check if already have a stream with that name from that source
    let slot = getStreamIndexForPeerId(callerid);
    //if (streamname=="default"){
    /*for (let i = 0; i < remoteStreams.length; i++) {
        if (remoteStreams[i].peerid === callerid) {
            console.warn("Stream already present for that source. Replacing.");
            slot = i;
            break;
        }
    }*/
    //}

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
        setTitle(false, slot, remoteContacts[contact_index].name);
    }

    /*if (isWeb){
        // Starts connected sound
        document.getElementById("audioConnected").play()
    }*/
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

    let request = {"peerid": local_peerid,
        "micro": isStatusIconActive(true, 1, "Mic"),
        "micro2":isStatusIconActive(true, 2, "Mic"),
        "speaker": isStatusIconActive(true, 1, "Speaker"),
        "video": isStatusIconActive(true, 1, "Video")};

    if (easyrtc.webSocketConnected){
        easyrtc.sendDataWS(callerid, 'updateStatus', request, function(ackMesg) {
            //console.error("ackMsg:",ackMesg);
            if( ackMesg.msgType === 'error' ) {
                console.error(ackMesg.msgData.errorText);
            }
        });
    }

    // Add second video, if present
    /*if (isElementVisible("selfVideo2")){
        console.log("Adding secondary video...");
        easyrtc.addStreamToCall(callerEasyrtcid, "miniVideo");
    }

    // Check if we need to display the remove video icon
    if (streamname=="miniVideo"){
        showElement(getRemoveVideoIconId(slot));
        hideElement(getAddVideoIconId(slot));
    }else{
    }*/

    //updateRemoteContactsInfos();

}
/*
function updateRemoteContactsInfos(){
    console.log("updateRemoteContactsInfos");
    // Find target id to update
    // Count number of streams for each contacts
    // let streams = [];
    // for (let i=0; i<remoteContacts.length; i++){
    //     streams[i] = 0;
    //     for (let j=0; j<4; j++){
    //         if (peerids[j] === remoteContacts[i].peerid){
    //             streams[i] = streams[i] + 1;
    //         }
    //     }
    // }

    for (let i=0; i<remoteContacts.length; i++){
        for (let j=0; j<4; j++){
            if (peerids[j] === remoteContacts[i].peerid){
                console.log("Found at " + j);
                setTitle(false, j+1, remoteContacts[i].name);

                // TODO: REVISE!
                // if (remoteContacts[i].ptz != undefined){
                //     // Set PTZ icon
                //     zoom_tag = "zoomButtons" + j;
                //     presets_tag = "presetButtons" + j;
                //     settings_tag = "settingsButton" + j;
                //
                //     showElement(zoom_tag);
                //     showElement(settings_tag);
                //
                //     // Update display
                //     if (remoteContacts[i].ptz.zoom)
                //         showElement(zoom_tag);
                //     else
                //         hideElement(zoom_tag);
                //
                //     if (remoteContacts[i].ptz.presets)
                //         showElement(presets_tag);
                //     else
                //         hideElement(presets_tag);
                //
                //     if (remoteContacts[i].ptz.settings)
                //         showElement(settings_tag);
                //     else
                //         hideElement(settings_tag);
                // }
                //
                // var addIcon = getAddVideoIconId(j);
                // var removeIcon = getRemoveVideoIconId(j);
                //
                // if (streams[i]==1){
                //
                //     if (remoteContacts[i].capabilities != undefined){
                //         // Set secondary camera capability
                //         if (remoteContacts[i].capabilities.video2){
                //             if (!isElementVisible(removeIcon)){
                //                 showElement(addIcon);
                //             }else{
                //                 hideElement(addIcon);
                //             }
                //         }else{
                //             hideElement(addIcon);
                //         }
                //     }else{
                //         hideElement(addIcon);
                //         hideElement(removeIcon);
                //     }
                // }else{
                //     hideElement(addIcon);
                // }

            }
        }
    }
}*/

function streamDisconnected(callerid, mediaStream, streamName){
    // Find video slot used by that caller
    let slot = getStreamIndexForPeerId(callerid);

    if (slot === undefined){
        showError("Stream disconnected", callerid  + " currently not displayed. Aborting.", false);
        return;
    }

    console.log ("Stream disconnected: " + callerid + " - Slot " + (slot+1));

    /*if (isWeb){
        // Starts connected sound
        document.getElementById("audioDisconnected").play()
    }*/

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
        setTitle(false, i+1, remoteContacts[i].name)
    }

    updateUserRemoteViewsLayout(remoteStreams.length);
    updateUserLocalViewLayout(localStreams.length, remoteStreams.length);
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

function getStreamIndexForPeerId(peerid){
    for (let i=0; i<remoteStreams.length; i++){
        if (remoteStreams[i].peerid === peerid)
            return i;
    }
    return undefined;
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
        let stream_index = getStreamIndexForPeerId(sendercid);
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
        let index = getStreamIndexForPeerId(sendercid);
        let contact_index = getContactIndexForPeerId(sendercid);
        if (contact_index === undefined){
            console.log("No contact card yet for that peer - creating one.");
            remoteContacts.push({peerid: sendercid});
            contact_index = remoteContacts.length-1;
        }

        remoteContacts[contact_index].status = msgData;
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

    /*if (isWeb){
        // Starts calling sounds
        document.getElementById("audioCalling").play();
    }*/


}

function signalingLoginFailure(errorCode, message) {

    showError("signalingLoginFailure", "Can't connect to signaling server! Code: " + errorCode +" - " + message);
    //easyrtc.showError(errorCode, message);
}