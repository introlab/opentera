///////////////////////////////////////////
// CHRONOS TOOLS
///////////////////////////////////////////
let localChronoTimerHandle = 0;
let chronoValues = [0, 0, 0, 0];
let localChronoValue = 0;
let chronoValuesIncrement = [-1, -1, -1, -1];
let localChronoIncrement = -1;

function startChronosFromDialog(){
    // Build list of participants to send
    let target_ids = [];
    let partSelect = Number($('#chronosPartSelect').children("option:selected").val());
    let msgSelect = $('#chronosTitleSelect').children("option:selected")[0].text;
    if ($('#chronosTitleSelect').children("option:selected").val() === "")
        msgSelect = "";
    //let durationSelect = Number($('#chronosDurationSelect').children("option:selected").val());
    let durationSelect = Number($('#chronosDurationMinutes')[0].value) * 60
        + Number($('#chronosDurationSeconds')[0].value);
    let chronoType = Number($('input[name="optChronoType"]:checked').val());
    let increment = -1;

    if (chronoType === 2){
        // Chronometer
        increment = 1;
        durationSelect = 0; // Always start chronometer at 0
    }


    if (partSelect === -1) {
        // Self only
        startChrono(true, 1, increment, durationSelect, msgSelect);
        return;
    }

    if (partSelect === 0){
        // All participants
        for (let i=0; i<remoteStreams.length; i++){
            target_ids.push(remoteStreams[i].peerid);
        }
    }else{
        // One participant... for now!
        target_ids = [remoteStreams[partSelect-1].peerid];
    }

    // Send message
    sendChronoMessage(target_ids, true, msgSelect, durationSelect, increment);

    // Start chronos
    for (let i=0; i<target_ids.length; i++){
        let stream_index = getStreamIndexForPeerId(target_ids[i]);
        if (stream_index !== undefined){
            startChrono(false, stream_index+1, increment, durationSelect, msgSelect);
        }
    }
}

function startChrono(local, index, increment=-1, duration = undefined, title=undefined){

    // Start chrono
    if (local === false){
        chronoValues[index-1] = duration;
        chronoValuesIncrement[index-1] = increment;
    }else{
        localChronoValue = duration;
        localChronoIncrement = increment;
    }
    updateChronoDisplay(local, index, duration, increment, title);
    showTextDisplay(local, index, true);

    // Start timer
    if (localChronoTimerHandle === 0){
        localChronoTimerHandle = setInterval(chronoTimerTimeout, 1000);
    }

}

function updateChronoDisplay(local, index, duration, increment, title=undefined){

    let count_str = chronoSecondsToText(duration);

    if (title !== undefined){
        // Refresh label in full
        let full_title = title;
        if (title !== "")
            full_title += ": ";
        full_title += count_str;
        setTextDisplay(local, index, full_title)
    }else{
        // Only update time
        let displayed = getTextDisplay(local, index);
        let prev_count_str = chronoSecondsToText(duration-1);
        displayed = displayed.substr(0, displayed.length-prev_count_str.length) + count_str;
        setTextDisplay(local, index, displayed);
    }
}

function chronoSecondsToText(duration){
    if (duration < 3600) // No hours
        return new Date(duration * 1000).toISOString().substr(14, 5);
    else
        return new Date(duration * 1000).toISOString().substr(11, 8);
}

function chronoShowCompleted(local, index, duration){
    let display_text = "<font color='yellow'>" + translator.translateForKey("chronosDialog.completed", currentLang) +
            "</font>";
    if (duration > 0) // Display chrono value if > 0
        display_text += " - " + chronoSecondsToText(duration);
    setTextDisplay(local, index, display_text);

    // Start hide chrono timer in 5 seconds
    setTimeout(showTextDisplay, 5000, local, index, false);
}

function chronoTimerTimeout(){
    // Update all active chronos
    let active = false;
    for (let i=0; i<chronoValues.length; i++){
        if (chronoValues[i] > 0 || chronoValuesIncrement[i] > 0){
            active = true;
            chronoValues[i] += chronoValuesIncrement[i];
            if (chronoValues[i] <= 0 && chronoValuesIncrement[i] < 0){
                // Countdown completed!
                chronoShowCompleted(false, i+1, chronoValues[i]);
            }else{
                updateChronoDisplay(false, i+1, chronoValues[i], chronoValuesIncrement[i]);
            }
        }
    }

    if (localChronoValue > 0 || localChronoIncrement > 0){
        active = true;
        localChronoValue += localChronoIncrement;
        if (localChronoValue <= 0 && localChronoIncrement < 0){
            // Start hide chrono timer in 5 seconds
            chronoShowCompleted(true, 1, localChronoValue);
        }else{
            updateChronoDisplay(true, 1, localChronoValue, localChronoIncrement);
        }
    }

    if (active === false){
        clearTimeout(localChronoTimerHandle);
        localChronoTimerHandle = 0;
    }
}

function stopChrono(local, index, no_msg=false){
    if (local === false){
        chronoShowCompleted(local, index, chronoValues[index-1]);
        chronoValues[index-1] = 0;
        chronoValuesIncrement[index-1] = -1;
        let target_peer = remoteStreams[index-1].peerid;
        if (!no_msg)
            sendChronoMessage([target_peer], false);
    }else{
        chronoShowCompleted(local, index, localChronoValue);
        localChronoValue = 0;
        localChronoIncrement = -1;
    }

    //showTextDisplay(local,index,false);
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
    showElement("measureAnglesTools");
    showElement("measureVideoCanvas");
}

function stopAngleMeasurement(){
    $('#measureVideo')[0].play();
    measuring = false;
    $("#measurePartSelect").attr('disabled',false);
    hideElement("measureAnglesTools");
    clearAngleMeasurement();
    hideElement("measureVideoCanvas");
}

function clearAngleMeasurement(){
    let canvas = $('#measureVideoCanvas')[0];
    const context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height);

    measurePoints = [];

    setAngleValue(translator.translateForKey("measureDialog.n-a", currentLang));
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
    $('#lblMeasureAnglesValue')[0].innerHTML = value
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

    setAngleValue(angle + "°");

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