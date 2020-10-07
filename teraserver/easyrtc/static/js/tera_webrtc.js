let local_peerid = "0";
let peerids = ["0", "0", "0", "0"]; // Remote peer ids

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
