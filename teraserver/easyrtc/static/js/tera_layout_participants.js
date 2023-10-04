let currentLargeViewId = "";
let isParticipant = true;

function initVideoAreas(){
    $.get(
        'includes/video_participant_remote_view.html',
        {},
        function (data) {
            for (let i=1; i<=maxRemoteSourceNum; i++){
                let divdata = data.replace(/{##view_id##}/g, i.toString());
                $('#remoteRows').append(divdata);
            }
            initialUserLayout();
        }
    );
}

function initialUserLayout(){
    updateUserRemoteViewsLayout();
    updateUserLocalViewLayout();
    setLargeView('remoteView1');
}

function updateUserRemoteViewsLayout(){
    let remoteViews = $("#remoteViews");
    let largeView = $("#largeView");
    let localViews = $("#localViews");

    let usedRemoteVideosIndexes = getVideoStreamsIndexes(remoteStreams);
    let remote_num = usedRemoteVideosIndexes.length;

    if (remote_num === 0){
        remoteViews.hide();
        largeView.hide();
        setLargeView('remoteView1', false);
        setColWidth(localViews, 12);
        return;
    }else {
        setColWidth(localViews, 2);
        largeView.show();
        if (remote_num > 1 || (currentLargeViewId.startsWith('local') && remote_num >0)){
            setColWidth(largeView, 8);
            remoteViews.show();
        }else {
            remoteViews.hide();
            setColWidth(largeView, 10);
        }

        // Check if large view is still valid
        let currentLargeViewIndex = parseInt(currentLargeViewId.charAt(currentLargeViewId.length-1));
        if (currentLargeViewIndex > remote_num){
            let new_large_view = getFirstRemoteUserVideoViewId();
            if (new_large_view === undefined)
                new_large_view = "remoteView1";
            setLargeView(new_large_view, false);
        }

    }

    let col_count = 1;
    if (remote_num > 5){
        col_count = 2;
    }
    let base_width = 12 / col_count;

    // Hide unused views
    for (let i=1; i<=maxRemoteSourceNum; i++){
        if (!usedRemoteVideosIndexes.includes(i))
            $("#remoteView" + i).hide();
    }

    // Show used views
    for (let i=1; i<=maxRemoteSourceNum; i++){
        if (usedRemoteVideosIndexes.includes(i)){
            let current_view = $("#remoteView" + i);
            current_view.show();
            if (currentLargeViewId !== 'remoteView' + i) {
                //setColWidth(current_view, base_width);
                removeClassByPrefix(current_view[0], 'col');
                current_view.addClass('col-xl-' + base_width + ' col-sm-12')
            }
        }
    }
}

function updateUserLocalViewLayout(){
    let selfViewRow1 = $("#localView1Row");
    let selfViewRow2 = $("#localView2Row");
    let largeView = $("#largeView");
    let localViews = $("#localViews");

    let usedRemoteVideosIndexes = getVideoStreamsIndexes(remoteStreams);
    let remote_num = usedRemoteVideosIndexes.length;
    let usedLocalVideosIndexes = getVideoStreamsIndexes(localStreams);
    let local_num = usedLocalVideosIndexes.length;
    console.log(usedLocalVideosIndexes);

    if (currentLargeViewId.startsWith('local') && local_num === 1){
        setColWidth(largeView, 10);
        localViews.hide();
    }else{
        if (remote_num > 1)
            setColWidth(largeView, 8);
        else
            setColWidth(largeView, 10);
        localViews.show();
    }

    switch(local_num){
        case 1:
            selfViewRow2.hide();
            break;
        case 2:
            selfViewRow2.show();
            break;
        default:
            if (local_num > 0)
                console.error('Unknown local view number, don\'t know how to set the layout!');
    }
}

function setLargeView(view_id, updateui=true){
    // Remove current view
    let largeView = $("#largeView");

    if (currentLargeViewId !== "" && currentLargeViewId !== undefined){
        let view_index = Number(currentLargeViewId.substr(-1));
        let currentLargeView = $('#' + currentLargeViewId);
        if (currentLargeViewId.startsWith("local")){
            setColWidth(largeView.children('div'),12);
            // Insert at the right place
            let prev_el = $('#localView' + view_index + 'Row');
            prev_el.append(currentLargeView);
        }else{
            removeClassByPrefix(currentLargeView[0], 'col');
            setColWidth(largeView.children('div'),0);
            currentLargeView.addClass('col-sm-12 col');

            if (view_index === 1){
                currentLargeView.insertBefore($('#remoteView2'));
            }else {
                let prev_el = $('#remoteView' + (view_index-1));
                currentLargeView.insertAfter(prev_el);
            }
        }
    }

    // Swap view
    currentLargeViewId = view_id;
    if (view_id !== ""){
        let view = $("#" + view_id);
        removeClassByPrefix(view[0], 'col');
        largeView.prepend(view);
    }

    if (updateui){
        updateUserRemoteViewsLayout();
        updateUserLocalViewLayout();
    }
}

function setColWidth(col, width){
    removeClassByPrefix(col[0], 'col');
    if (width>0) {
        col.addClass('col-' + width);
    }else{
        col.addClass('col');
    }
}

function setRowHeight(row, height){
    removeClassByPrefix(row[0], 'h-');
    row.addClass('h-' + height);

}

function showLayout(show){
    let mainContainer = $('#mainContainer');
    (show === true) ? mainContainer.show() : mainContainer.hide();
}

function removeClassByPrefix(el, prefix) {
    for(let i = el.classList.length - 1; i >= 0; i--) {
        if(el.classList[i].startsWith(prefix)) {
            el.classList.remove(el.classList[i]);
        }
    }
}

function testLayout(local_num, remote_num){
    remoteStreams=[]
    for (let i=1; i<=remote_num; i++) {
        let remoteVideo = $('#remoteVideo' + i)[0];
        remoteVideo.srcObject = $('#localVideo1')[0].srcObject;
        remoteVideo.muted = true;
        remoteVideo.play();
        remoteStreams.push(remoteVideo.srcObject)
    }
    if (localStreams.length < local_num){
        let localVideo2 = $('#localVideo2')[0];
        localVideo2.srcObject = $('#localVideo1')[0].srcObject;
        localVideo2.muted = true;
        localVideo2.play();
        localStreams.push(localVideo2.srcObject)
    }else{
        localStreams.pop();
    }

    updateUserRemoteViewsLayout();
    updateUserLocalViewLayout();
}
