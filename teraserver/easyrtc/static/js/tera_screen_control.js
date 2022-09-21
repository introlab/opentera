function manageMouseEvent(event, local, index, event_name){
    if (event_name === 'MouseMoveEvent' && event.buttons === 0){
        // Mouse move but no button - ignoring!
        return;
    }
    if (teraConnected && !local){
        // Only handle if using openteraplus and don't do anything if local
        let remote_peer = remoteStreams[index - 1].peerid;
        let remote_contact = remoteContacts[getContactIndexForPeerId(remote_peer)];
        if (remote_contact.capabilities.screenControl){
            let video = getVideoWidget(local, index);
            if (!video.length){
                console.error(event_name + ": Can't find video!");
                return;
            }

            video = video[0];
            const offsets = video.getBoundingClientRect();

            const video_dims = calculateContainsWindow(video);
            const real_video_width = (video.clientWidth * video_dims.destinationWidthPercentage);
            const bar_width = (video.clientWidth - real_video_width) / 2;

            const real_video_height = (video.clientHeight * video_dims.destinationHeightPercentage);
            const bar_height = (video.clientHeight - real_video_height) / 2;

            console.log(event_name + " to :", remote_peer);

            let request = {
                "x": event.clientX - bar_width - offsets.left,
                "y": event.clientY - bar_height,
                "w": real_video_width,
                "h": real_video_height,
                "streamname": remoteStreams[index - 1].streamname
            };
            if (easyrtc.webSocketConnected) {
                easyrtc.sendDataWS(remote_peer, event_name, request, function (ackMesg) {
                    //console.error("ackMsg:",ackMesg);
                    if (ackMesg.msgType === 'error') {
                        console.error(ackMesg.msgData.errorText);
                    }
                });
            }
        }
    }
}

function manageKeyEvent(event, local, index, event_name){
    if (teraConnected && !local){
        // Only handle if using openteraplus and don't do anything if local
        let remote_peer = remoteStreams[index - 1].peerid;
        let remote_contact = remoteContacts[getContactIndexForPeerId(remote_peer)];
        if (remote_contact.capabilities.screenControl){
            let request = {
                "key": event.key,
                "alt": event.alt_Key,
                "ctrl": event.ctrlKey,
                "shift": event.shifKey,
                "streamname": remoteStreams[index - 1].streamname
            };
            if (easyrtc.webSocketConnected) {
                easyrtc.sendDataWS(remote_peer, event_name, request, function (ackMesg) {
                    //console.error("ackMsg:",ackMesg);
                    if (ackMesg.msgType === 'error') {
                        console.error(ackMesg.msgData.errorText);
                    }
                });
            }
        }
    }
}
