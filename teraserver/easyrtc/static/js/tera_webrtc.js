// WebRTC ids
var local_peerid = "0";
var peerids = ["0", "0", "0", "0"]; // Remote peer ids
var peers_uuids_mapping = {} // OpenTera UUID - Peer ID mapping

// Contact cards
var localContact = {};
var remoteContacts = []; // Used to store informations about everyone that has connected (contactinfos)

// Status / controls variables
var connected = false;
var needToCallOtherUsers = false;
let remoteStreamsCount = 0;
let localStreamsCount = 0;


function initSystem(){
    let urlParams = new URLSearchParams(window.location.search);
    isWeb = (urlParams.get('source') == 'web');

    let port = getTeraPlusPort(); // This function is rendered in the main html document
    let websocket_path =  "/websocket/" + port
    easyrtc.setSocketUrl(window.location.origin, {path: websocket_path});

    deviceEnumCompleted = false;
    initialSourceSelect	=false;

    let local_uuid = urlParams.get('uuid');
    if (local_uuid)
        localContact.uuid = local_uuid;

    let local_name = urlParams.get('name');
    if (local_name)
        localContact.name = local_name;

    // Initialize
    if (!isWeb){
        // Connect Shared Object websocket
        include("qrc:///qtwebchannel/qwebchannel.js");
        connectSharedObject();
    }
    fillDefaultSourceList();
    connect();
}

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
    // SB - TODO - REFACTORING HERE 07/10/2020
    easyrtc.setOnStreamClosed(streamDisconnected);
    easyrtc.setPeerListener(dataReception);

    //Post-connect Event listeners
    //easyrtc.setOnHangup(streamDisconnected);
    //easyrtc.setOnCall(newStreamStarted);

    connected = true;
    updateLocalAudioVideoSource();
}

function muteMicro(local, index){
    let new_state = !isStatusIconActive(local, index, "Mic");

    updateStatusIconState(new_state, local, index, "Mic");

    let micro_value = (new_state === true) ? "true" : "false";

    if (local === true){
        // Send display update request
        let request = {"peerid": local_peerid, micro:micro_value};
        easyrtc.enableMicrophone(new_state, "localStream" + index);

        //console.log(request);
        if (easyrtc.webSocketConnected) {
            easyrtc.sendDataWS("default", 'updateStatus', request,
                function (ackMesg) {
                if (ackMesg.msgType === 'error') {
                    console.error(ackMesg.msgData.errorText);
                }
            });
        }
    }else{
        // Request mute to someone else
        let request = {"index": 1}; // TODO: Manage multiple remote streams??
        if (easyrtc.webSocketConnected){
            easyrtc.sendDataWS( peerids[index-1], 'muteMicro', request,
                function(ackMesg) {
                //console.error("ackMsg:",ackMesg);
                if( ackMesg.msgType === 'error' ) {
                    console.error(ackMesg.msgData.errorText);
                }
            });
        }
    }
}

function muteVideo(local, index){
    let new_state = !isStatusIconActive(local, index, "Video");

    updateStatusIconState(new_state, local, index, "Video");

    let video_value = (new_state === true) ? "true" : "false";

    if (local === true){
        // Send display update request
        let request = {"peerid": local_peerid, video: video_value};

        // TODO
        //easyrtc.enableMicrophone(new_state, "localStream" + index);

        if (easyrtc.webSocketConnected) {
            easyrtc.sendDataWS("default", 'updateStatus', request,
                function (ackMesg) {
                    if (ackMesg.msgType === 'error') {
                        console.error(ackMesg.msgData.errorText);
                    }
                });
        }
    }else{
        // Request video mute to someone else
        let request = {"index": 1}; // TODO: Manage multiple remote streams??
        if (easyrtc.webSocketConnected){
            easyrtc.sendDataWS( peerids[index-1], 'muteVideo', request,
                function(ackMesg) {
                    //console.error("ackMsg:",ackMesg);
                    if( ackMesg.msgType === 'error' ) {
                        console.error(ackMesg.msgData.errorText);
                    }
                });
        }
    }
}

function muteSpeaker(local, index){
    let new_state = !isStatusIconActive(local, index, "Speaker");

    updateStatusIconState(new_state, local, index, "Speaker");

    let speaker_value = (new_state === true) ? "true" : "false";

    if (local === true){
        // Send display update request
        let request = {"peerid": local_peerid, speaker: speaker_value};

        // TODO
        //easyrtc.enableMicrophone(new_state, "localStream" + index);

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
        let request = {"index": 1}; // TODO: Manage multiple remote streams??
        if (easyrtc.webSocketConnected){
            easyrtc.sendDataWS( peerids[index-1], 'muteSpeaker', request,
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
    let mirror_value = (mirror === true) ? "true" : "false";

    if (local === true){
        // Send display update request
        let request = {"peerid": local_peerid, mirror: mirror_value};

        showLocalVideoMirror(mirror);

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
        let request = {"index": 1}; // TODO: Manage multiple remote streams??
        if (easyrtc.webSocketConnected){
            easyrtc.sendDataWS( peerids[index-1], 'setMirror', request,
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
    console.log("updateLocalVideoSource");
    if (connected === true){
        console.log("Updating local video source...");
        easyrtc.disconnect();

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
        easyrtc.closeLocalMediaStream();
        //easyrtc.renegotiate();
        easyrtc.initMediaSource(
            localVideoStreamSuccess,
            localVideoStreamError,
            "localStream1");
    }else{
        console.warn("Not connected to WebRTC... Can't update!");
    }
}

function localVideoStreamSuccess(stream){
    if (stream.active){
        easyrtc.setVideoObjectSrc(getVideoWidget(local,1)[0], stream);
        console.log("Connecting to session...");
        easyrtc.connect("TeraPlus", loginSuccess, loginFailure);
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
        if (settings.uuid in peers_uuids_mapping){
            let peer_id = peers_uuids_mapping[settings.uuid];
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
    let shownVideos = 0;
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
    let slot = -1;
    //if (streamname=="default"){
    for (let i = 0; i < 4; i++) {
        if (peerids[i] === callerid) {
            console.warn("Stream already present for that source. Replacing.");
            slot = i;
            break;
        }
    }
    //}

    // Find first empty slot
    if (slot === -1){
        if (remoteStreamsCount+1 > 4) {
            showError("newStreamStarted", "New stream received, but not slot available!", true);
            return;
        }
        remoteStreamsCount += 1;
        slot = remoteStreamsCount;
    }

    console.log ("Assigning to slot " + slot);

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

    peerids[slot] = callerid;
    easyrtc.setVideoObjectSrc(getVideoWidget(false, slot)[0], stream);

    // Update display
    updateUserRemoteViewsLayout(remoteStreamsCount);
    updateUserLocalViewLayout(localStreamsCount, remoteStreamsCount);

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

    updateRemoteContactsInfos();

}

function updateRemoteContactsInfos(){
    // Find target id to update
    // Count number of streams for each contacts
    /*let streams = [];
    for (let i=0; i<remoteContacts.length; i++){
        streams[i] = 0;
        for (let j=0; j<4; j++){
            if (peerids[j] === remoteContacts[i].peerid){
                streams[i] = streams[i] + 1;
            }
        }
    }*/
    for (let i=0; i<remoteContacts.length; i++){
        for (let j=0; j<4; j++){
            if (peerids[j] === remoteContacts[i].peerid){
                //console.log("Found at " + j);
                peers_uuids_mapping[remoteContacts[i].uuid] = remoteContacts[i].peerid;
                setTitle(false, j+1, remoteContacts[i].name);

                // TODO: REVISE!
               /* if (remoteContacts[i].ptz != undefined){
                    // Set PTZ icon
                    zoom_tag = "zoomButtons" + j;
                    presets_tag = "presetButtons" + j;
                    settings_tag = "settingsButton" + j;

                    showElement(zoom_tag);
                    showElement(settings_tag);

                    // Update display
                    if (remoteContacts[i].ptz.zoom)
                        showElement(zoom_tag);
                    else
                        hideElement(zoom_tag);

                    if (remoteContacts[i].ptz.presets)
                        showElement(presets_tag);
                    else
                        hideElement(presets_tag);

                    if (remoteContacts[i].ptz.settings)
                        showElement(settings_tag);
                    else
                        hideElement(settings_tag);
                }

                var addIcon = getAddVideoIconId(j);
                var removeIcon = getRemoveVideoIconId(j);

                if (streams[i]==1){

                    if (remoteContacts[i].capabilities != undefined){
                        // Set secondary camera capability
                        if (remoteContacts[i].capabilities.video2){
                            if (!isElementVisible(removeIcon)){
                                showElement(addIcon);
                            }else{
                                hideElement(addIcon);
                            }
                        }else{
                            hideElement(addIcon);
                        }
                    }else{
                        hideElement(addIcon);
                        hideElement(removeIcon);
                    }
                }else{
                    hideElement(addIcon);
                }*/

            }
        }
    }
}