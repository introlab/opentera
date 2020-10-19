let debounceWheel = 0;
var localPTZCapabilities = {'uuid':0, 'zoom':false,'presets':false,'settings':false};
var remotePTZCapabilities = [{}];

function managePTZMouseWheel(event, local, index){
    // Ignore events for 500 ms
    let currentTime = Date.now();

    if (currentTime > debounceWheel){
        if (event.deltaY > 0){
            zoomOut(local, index);
        }else{
            zoomIn(local, index);
        }
        debounceWheel = currentTime + 500;
    }
}

function zoomIn(local, index){
    if (local === true){
        if (teraConnected)
            SharedObject.zoomInClicked(localContact.uuid);
    }else{
        let request = {"value":"in"};
        if (easyrtc.webSocketConnected) {
            easyrtc.sendDataWS(remoteStreams[index-1].peerid, 'ZoomRequest', request, function (ackMesg) {
                //console.error("ackMsg:",ackMesg);
                if (ackMesg.msgType === 'error') {
                    console.error(ackMesg.msgData.errorText);
                }
            });
        }

    }
    resetInactiveTimer();
}

function zoomOut(local, index){
    if (local === true){
        if (teraConnected)
            SharedObject.zoomOutClicked(localContact.uuid);
    }else{
        let request = {"value":"out"};
        if (easyrtc.webSocketConnected) {
            easyrtc.sendDataWS(remoteStreams[index-1].peerid, 'ZoomRequest', request, function (ackMesg) {
                //console.error("ackMsg:",ackMesg);
                if (ackMesg.msgType === 'error') {
                    console.error(ackMesg.msgData.errorText);
                }
            });
        }

    }
    resetInactiveTimer();
}

function zoomMin(local, index){
    if (local === true){
        if (teraConnected)
            SharedObject.zoomMinClicked(localContact.uuid);
    }else{
        let request = {"value":"min"};
        if (easyrtc.webSocketConnected) {
            easyrtc.sendDataWS(remoteStreams[index-1].peerid, 'ZoomRequest', request, function (ackMesg) {
                //console.error("ackMsg:",ackMesg);
                if (ackMesg.msgType === 'error') {
                    console.error(ackMesg.msgData.errorText);
                }
            });
        }
    }
}

function zoomMax(local, index){
    if (local === true){
        if (teraConnected)
            SharedObject.zoomMaxClicked(localContact.uuid);
    }else{
        let request = {"value":"max"};
        if (easyrtc.webSocketConnected) {
            easyrtc.sendDataWS(remoteStreams[index-1].peerid, 'ZoomRequest', request, function (ackMesg) {
                //console.error("ackMsg:",ackMesg);
                if (ackMesg.msgType === 'error') {
                    console.error(ackMesg.msgData.errorText);
                }
            });
        }
    }
}

function gotoPreset(event, local, index, preset){
    console.log("gotoPreset: local: " + local + ", index: " + index + ", preset: " + preset +
        ", shift: " + event.shiftKey + ", ctrl: " + event.ctrlKey);
    if (local === true){
        if (teraConnected){
            if (event.shiftKey && event.ctrlKey)
                SharedObject.setPresetClicked(localContact.uuid, preset);
            else
                SharedObject.gotoPresetClicked(localContact.uuid, preset);
        }
    }else{
        let set = false;
        if (event.shiftKey && event.ctrlKey)
            set = true;
        let request = {"preset": preset, "set": set};
        if (easyrtc.webSocketConnected) {
            easyrtc.sendDataWS(remoteStreams[index-1].peerid, 'PresetRequest', request, function (ackMesg) {
                //console.error("ackMsg:",ackMesg);
                if (ackMesg.msgType === 'error') {
                    console.error(ackMesg.msgData.errorText);
                }
            });
        }

    }
}

function camSettings(local, index){
    if (local === true){
        if (teraConnected)
            SharedObject.camSettingsClicked(uuids[index]);
    }else{
        let request = "";
        if (easyrtc.webSocketConnected) {
            easyrtc.sendDataWS(remoteStreams[index-1].peerid, 'CamSettingsRequest', request, function (ackMesg) {
                //console.error("ackMsg:",ackMesg);
                if (ackMesg.msgType === 'error') {
                    console.error(ackMesg.msgData.errorText);
                }
            });
        }

    }
}

function managePTZClickEvent(event, local, index){
    let video = getVideoWidget(local, index);
    if (!video.length){
        console.error("managePTZClickEvent: Can't find video!");
        return;
    }
    video = video[0];
    const offsets = video.getBoundingClientRect();

    const video_dims = calculateContainsWindow(video);
    const real_video_width = (video.clientWidth * video_dims.destinationWidthPercentage);
    const bar_width = (video.clientWidth - real_video_width) / 2;

    const real_video_height = (video.clientHeight * video_dims.destinationHeightPercentage);
    const bar_height = (video.clientHeight - real_video_height) / 2;

    //alert("x=" + (event.clientX - offsets.left) + " y=" + (event.clientY - offsets.top) + " w=" + video.clientWidth + " h=" + video.clientHeight);
    if (local === true){
        if (teraConnected){
            console.log("Local PTZ request");
            //SharedObject.imageClicked(localContact.uuid, video.clientWidth - (event.clientX - offsets.left), event.clientY - offsets.top, video.clientWidth, video.clientHeight);
            SharedObject.imageClicked(localContact.uuid, (event.clientX - bar_width), event.clientY - bar_height, real_video_width, real_video_height);
            // Uncomment next line if using mirror image!
            //SharedObject.imageClicked(localContact.uuid, (event.clientX - offsets.left), event.clientY - offsets.top, video.clientWidth, video.clientHeight);
        }
    }else{
        // Send message to the other client
        console.log("PTZ request to :", remoteStreams[index-1].peerid);
        //send contact information to other users
        //request = {"x":event.clientX - offsets.left, "y": event.clientY - offsets.top, "w":video.clientWidth, "h": video.clientHeight};
        request = {"x": event.clientX - bar_width - offsets.left, "y": event.clientY - bar_height, "w": real_video_width, "h": real_video_height};
        if (easyrtc.webSocketConnected){
            easyrtc.sendDataWS( remoteStreams[index-1].peerid, 'PTZRequest', request, function(ackMesg) {
                //console.error("ackMsg:",ackMesg);
                if( ackMesg.msgType === 'error' ) {
                    console.error(ackMesg.msgData.errorText);
                }
            });
        }

    }
}

function setPTZCapabilities(uuid, zoom, presets, settings){
    let ptz = {'uuid':uuid, 'zoom':zoom,'presets':presets,'settings':settings};

    console.log("Setting PTZ Capabilities: " + uuid + " = " + zoom + " " + presets + " " + settings);

    if (uuid === 0){
        console.warn("setPTZCapabilities -- UUID = 0, not valid!", false);
        return;
    }

    if (uuid === localContact.uuid || (localContact.uuid === undefined && !isWeb)){
        console.log(" -- Local UUID - settings values.");
        // Setting local capabilities
        localPTZCapabilities = ptz;

        // Show buttons
        showPTZControls(true, 1, zoom, presets, settings);

        // Send to remotes
        broadcastlocalPTZCapabilities();

    }else{
        console.log(" -- Remote UUID received: " + uuid + ", I am " + localContact.uuid);
        // Find and update PTZ infos in remoteContacts
        for (let i=0; i<remoteContacts.length; i++){
            if (remoteContacts[i].uuid === uuid){
                remoteContacts[i].ptz = ptz;
                // Show buttons
                showPTZControls(false, i+1, zoom, presets, settings);
                break;
            }
        }
    }

}