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
            if (isCurrentCameraPTZ())
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
            if (isCurrentCameraPTZ())
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
            if (isCurrentCameraPTZ())
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
            if (isCurrentCameraPTZ())
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
            if (isCurrentCameraPTZ()) {
                if (event.shiftKey && event.ctrlKey)
                    SharedObject.setPresetClicked(localContact.uuid, preset);
                else
                    SharedObject.gotoPresetClicked(localContact.uuid, preset);
            }
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
            if (isCurrentCameraPTZ())
                SharedObject.camSettingsClicked(localContact.uuid);
    }else{
        let request = {"uuid": localContact.uuid};
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
    let request;
    if (local === true) {
        if (teraConnected) {
            if (isCurrentCameraPTZ()) {
                let x = (event.clientX - bar_width);
                let y = (event.clientY - bar_height);
                if (x < 0 || x > real_video_width || y < 0 || y > real_video_height)
                    return; // Click outside the displayed video
                //console.log("Local PTZ request - x=" + x + ", y=" + y + ", w=" + real_video_width + ", h=" + real_video_height);
                SharedObject.imageClicked(localContact.uuid, x, y, real_video_width, real_video_height);
            }
        }
    } else {
        // Send message to the other client
        console.log("PTZ request to :", remoteStreams[index - 1].peerid);
        //send contact information to other users
        //request = {"x":event.clientX - offsets.left, "y": event.clientY - offsets.top, "w":video.clientWidth, "h": video.clientHeight};
        request = {
            "x": event.clientX - bar_width - offsets.left,
            "y": event.clientY - bar_height,
            "w": real_video_width,
            "h": real_video_height,
            "streamname": remoteStreams[index - 1].streamname
        };
        if (easyrtc.webSocketConnected) {
            easyrtc.sendDataWS(remoteStreams[index - 1].peerid, 'PTZRequest', request, function (ackMesg) {
                //console.error("ackMsg:",ackMesg);
                if (ackMesg.msgType === 'error') {
                    console.error(ackMesg.msgData.errorText);
                }
            });
        }

    }
}

function setPTZCapabilities(uuid, zoom, presets, settings, camera = undefined){
    let ptz = {'uuid':uuid, 'zoom':zoom,'presets':presets,'settings':settings, 'camera':camera};

    console.log("Setting PTZ Capabilities on camera: " + camera + ", uuid = " + uuid + " = " + zoom + " " + presets + " " + settings);

    if (uuid === 0){
        console.warn("setPTZCapabilities -- UUID = 0, not valid!", false);
        return;
    }

    if (uuid === localContact.uuid || (localContact.uuid === undefined && !isWeb)){
        console.log(" -- Local UUID - settings values.");
        // Setting local capabilities
        localPTZCapabilities = ptz;

        // Show buttons
        showPTZControls(true, 1, zoom, presets, settings, camera);

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

function isCurrentCameraPTZ() {
    if (localPTZCapabilities === undefined)
        return false;
    if (currentConfig['currentVideoSourceIndex'] >= 0 && currentConfig['currentVideoSourceIndex'] < videoSources.length) {
        if ((localPTZCapabilities.camera === undefined && (localPTZCapabilities.zoom === true ||
            localPTZCapabilities.presets === true || localPTZCapabilities.settings === true))||
            videoSources[currentConfig['currentVideoSourceIndex']].label === localPTZCapabilities.camera){
            return true;
        }
    }

    return false;
}
