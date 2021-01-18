let currentLargeViewId = "";
let isParticipant = true;

function initialUserLayout(){
    updateUserRemoteViewsLayout(0);
    updateUserLocalViewLayout(1, 0);
    setLargeView('remoteView1');
}

function updateUserRemoteViewsLayout(remote_num){
    // TODO: Improve.

    let remoteView1 = $("#remoteView1");
    let remoteView2 = $("#remoteView2");
    let remoteView3 = $("#remoteView3");
    let remoteView4 = $("#remoteView4");
    let remoteViews = $("#remoteViews");
    let largeView = $("#largeView");
    let localViews = $("#localViews");


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

    switch(remote_num){
        case 1:
            remoteView1.show();
            remoteView2.hide();
            remoteView3.hide();
            remoteView4.hide();
            //setLargeView('remoteView1');
            break;
        case 2:
            remoteView1.show();
            remoteView2.show();
            remoteView3.hide();
            remoteView4.hide();
            break;
        case 3:
            remoteView1.show();
            remoteView2.show();
            remoteView3.show();
            remoteView4.hide();
            break;
        case 4:
            remoteView1.show();
            remoteView3.show();
            remoteView2.show();
            remoteView4.show();
            break;
        default:
            console.error('Too many views, don\'t know how to set the layout!');
            break;
    }
}

function updateUserLocalViewLayout(local_num, remote_num){
    let selfViewRow1 = $("#localView1Row");
    let selfViewRow2 = $("#localView2Row");
    let largeView = $("#largeView");
    let localViews = $("#localViews");

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

    if (currentLargeViewId !== ""){
        let view_index = Number(currentLargeViewId.substr(-1));
        if (currentLargeViewId.startsWith("local")){
            setColWidth(largeView.children('div'),12);
            // Insert at the right place
            let prev_el = $('#localView' + view_index + 'Row');
            prev_el.append($('#' + currentLargeViewId));
        }else{
            setColWidth(largeView.children('div'),0);
            if (view_index === 1){
                $('#' + currentLargeViewId).insertBefore($('#remoteView2'));
            }else {
                let prev_el = $('#remoteView' + (view_index-1));
                $('#' + currentLargeViewId).insertAfter(prev_el);
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
        updateUserRemoteViewsLayout(remoteStreams.length);
        updateUserLocalViewLayout(localStreams.length, remoteStreams.length);
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