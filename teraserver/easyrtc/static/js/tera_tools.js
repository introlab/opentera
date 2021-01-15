///////////////////////////////////////////
// CHRONOS TOOLS
///////////////////////////////////////////
let localChronoTimerHandle = 0;
let chronoValues = [0, 0, 0, 0];
let localChronoValue = 0;

function startChronosFromDialog(){
    // Build list of participants to send
    let target_ids = [];
    let partSelect = Number($('#chronosPartSelect').children("option:selected").val());
    let msgSelect = $('#chronosTitleSelect').children("option:selected")[0].text;
    let durationSelect = Number($('#chronosDurationSelect').children("option:selected").val());

    if (partSelect === 0){
        // All participants
        for (let i=0; i<remoteStreams.length; i++){
            target_ids.push(remoteStreams[i].peerid);
        }
    }else{
        // Only one... for now!
        target_ids = [remoteStreams[partSelect-1].peerid];
    }

    // Send message
    sendChronoMessage(target_ids, true, msgSelect, durationSelect);

    // Start chronos
    for (let i=0; i<target_ids.length; i++){
        let stream_index = getStreamIndexForPeerId(target_ids[i]);
        if (stream_index !== undefined){
            startChrono(false, stream_index+1, durationSelect, msgSelect);
        }
    }
}

function startChrono(local, index, duration = undefined, title=undefined){

    // Start chrono
    if (local === false){
        chronoValues[index-1] = duration;
    }else{
        localChronoValue = duration;
    }
    updateChronoDisplay(local, index, duration, title);
    showTextDisplay(local, index, true);

    // Start timer
    if (localChronoTimerHandle === 0){
        localChronoTimerHandle = setInterval(chronoTimerTimeout, 1000);
    }

}

function updateChronoDisplay(local, index, duration, title=undefined){

    let count_str = new Date(duration * 1000).toISOString().substr(14, 5)

    if (duration === 0){
        count_str = "<font color='yellow'>" + translator.translateForKey("chronosDialog.completed", currentLang) +
            "</font>";
    }

    if (title !== undefined){
        // Refresh label in full
        setTextDisplay(local, index, title + ": " + count_str)
    }else{
        // Only update time
        let displayed = getTextDisplay(local, index);
        displayed = displayed.substr(0, displayed.length-5) + count_str;
        setTextDisplay(local, index, displayed);
    }
}

function chronoTimerTimeout(){
    // Update all active chronos
    let active = false;
    for (let i=0; i<chronoValues.length; i++){
        if (chronoValues[i] > 0){
            active = true;
            chronoValues[i] -= 1;
            updateChronoDisplay(false, i+1, chronoValues[i]);
            if (chronoValues[i] === 0){
                // Start hide chrono timer in 5 seconds
                setTimeout(showTextDisplay, 5000, false, i+1, false);
            }
        }
    }

    if (localChronoValue > 0){
        active = true;
        localChronoValue -= 1;
        updateChronoDisplay(true, 1, localChronoValue);
        if (localChronoValue === 0){
            // Start hide chrono timer in 5 seconds
            setTimeout(showTextDisplay, 5000, true, 1, false);
        }
    }

    if (active === false){
        clearTimeout(localChronoTimerHandle);
        localChronoTimerHandle = 0;
    }
}

function stopChrono(local, index, no_msg=false){
    if (local === false){
        chronoValues[index-1] = 0;
        let target_peer = remoteStreams[index-1].peerid;
        if (!no_msg)
            sendChronoMessage([target_peer], false);
    }else{
        localChronoValue = 0;
    }

    showTextDisplay(local,index,false);
}

///////////////////////////////////////////
// MEASUREMENTS TOOLS
///////////////////////////////////////////
let measuring = false;
function onMeasureParticipantChanged(){
    let partSelect = Number($('#measurePartSelect').children("option:selected").val());

    // Show selected video
    easyrtc.setVideoObjectSrc($('#measureVideo')[0], remoteStreams[partSelect-1].stream);
}

function onAngleMeasurementToggle(){
    if (measuring)
        stopAngleMeasurement();
    else
        startAngleMeasurement();
}

function startAngleMeasurement(){
    $('#measureVideo')[0].pause();
    measuring = true;
    $("#measurePartSelect").attr('disabled',true);

}

function stopAngleMeasurement(){
    $('#measureVideo')[0].play();
    measuring = false;
    $("#measurePartSelect").attr('disabled',false);
}

// On close event
$(document).on('hide.bs.modal', '#measureDialog',function (e) {
    easyrtc.setVideoObjectSrc($('#measureVideo')[0], null);
    measuring = false;
})
