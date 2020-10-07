let localTimerHandles = [0, 0];
let remoteTimerHandles = [0, 0, 0, 0];

function resetInactiveTimer(local, index){
    stopInactiveTimer(local, index);

    let timerHandle = setTimeout(inactiveTimeout, 3000, local, index);
    if (local === true){
        localTimerHandles[index-1] = timerHandle;
    }else{
        remoteTimerHandles[index-1] = timerHandle;
    }
}

function stopInactiveTimer(local, index){
    let timerHandle = (local===true) ? localTimerHandles[index-1] : remoteTimerHandles[index-1];
    if (timerHandle !== 0){
        clearTimeout(timerHandle);
        (local===true) ? localTimerHandles[index-1] = 0 : remoteTimerHandles[index-1] = 0;
    }
}

function showButtons(local, show, index){
    let view_prefix = ((local === true) ? 'local' : 'remote');
    let ptzControls = $("#" + view_prefix + "PtzControls" + index);
    let srcControls = $("#" + view_prefix + "SourcesControls" + index);
    let statusControls = $("#" + view_prefix + "ViewControls" + index)

    if (ptzControls.length){
        (show === true) ? ptzControls.show() : ptzControls.hide();
    }
    if (srcControls.length){
        (show === true) ? srcControls.show() : srcControls.hide();
    }
    if (statusControls.length){
        // Must hide individual icons according to state
        let micIcon = getStatusIcon(local, index, "Mic");
        let videoIcon = getStatusIcon(local, index, "Video");
        let configIcon = $("#" + view_prefix + "Config" + index);
        let speakerIcon = getStatusIcon(local, index, "Speaker");

        if (micIcon.length){
            let iconActive = isStatusIconActive(local, index, "Mic");
            if (iconActive === true){
                (show === true) ? micIcon.show() : micIcon.hide();
            }else{
                micIcon.show();
            }
        }

        if (videoIcon.length){
            let iconActive = isStatusIconActive(local, index, "Video");
            if (iconActive === true){
                (show === true) ? videoIcon.show() : videoIcon.hide();
            }else{
                videoIcon.show();
            }
        }

        if (speakerIcon.length){
            let iconActive = isStatusIconActive(local, index, "Speaker");
            if (iconActive === true){
                (show === true) ? speakerIcon.show() : speakerIcon.hide();
            }else{
                speakerIcon.show();
            }
        }
        if (configIcon.length){
            (show === true) ? configIcon.show() : configIcon.hide();
        }
    }

}

function inactiveTimeout(local, index){
    stopInactiveTimer(local, index);
    showButtons(local, false, index);
}

function showAllButtons(show){
    showButtons(true, show, 1);
    showButtons(true, show, 2);
    showButtons(false, show, 1);
    showButtons(false, show, 2);
    showButtons(false, show,3);
    showButtons(false, show,4);
}

function showSecondaryLocalSourcesIcons(show_add_button, show_remove_button){
    (show_add_button) ? showElement('imgAddLocalVideo2') : hideElement('imgAddLocalVideo2');
    (show_remove_button) ? showElement('imgRemoveLocalVideo2') : hideElement('imgRemoveLocalVideo2');
}

function showLocalVideoMirror(mirror){
    (mirror === true) ? $('#localVideo1').addClass('easyrtcMirror') : $('#localVideo1').removeClass('easyrtcMirror');
}

function hideElement(id){
    $("#"+id).hide();
}

function showElement(id){
    $("#"+id).show();
}

function getStatusIcon(local, index, prefix){
    let view_prefix = ((local === true) ? 'local' : 'remote');
    return $("#" + view_prefix + prefix + "Status" + index);
}

function getVideoWidget(local, index){
    let view_prefix = ((local === true) ? 'local' : 'remote');
    return $("#" + view_prefix + "Video" + index);
}

function isStatusIconActive(local, index, prefix){
    let icon = getStatusIcon(local, index, prefix);
    return !icon.attr('src').includes("off");
}

function updateStatusIconState(status, local, index, prefix){
    let icon = getStatusIcon(local, index, prefix);

    let iconImgPath = icon.attr('src').split('/')

    if (status === true){
        iconImgPath[iconImgPath.length-1] = prefix.toLowerCase() + ".png";
    }else{
        iconImgPath[iconImgPath.length-1] = prefix.toLowerCase() + "_off.png";
    }
    icon.attr('src', pathJoin(iconImgPath))
}

function swapViews(){
    console.warn('SwapViews: Feature not currently enabled.');

}

function setConfigDialogValues(audios, videos, config){
    // Main video source selector
    let videoSelect = $('#videoSelect')[0];
    videoSelect.options.length = 0;

    // Main audio source selector
    let audioSelect = $('#audioSelect')[0];
    audioSelect.options.length = 0;

    // Secondary video source selector
    let videoSelect2 = $('#videoSelect2')[0];
    videoSelect2.options.length = 0;
    videoSelect2.options[videoSelect2.options.length] = new Option("Aucune", "0");

    // Secondary audio source selector
    let audioSelect2 = $('#audioSelect2')[0];;
    audioSelect2.options.length = 0;
    audioSelect2.options[audioSelect2.options.length] = new Option("Aucune", "0");

    // Mirror toggle
    let mirrorCheck = $('#mirrorCheck')[0];
    mirrorCheck.checked = currentConfig['video1Mirror'];

    // Fill lists
    audios.forEach(audio => {
            let name = audio.label;
            if (name === "") name = audio.deviceId;
            audioSelect.options[audioSelect.options.length] = new Option(name.substr(0,50), audio.deviceId);
            audioSelect2.options[audioSelect2.options.length] = new Option(name.substr(0,50), audio.deviceId);
    });

    videos.forEach(video => {
        let name = video.label;
        if (name === "") name = video.deviceId;
        videoSelect.options[videoSelect.options.length] = new Option(name.substr(0,50), video.deviceId);
        videoSelect2.options[videoSelect2.options.length] = new Option(name.substr(0,50), video.deviceId);
    });

    videoSelect.selectedIndex = config['currentVideoSourceIndex'];
    videoSelect2.selectedIndex = config['currentVideoSource2Index']+1;
    audioSelect.selectedIndex = config['currentAudioSourceIndex'];
    audioSelect2.selectedIndex = config['currentAudioSource2Index']+1;

}

function showError(err_context, err_msg, ui_display){
    console.error(err_context + ": " + err_msg);

    // TODO: Display in UI
}


function setTitle(local, index, title){
    let view_prefix = ((local === true) ? 'local' : 'remote');
    let label = $('#' + view_prefix + 'ViewTitle' + index);
    if (label.length){
        label[0].innerText = title;
    }
}