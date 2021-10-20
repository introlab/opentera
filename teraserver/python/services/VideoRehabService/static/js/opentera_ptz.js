let debounceWheel = 0;
let localPTZCapabilities = {'uuid':0, 'zoom':false,'presets':false,'settings':false};

function managePTZMouseWheel(event){
    // Ignore events for 500 ms
    let currentTime = Date.now();

    if (currentTime > debounceWheel){
        if (event.deltaY > 0){
            zoomOut();
        }else{
            zoomIn();
        }
        debounceWheel = currentTime + 500;
    }
}

function zoomIn(){
    if (teraConnected)
        if (isCurrentCameraPTZ())
            SharedObject.zoomInClicked(localContact.uuid);

    resetInactiveTimer();
}

function zoomOut(){
    if (teraConnected)
        if (isCurrentCameraPTZ())
            SharedObject.zoomOutClicked(localContact.uuid);

    resetInactiveTimer();
}

function zoomMin(){
    if (teraConnected)
        if (isCurrentCameraPTZ())
            SharedObject.zoomMinClicked(localContact.uuid);

}

function zoomMax(){
    if (teraConnected)
        if (isCurrentCameraPTZ())
            SharedObject.zoomMaxClicked(localContact.uuid);
}

function gotoPreset(event, preset){
    console.log("gotoPreset: preset: " + preset +
        ", shift: " + event.shiftKey + ", ctrl: " + event.ctrlKey);

    if (teraConnected){
        if (isCurrentCameraPTZ()) {
            if (event.shiftKey && event.ctrlKey)
                SharedObject.setPresetClicked(localContact.uuid, preset);
            else
                SharedObject.gotoPresetClicked(localContact.uuid, preset);
        }
    }
}

function camSettings(){
    if (teraConnected)
        if (isCurrentCameraPTZ())
            SharedObject.camSettingsClicked(localContact.uuid);
}

function managePTZClickEvent(event){
    let video = $('#selfVideo')[0];
    const offsets = video.getBoundingClientRect();

    const video_dims = calculateContainsWindow(video);
    const real_video_width = (video.clientWidth * video_dims.destinationWidthPercentage);
    const bar_width = (video.clientWidth - real_video_width) / 2;

    const real_video_height = (video.clientHeight * video_dims.destinationHeightPercentage);
    const bar_height = (video.clientHeight - real_video_height) / 2;

    //console.log("x=" + (event.clientX - offsets.left) + " y=" + (event.clientY - offsets.top) + " w=" + video.clientWidth + " h=" + video.clientHeight);
    if (teraConnected){
        if (isCurrentCameraPTZ()) {
            let x = (event.clientX - bar_width);
            let y = (event.clientY - bar_height);
            if (x < 0 || x > real_video_width || y < 0 || y > real_video_height)
                return; // Click outside the displayed video
            //console.log("Local PTZ request - x=" + x + ", y=" + y + ", w=" + real_video_width + ", h=" + real_video_height);
            SharedObject.imageClicked(localContact.uuid, x, y, real_video_width, real_video_height);
        }
    }

}

function setPTZCapabilities(zoom, presets, settings, camera = undefined){
    let ptz = {'zoom':zoom,'presets':presets,'settings':settings, 'camera':camera};
    console.log(" -- Local UUID - settings values.");
    // Setting local capabilities
    localPTZCapabilities = ptz;

    // Show buttons
    showPTZControls(true, 1, zoom, presets, settings, camera);
}

function isCurrentCameraPTZ() {
    if (localPTZCapabilities.camera === undefined ||
        currentConfig['currentVideoName'] === localPTZCapabilities.camera){
        return true;
    }
    return false;
}