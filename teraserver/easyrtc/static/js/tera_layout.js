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

    switch(remote_num){
        case 1:
            remoteView1.show();
            remoteView2.hide();
            remoteView3.hide();
            remoteView4.hide();
            if (!remoteView1[0].classList.contains('col') && currentLargeViewId !== 'remoteView1')
                setColWidth(remoteView1, 12);
            break;
        case 2:
            remoteView1.show();
            remoteView2.show();
            remoteView3.hide();
            remoteView4.hide();
            if (!remoteView1[0].classList.contains('col') && currentLargeViewId !== 'remoteView1')
                setColWidth(remoteView1, 6);
            break;
        case 3:
            remoteView1.show();
            remoteView2.show();
            remoteView3.show();
            remoteView4.hide();
            if (!remoteView1[0].classList.contains('col') && currentLargeViewId !== 'remoteView1')
                setColWidth(remoteView1,6);
            if (!remoteView3[0].classList.contains('col') && currentLargeViewId !== 'remoteView3')
                setColWidth(remoteView3, 12);
            break;
        case 4:
            remoteView1.show();
            remoteView3.show();
            remoteView2.show();
            remoteView4.show();
            if (!remoteView1[0].classList.contains('col') && currentLargeViewId !== 'remoteView1')
                setColWidth(remoteView1,6);
            if (!remoteView3[0].classList.contains('col') && currentLargeViewId !== 'remoteView3')
                setColWidth(remoteView3,6);
            break;
        default:
            console.error('Too many views, don\'t know how to set the layout!');
            break;
    }
}

function updateUserLocalViewLayout(local_num, remote_num){
    let selfViewRow1 = $("#localView1Row");
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
    let remoteRows = $("#remoteRows1");
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
            setColWidth(remoteViews, 2);
            remoteRows.attr("style","flex-flow: column;");
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