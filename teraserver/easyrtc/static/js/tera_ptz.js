let debounceWheel = 0;

function manageMouseWheel(event, index){
    // Ignore events for 750 ms
    let currentTime = Date.now();

    if (currentTime > debounceWheel){
        if (event.deltaY > 0){
            zoomOut(index);
        }else{
            zoomIn(index);
        }
        debounceWheel = currentTime + 500;
    }
}