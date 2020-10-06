let timerHandle = 0;

function resetInactiveTimer(){
    stopInactiveTimer();

    timerHandle = setTimeout(inactiveTimeout, 3000);
}

function stopInactiveTimer(){
    if (timerHandle != 0){
        clearTimeout(timerHandle);
        timerHandle = 0;
    }
}

function showButtons(view_prefix, show){
    let ptzControls = $("#" + view_prefix + "PtzControls");
    let srcControls = $("#" + view_prefix + "SourcesControls");

    if (ptzControls.length){
        if (show === true)
            ptzControls.show();
        else
            ptzControls.hide();
    }

    if (srcControls.length){
        if (show === true)
            srcControls.show();
        else
            srcControls.hide();
    }

}

function inactiveTimeout(){
    stopInactiveTimer();
    showButtons('local', false);
    showButtons('remote1', false);
    showButtons('remote2', false);
    showButtons('remote3', false);
    showButtons('remote4', false);
}

function hideElement(id){
    $("#"+id).hide();
}

function showElement(id){
    $("#"+id).show();
}

// ***** MICROPHONE *****
function getMicIcon(local, index){
    let local_str = 'remote';
    if (local === true)
        local_str = 'local';
    return $("#" + local_str + "MicStatus" + index);
}

function isMicIconActive(local, index){
    let micIcon = getMicIcon(local, index);
    return !micIcon.attr('src').includes("off");
}

function updateMicIconState(status, local, index){
    let micIcon = getMicIcon(local, index);
    let videoWidget = getVideoWidget(local, index);

    videoWidget.micEnabled = status;

    let micImgPath = micIcon.attr('src').split('/')

    if (videoWidget.micEnabled){
        micImgPath[micImgPath.length-1] = "micro.png";
    }else{
        micImgPath[micImgPath.length-1] = "micro_off.png";
    }
    micIcon.attr('src', pathJoin(micImgPath))
}

// ***** VIDEO *****
function getVideoWidget(local, index){
    let local_str = 'remote';
    if (local === true)
        local_str = 'local';
    return $("#" + local_str + "Video" + index);
}

function getVideoIcon(local, index){
    let local_str = 'remote';
    if (local === true)
        local_str = 'local';
    return $("#" + local_str + "VideoStatus" + index);
}

function isVideoIconActive(local, index){
    let videoIcon = getVideoIcon(local, index);
    return !videoIcon.attr('src').includes("off");
}

function updateVideoIconState(status, local, index){
    let videoIcon = getVideoIcon(local, index);

    let videoImgPath = videoIcon.attr('src').split('/')

    if (status === true){
        videoImgPath[videoImgPath.length-1] = "video.png";
    }else{
        videoImgPath[videoImgPath.length-1] = "video_off.png";
    }
    videoIcon.attr('src', pathJoin(videoImgPath))
}
