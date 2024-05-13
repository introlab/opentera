///////////////////////////////////////////
// CHRONOS TOOLS
///////////////////////////////////////////
let localChronoTimerHandle = 0;
let chronoInfos = {}; // List of dict by key (peer id) - increment, duration, message

function startChronosFromDialog(){
    // Build list of participants to send
    let partSelect = Number($('#chronosPartSelect').children("option:selected").val());
    /*let message = $('#chronosTitleSelect').children("option:selected")[0].text;
    if ($('#chronosTitleSelect').children("option:selected").val() === "")
        message = "";*/
    //let durationSelect = Number($('#chronosDurationSelect').children("option:selected").val());
    let duration = Number($('#chronosDurationMinutes')[0].value) * 60 + Number($('#chronosDurationSeconds')[0].value);
    let chronoType = Number($('input[name="optChronoType"]:checked').val());
    let increment = -1;
    let message = "";

    // Reset values
    chronoInfos = {};
    showChrono(true, 1, false);
    for (let i=0; i<remoteStreams.length; i++){
        showChrono(false, i+1, false);
    }

    if (chronoType === 2){
        // Chronometer
        increment = 1;
        duration = 0; // Always start chronometer at 0
    }

    if (partSelect === -1) {
        // Self only
        setupChrono(true, 1, increment, duration, message);
        return;
    }

    if (partSelect === 0){
        // All participants
        for (let i=0; i<remoteStreams.length; i++){
            if (remoteStreams[i].streamname === 'default')
                setupChrono(false, i, increment, duration, message);
        }
    }else{
        // One participant... for now!
        setupChrono(false, partSelect-1, increment, duration, message);
    }
}

function startChrono(){
    let target_peers = Object.keys(chronoInfos);
    if (target_peers.includes(local_peerid)){
        showChronoButtons(true, 1, true, false);
    }else{
        target_peers.forEach( function(target){
                if (!isParticipant){
                    sendChronoMessage([target], 1, chronoInfos[target].message, chronoInfos[target].duration,
                        chronoInfos[target].increment, chronoInfos[target].value);
                }
                showChronoButtons(false, getStreamIndexForPeerId(target)+1, true, false);
            }

        )
    }

    // Start timer
    if (localChronoTimerHandle === 0){
        localChronoTimerHandle = setInterval(chronoTimerTimeout, 1000);
    }
}

function setupChrono(local, index, increment=-1, duration = undefined, title=undefined, initial_value = -1){
    // Setup chrono
    let peer_id;
    if (local === false){
        // Get peer id for index
        peer_id = remoteStreams[index].peerid;
    }else{
        peer_id = local_peerid;
        index = 0;
    }

    let value = 0;
    if (initial_value >= 0){
        value = initial_value;
    }else{
        if (increment < 0){
            value = duration;
        }
    }

    chronoInfos[peer_id] = {"increment": increment, "duration": duration, "value": value, "message": title};

    // Stop current local Chrono if needed
    if (localChronoTimerHandle > 0){
        // Stop current timer if needed
        clearTimeout(localChronoTimerHandle);
        localChronoTimerHandle = 0;
    }

    updateChronoDisplay(local, index+1, value, increment, title);
    showChrono(local, index+1, true);
}

function updateChronoDisplay(local, index, duration, increment, title=undefined){

    let count_str = chronoSecondsToText(duration);

    if (title !== undefined){
        // Refresh label in full
        let full_title = title;
        if (title !== "")
            full_title += ": ";
        full_title += count_str;
        setChronoText(local, index, full_title)
    }else{
        // Only update time
        let displayed = getChronoTextDisplay(local, index);
        let prev_count_str = chronoSecondsToText(duration-increment);
        displayed = displayed.substring(0, displayed.length-prev_count_str.length) + count_str;
        setChronoText(local, index, displayed);
    }
}

function chronoSecondsToText(duration){
    if (duration < 3600) // No hours
        return new Date(duration * 1000).toISOString().substring(14, 19);
    else
        return new Date(duration * 1000).toISOString().substring(11, 19);
}

function chronoShowCompleted(local, index, duration){
    let display_text = "<font color='yellow'>" + translator.translateForKey("chronosDialog.completed", currentLang) +
            "</font>";
    if (duration > 0) // Display chrono value if > 0
        display_text += " - " + chronoSecondsToText(duration);
    setChronoText(local, index, display_text);

    // Start hide chrono timer in 5 seconds
    setTimeout(showChrono, 5000, local, index, false);
}

function chronoTimerTimeout(){
    // Update all active chronos
    let active = true;
    Object.keys(chronoInfos).forEach(function(peer_id) {
        chronoInfos[peer_id].value += chronoInfos[peer_id].increment;
        let index = 0;
        if (peer_id !== local_peerid){
            index = getStreamIndexForPeerId(peer_id);
        }
        if (chronoInfos[peer_id].value <= 0 && chronoInfos[peer_id].increment < 0){
            // Countdown completed!
            chronoShowCompleted(peer_id === local_peerid, index+1, chronoInfos[peer_id].value);
            active = false;
        }else{
            updateChronoDisplay(peer_id === local_peerid, index+1,chronoInfos[peer_id].value,
                chronoInfos[peer_id].increment);
        }
    });

    if (active === false){
        clearTimeout(localChronoTimerHandle);
        localChronoTimerHandle = 0;
    }
}

function stopChrono(local, index, no_msg=false){
    let final_value = 0;
    if (local === false){
        let peer_id = remoteStreams[index-1].peerid;
        if (!Object.keys(chronoInfos).includes(peer_id))
            return; // Nothing to stop!
        final_value = chronoInfos[peer_id].value;
        if (!no_msg)
            sendChronoMessage([peer_id], 0);
        delete chronoInfos[peer_id];
    }else{
        if (!Object.keys(chronoInfos).includes(local_peerid))
            return; // Nothing to stop!
        final_value = chronoInfos[local_peerid].value;
        delete chronoInfos[local_peerid];
    }
    chronoShowCompleted(local, index, final_value);

    showChronoButtons(local, index, false, true);

    //showTextDisplay(local,index,false);
}

function pauseChrono(local, index){
    if (local === false){
        let peer_id = remoteStreams[index-1].peerid;
        if (!Object.keys(chronoInfos).includes(peer_id))
            return; // Nothing to pause!
        sendChronoMessage([peer_id], 2);
    }else{
        if (!Object.keys(chronoInfos).includes(local_peerid))
            return; // Nothing to pause!
    }
    clearTimeout(localChronoTimerHandle);
    showChronoButtons(local, index, false, false);
    localChronoTimerHandle = 0;
}

///////////////////////////////////////////
// MEASUREMENTS TOOLS
///////////////////////////////////////////
let measuring = false;
let measurePoints = [];

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
    //showElement("measureAnglesTools");
    $('#measureAnglesTools').css('display', 'inline');
    showElement("measureVideoCanvas");
    let angle_btn = $('#btnMeasureAngles');
    angle_btn.html(translator.translateForKey("measureDialog.measure-angle-stop"));
    angle_btn.addClass('btn-danger');
    angle_btn.removeClass('btn-success');
}

function stopAngleMeasurement(){
    $('#measureVideo')[0].play();
    measuring = false;
    $("#measurePartSelect").attr('disabled',false);
    hideElement("measureAnglesTools");
    clearAngleMeasurement();
    hideElement("measureVideoCanvas");

    // Change button label
    let angle_btn = $('#btnMeasureAngles');
    angle_btn.html(translator.translateForKey("measureDialog.measure-angle"));
    angle_btn.removeClass('btn-danger');
    angle_btn.addClass('btn-success');
}

function clearAngleMeasurement(){
    let canvas = $('#measureVideoCanvas')[0];
    const context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height);

    measurePoints = [];

    setAngleValue(null);
}

function measureAddAndDrawPoint(pos_x, pos_y){
    measurePoints.push({'x': pos_x, 'y': pos_y});
    let canvas = $('#measureVideoCanvas')[0];
    const ctx = canvas.getContext('2d');
    ctx.beginPath();
    ctx.strokeStyle = "black";
    ctx.fillStyle = "white";
    ctx.lineWidth = 2;
    ctx.arc(pos_x, pos_y, 5, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();
}

function measureDrawLine(x1, y1, x2, y2){
    let canvas = $('#measureVideoCanvas')[0];
    const ctx = canvas.getContext('2d');
    ctx.beginPath();
    ctx.strokeStyle = "white";
    ctx.lineWidth = 3;
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
}

function setAngleValue(value){
    if (value === null) {
        $('#lblMeasureAnglesValue')[0].innerHTML = translator.translateForKey("measureDialog.n-a", currentLang)
        $('#lblMeasureAnglesCompValue')[0].innerHTML = translator.translateForKey("measureDialog.n-a", currentLang)
    }else{
        $('#lblMeasureAnglesValue')[0].innerHTML = value + "°"
        $('#lblMeasureAnglesCompValue')[0].innerHTML = (value - 180) + "°"
    }
}

function measureCurrentAngle(last_x = null, last_y=null){
    if (measurePoints.length >=3 || (last_x == null && last_y == null && measurePoints.length < 2))
        return;

    let A = measurePoints[0];
    let B = measurePoints[1];
    let C;
    if (measurePoints.length >= 3)
        C = measurePoints[2];
    else
        C = {x: last_x, y: last_y}

    let AB = Math.sqrt(Math.pow(B.x-A.x,2)+ Math.pow(B.y-A.y,2));
    let BC = Math.sqrt(Math.pow(B.x-C.x,2)+ Math.pow(B.y-C.y,2));
    let AC = Math.sqrt(Math.pow(C.x-A.x,2)+ Math.pow(C.y-A.y,2));

    let angle = Math.round(Math.acos((BC*BC+AB*AB-AC*AC) / (2*BC*AB)) * (180 / Math.PI));

    setAngleValue(angle);

}


// On close event
$(document).on('hide.bs.modal', '#measureDialog',function (e) {
    easyrtc.setVideoObjectSrc($('#measureVideo')[0], null);
    measuring = false;
    stopAngleMeasurement();

})

// On canvas click event
$(document).on('click', '#measureVideoCanvas', function(evt) {
    if (!measuring)
        return;
    let canvas = $('#measureVideoCanvas');
    let x = evt.pageX - canvas.offset().left;
    let y = evt.pageY - canvas.offset().top;

    // If we already had 3 points, clear and start again
    if (measurePoints.length>=3)
        clearAngleMeasurement();

    // Draw dot
    measureAddAndDrawPoint(x,y);

    if (measurePoints.length > 1){
        // Also draw line between points
        let point1 = measurePoints.length-2;
        let point2 = point1 + 1;
        measureDrawLine(measurePoints[point1].x, measurePoints[point1].y,
            measurePoints[point2].x,measurePoints[point2].y);
    }

    // Final point - measure angle
    if (measurePoints.length >= 3){
        measureCurrentAngle();
    }
});

// On canvas mouve move event
$(document).on('mousemove', '#measureVideoCanvas', function(evt) {
    if (measurePoints.length<2 || measurePoints.length >=3 )
        return;
    let canvas = $('#measureVideoCanvas');
    let x = evt.pageX - canvas.offset().left;
    let y = evt.pageY - canvas.offset().top;

    measureCurrentAngle(x,y);

});

///////////////////////////////////////////
// COUNTER TOOLS
///////////////////////////////////////////
let counterInfos = {};
function startCountersFromDialog(){
    // Build list of participants to send
    let partSelect = Number($('#counterPartSelect').children("option:selected").val());

    // Reset values
    counterInfos = {};
    showCounter(true, 1, false);
    for (let i=0; i<remoteStreams.length; i++){
        showCounter(false, i+1, false);
    }

    if (partSelect === -1) {
        // Self only
        setupCounter(true, 1);
        return;
    }

    if (partSelect === 0){
        // All participants
        for (let i=0; i<remoteStreams.length; i++){
            if (remoteStreams[i].streamname === 'default'){
                setupCounter(false, i);
                sendCounterMessage([remoteStreams[i].peerid], true, counterInfos[remoteStreams[i].peerid].value);
            }
        }

    }else{
        // One participant... for now!
        setupCounter(false, partSelect-1);
        sendCounterMessage([remoteStreams[partSelect-1].peerid], true, counterInfos[remoteStreams[partSelect-1].peerid].value);
    }
}

function setupCounter(local, index, initial_value=0){
    let peer_id;
    if (local === false){
        // Get peer id for index
        peer_id = remoteStreams[index].peerid;
    }else{
        peer_id = local_peerid;
        index = 0;
    }

    counterInfos[peer_id] = {"value": initial_value};

    setCounterText(local, index+1, initial_value);
    showCounter(local, index+1, true);
}

function counterPlus(local, index){
    let peer_id;
    if (local === false){
        // Get peer id for index
        peer_id = remoteStreams[index-1].peerid;
    }else{
        peer_id = local_peerid;
    }

    counterInfos[peer_id].value = counterInfos[peer_id].value + 1;
    setCounterText(local, index, counterInfos[peer_id].value);
    if (local === false){
        sendCounterMessage([peer_id], true, counterInfos[peer_id].value);
    }

}

function counterMinus(local, index){
    let peer_id;
    if (local === false){
        // Get peer id for index
        peer_id = remoteStreams[index-1].peerid;
    }else{
        peer_id = local_peerid;
    }

    counterInfos[peer_id].value = counterInfos[peer_id].value - 1;
    if (counterInfos[peer_id].value < 0)
        counterInfos[peer_id].value = 0;
    setCounterText(local, index, counterInfos[peer_id].value);
    if (local === false){
        sendCounterMessage([peer_id], true, counterInfos[peer_id].value);
    }
}

function stopCounter(local, index){
    let peer_id;
    if (local === false){
        // Get peer id for index
        peer_id = remoteStreams[index-1].peerid;
    }else{
        peer_id = local_peerid;
    }
    delete counterInfos[peer_id];
    showCounter(local, index, false);
    if (!local){
        sendCounterMessage([peer_id], false, 0);
    }
}
