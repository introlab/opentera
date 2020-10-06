let peerids = ["0", "0", "0", "0", "0"]; //0 = Local, 1,2,3,4... = distants

function muteMicro(local, index){
    let new_state = !isMicIconActive(local, index);

    updateMicIconState(new_state, local, index);

    let micro_value = "false";
    if (new_state === true)
        micro_value = "true";

    if (local === true){
        // Send display update request
        let request = {"peerid": peerids[index], micro:micro_value};

        if (index==0)
            easyrtc.enableMicrophone(new_state);
        else
            easyrtc.enableMicrophone(new_state, "miniVideo");

        //console.log(request);
        if (easyrtc.webSocketConnected) {
            easyrtc.sendDataWS({"targetRoom": "default"}, 'updateStatus', request,
                function (ackMesg) {
                if (ackMesg.msgType === 'error') {
                    console.error(ackMesg.msgData.errorText);
                }
            });
        }
    }else{
        // Request mute to someone else
        let request = {"index": index};
        if (easyrtc.webSocketConnected){
            easyrtc.sendDataWS( peerids[index], 'muteMicro', request,
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
    let new_state = !isVideoIconActive(local, index);

    updateVideoIconState(new_state, local, index);

    let video_value = "false";
    if (new_state === true)
        video_value = "true";

    if (local === true){
        // Send display update request
        let request = {"peerid": peerids[index], video: video_value};

        // TODO
        /*if (index==0)
            easyrtc.enableMicrophone(new_state);
        else
            easyrtc.enableMicrophone(new_state, "miniVideo");

        //console.log(request);
        if (easyrtc.webSocketConnected) {
            easyrtc.sendDataWS({"targetRoom": "default"}, 'updateStatus', request,
                function (ackMesg) {
                    if (ackMesg.msgType === 'error') {
                        console.error(ackMesg.msgData.errorText);
                    }
                });
        }*/
    }else{
        // Request video mute to someone else
        let request = {"index": index};
        if (easyrtc.webSocketConnected){
            easyrtc.sendDataWS( peerids[index], 'muteVideo', request,
                function(ackMesg) {
                    //console.error("ackMsg:",ackMesg);
                    if( ackMesg.msgType === 'error' ) {
                        console.error(ackMesg.msgData.errorText);
                    }
                });
        }
    }
}
