let localTimerHandles = [0, 0];
let remoteTimerHandles = [0, 0, 0, 0];

function initUI(){
    $('#configDialog').on('hidden.bs.modal', configDialogClosed);
}

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
        if (show === true){
            (hasPTZControls(local, index)) ? ptzControls.show() : ptzControls.hide();
        }else{
            ptzControls.hide();
        }
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

function showVideoMirror(local, index, mirror){
    let video_widget = getVideoWidget(local, index);
    if (video_widget !== undefined){
        (mirror === true) ? video_widget.addClass('easyrtcMirror') : video_widget.removeClass('easyrtcMirror');
    }
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
        let must_show = false;
        if (local){
            if (localTimerHandles[index-1] !== 0) must_show = true;
        }else{
            if (remoteTimerHandles[index-1] !== 0) must_show = true;
        }
        (!must_show) ? icon.hide() : icon.show();
    }else{
        iconImgPath[iconImgPath.length-1] = prefix.toLowerCase() + "_off.png";
        icon.show();
    }
    icon.attr('src', pathJoin(iconImgPath))
}

function swapViews(){
    console.warn('SwapViews: Feature not currently enabled.');

}

function showError(err_context, err_msg, ui_display){
    console.error(err_context + ": " + err_msg);

    if (ui_display === true){
        $('#errorDialogText')[0].innerHTML = err_msg;
        $('#errorDialog').modal('show')
    }
}

function showStatusMsg(status_msg){
    $('#statusLabel')[0].innerHTML = status_msg;
    $('#statusAlert').show();
}

function clearStatusMsg(){
    $('#statusAlert').hide();
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
    let audioSelect2 = $('#audioSelect2')[0];
    audioSelect2.options.length = 0;
    audioSelect2.options[audioSelect2.options.length] = new Option("Aucune", "0");

    // Mirror toggle
    let mirrorCheck = $('#mirrorCheck')[0];
    mirrorCheck.checked = config['video1Mirror'];

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
    videoSelect2.selectedIndex = config['currentVideoSource2Index'];
    audioSelect.selectedIndex = config['currentAudioSourceIndex'];
    audioSelect2.selectedIndex = config['currentAudioSource2Index'];
}

function configDialogClosed(e){
    // Compare values with current config and apply changes if needed
    let videoSelect = $('#videoSelect')[0];
    let audioSelect = $('#audioSelect')[0];
    let videoSelect2 = $('#videoSelect2')[0];
    let audioSelect2 = $('#audioSelect2')[0];
    let mirrorCheck = $('#mirrorCheck')[0];

    if (videoSelect.selectedIndex !== currentConfig['currentVideoSourceIndex'] ||
        audioSelect.selectedIndex !== currentConfig['currentAudioSourceIndex']){
        // Video and/or audio source changed
        currentConfig['currentVideoSourceIndex'] = videoSelect.selectedIndex;
        currentConfig['currentAudioSourceIndex'] = audioSelect.selectedIndex;
        updateLocalAudioVideoSource();
    }

    if (mirrorCheck.checked !== currentConfig['video1Mirror']){
        // Mirror changed
        currentConfig['video1Mirror'] = mirrorCheck.checked;
        setMirror(currentConfig['video1Mirror'], true, 1);
    }

    if (videoSelect2.selectedIndex !== currentConfig['currentVideoSource2Index']){
        // Video source changed
    }

    if (audioSelect2.selectedIndex !== currentConfig['currentAudioSource2Index']){
        // Audio source changed
    }


}

function setTitle(local, index, title){
    let view_prefix = ((local === true) ? 'local' : 'remote');
    let label = $('#' + view_prefix + 'ViewTitle' + index);
    if (label.length){
        label[0].innerText = title;
    }
}

function showPTZControls(local, index, zoom, presets, settings){
    let view_prefix = ((local === true) ? 'local' : 'remote');
    let zoomControls = $("#" + view_prefix + "ZoomButtons" + index);
    let presetControls = $("#" + view_prefix + "PresetButtons" + index);
    let settingsControl = $("#" + view_prefix + "SettingsButton" + index);

    (zoom === true) ? zoomControls.show() : zoomControls.hide();
    (presets === true) ? presetControls.show() : presetControls.hide();
    (settings === true) ? settingsControl.show() : settingsControl.hide();
}

function hasPTZControls(local, index){
    let view_prefix = ((local === true) ? 'local' : 'remote');
    let zoomControls = $("#" + view_prefix + "ZoomButtons" + index);
    let presetControls = $("#" + view_prefix + "PresetButtons" + index);
    let settingsControl = $("#" + view_prefix + "SettingsButton" + index);

    return zoomControls.css('display') !== 'none' ||
        presetControls.css('display') !== 'none' ||
        settingsControl.css('display') !== 'none';

}

function refreshRemoteStatusIcons(peerid){
    let card_index = getContactIndexForPeerId(peerid);
    let index = getStreamIndexForPeerId(peerid);

    if (card_index === undefined){
        console.log('refreshRemoteStatusIcons - no contact information for ' + peerid);
        return;
    }

    if (index === undefined){
        console.log('refreshRemoteStatusIcons - no stream for ' + peerid);
        return;
    }

    let status = remoteContacts[card_index].status;

    if (status.micro !== undefined) {
        updateStatusIconState(status.micro, false, index + 1, "Mic");
    }

    /*if (msgData.micro2 !== undefined){
        let index = getStreamIndexForPeerId(sendercid);
        if (index)
            updateStatusIconState(msgData.micro === "true", false, index, "Mic");
    }*/

    if (status.speaker !== undefined) {
        updateStatusIconState(status.speaker, false, index + 1, "Speaker");
    }

    if (status.video !== undefined) {
        updateStatusIconState(status.video, false, index + 1, "Video");
    }
}