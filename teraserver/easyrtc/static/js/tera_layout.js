const layouts = {
    GRID: 0,
    LARGEVIEW: 1
}

let currentLayoutId = layouts.GRID;
let currentLargeViewId = "";
let isParticipant = false;

function initialUserLayout(){
    updateUserRemoteViewsLayout(0);
    updateUserLocalViewLayout(1, 0);
}

function updateUserRemoteViewsLayout(remote_num){
    let remoteViews = $("#remoteViews");
    let largeView = $("#largeView");
    let localViews = $("#localViews");

    if (remote_num === 0){
        remoteViews.hide();
        setCurrentUserLayout(layouts.GRID, false);
        setColWidth(localViews, 12);
        return;
    }else {
        if (currentLayoutId === layouts.GRID){
            setColWidth(localViews, 3);
            remoteViews.show();
            largeView.hide();
        }
        if (currentLayoutId === layouts.LARGEVIEW){
            setColWidth(localViews, 2);
            largeView.show();
            (remote_num > 1 || (currentLargeViewId.startsWith('local') && remote_num >0)) ? remoteViews.show() : remoteViews.hide();
        }
    }

    // Hide unused views
    for (let i=remote_num+1; i<=maxRemoteSourceNum; i++){
        $("#remoteView" + i).hide();
    }

    // Set base col-width depending on number of remote views (2x2 grid if less than 4, 2x3 and then 2x4)
    let col_count = Math.ceil(remote_num / 2);
    if (currentLayoutId === layouts.GRID) {
        if (remote_num === 1) {
            col_count = 1;
        }
        if (remote_num === 2) {
            col_count = 2;
        }
    }
    if (currentLayoutId === layouts.LARGEVIEW){
        if (remote_num > 4){
            col_count = 2;
        }else{
            col_count = 1;
        }
    }

    let base_width = 12 / col_count;

    // Show used views
    for (let i=1; i<=remote_num; i++){
        let current_view = $("#remoteView" + i);
        current_view.show();
        if (currentLayoutId === layouts.GRID) {
            if (!current_view[0].classList.contains('col')) {
                setColWidth(current_view, base_width);
            }
        }
        if (currentLayoutId === layouts.LARGEVIEW){
            if (currentLargeViewId !== 'remoteView' + i){
                // Other views
                setColWidth(current_view, base_width);
            }
        }
    }

    // If odd number of streams, stretch the row with odd number of columns
    if (currentLayoutId === layouts.GRID && remote_num % 2 > 0){
        for (let i=remote_num-col_count+2; i<=remote_num; i++){
            let last_view = $("#remoteView" + i);
            if (!last_view[0].classList.contains('col')){
                setColWidth(last_view, Math.ceil(12 / (col_count - 1)));
            }
        }
    }

    if (currentLayoutId === layouts.LARGEVIEW && remote_num % 2 === 0){
        let last_view = $("#remoteView" + remote_num);
        if (currentLargeViewId === 'remoteView' + remote_num){
            if (remote_num-1 > 0) {
                last_view = $("#remoteView" + remote_num - 1);
            }else{
                last_view = $("#remoteView" + remote_num + 1);
            }
        }
        if (!last_view[0].classList.contains('col')){
            setColWidth(last_view, Math.ceil(12 / (col_count - 1)));
        }
    }
}

function updateUserLocalViewLayout(local_num, remote_num){
    // let selfViewRow1 = $("#localView1Row");
    let selfViewRow2 = $("#localView2Row");
    let toolsView = $("#toolsViewRow");

    // Tool bar display
    if (remote_num>0){
        toolsView.show();
    }else{
        toolsView.hide();
    }

    switch(local_num){
        case 1:
            selfViewRow2.hide();
            break;
        case 2:
            selfViewRow2.show();
            break;
        default:
            console.error('Unknown local view number, don\'t know how to set the layout!');
    }
}

function setCurrentUserLayout(layout_id, update_views= true, largeViewId = ""){
    currentLayoutId = layout_id;

    let largeView = $('#largeView');
    let remoteViews = $("#remoteViews");
    let remoteRows = $("#remoteRows");
    let localViews = $("#localViews");

    switch (currentLayoutId){
        case layouts.GRID:
            // Move current large view to its position
            setLargeView("");
            largeView.hide();
            setColWidth(localViews, 3);
            setColWidth(remoteViews, 9);
            remoteRows.attr("style","");
            for (let i=1; i<=4; i++){
                setColWidth($('#remoteView' + i), 6);
            }
            break;
        case layouts.LARGEVIEW:
            largeView.show();
            setColWidth(localViews, 2);
            setColWidth(remoteViews, 3);
            //remoteRows.attr("style","flex-flow: column;");
            for (let i=1; i<=4; i++){
                setColWidth($('#remoteView' + i), 0);
            }

            if (largeViewId === "")
                // Set remote 1 as default view
                setLargeView("remoteView1");
            else{
                setLargeView(largeViewId);
            }
            break;

        default:
            showError("setCurrentUserLayout", "Unknown user layout ID", false);
    }
    if (update_views === true)
        updateUserRemoteViewsLayout(remoteStreams.length);
}

function setLargeView(view_id){
    /*if (currentLayoutId !== 1 && view_id !== ""){
        console.warn("Trying to set large view, but wrong layout!");
        return;
    }*/

    // Remove current view
    let largeView = $("#largeView");
    if (currentLargeViewId !== ""){
        let view_index = Number(currentLargeViewId.substr(-1));
        if (currentLargeViewId.startsWith("local")){
            //let localViews = $('#localViews');
            setColWidth(largeView.children('div'),12);
            // Insert at the right place
            let prev_el = $('#localView' + view_index + 'Row');
            prev_el.append($('#' + currentLargeViewId));
            //localViews.append(largeView.children('div')[0]);

        }else{
            setColWidth(largeView.children('div'),0);
            if (view_index === 1){
                $('#' + currentLargeViewId).insertBefore($('#remoteView2'));
            }else {
                //remoteViews.append(largeView.children('div')[0]);
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
        largeView.append(view);
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
        $('#remoteVideo' + i)[0].srcObject = $('#localVideo1')[0].srcObject;
        $('#remoteVideo' + i)[0].muted = true;
        $('#remoteVideo' + i)[0].play();
        remoteStreams.push($('#remoteVideo' + i)[0].srcObject)
    }
    if (localStreams.length < local_num){
        $('#localVideo2')[0].srcObject = $('#localVideo1')[0].srcObject;
        $('#localVideo2')[0].muted = true;
        $('#localVideo2')[0].play();
        localStreams.push($('#localVideo2')[0].srcObject)
    }else{
        localStreams.pop();
    }

    updateUserRemoteViewsLayout(remote_num);
    updateUserLocalViewLayout(local_num, remote_num);
}
