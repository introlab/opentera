let currentLayoutId = 0;
let currentLargeViewId = "";

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
    //let largeView = $("#largeView");
    let localViews = $("#localViews");


    if (remote_num === 0){
        remoteViews.hide();
        setCurrentUserLayout(0, false);
        setColWidth(localViews, 12);
        return;
    }else {
        remoteViews.show();
        if (currentLayoutId === 0) setColWidth(localViews, 3);
        if (currentLayoutId === 1) setColWidth(localViews, 2);
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

    switch(local_num){
        case 1:
            if (remote_num>0){
                setRowHeight(selfViewRow1, 80);
                setRowHeight(toolsView, 20);
                toolsView.show();
            }else{
                setRowHeight(selfViewRow1, 100);
                toolsView.hide();
            }
            selfViewRow2.hide();
            break;
        case 2:
            if (remote_num>0){
                setRowHeight(selfViewRow1, 40);
                setRowHeight(selfViewRow2, 40);
                setRowHeight(toolsView,20);
                toolsView.show();
            }else{
                setRowHeight(selfViewRow1,50);
                setRowHeight(selfViewRow2,50);
                toolsView.hide();
            }

            selfViewRow2.show();
            break;
        default:
            console.error('Unknown local view number, don\'t know how to set the layout!');
    }
}

function setCurrentUserLayout(layout_id, update_views= true){
    currentLayoutId = layout_id;

    let largeView = $('#largeView');
    let remoteViews = $("#remoteViews");
    let remoteRows = $("#remoteRows1");
    let localViews = $("#localViews");

    switch (currentLayoutId){
        case 0:
            largeView.hide();
            setColWidth(localViews, 3);
            setColWidth(remoteViews, 9);
            remoteRows.attr("style","");
            for (let i=1; i<=4; i++){
                setColWidth($('#remoteView' + i), 6);
            }
            if (update_views === true)
                updateUserRemoteViewsLayout(remoteStreams.length);

            // Move current large view to its position
            setLargeView("");
            break;
        case 1:
            largeView.show();
            setColWidth(localViews, 2);
            setColWidth(remoteViews, 2);
            remoteRows.attr("style","flex-flow: column;");
            for (let i=1; i<=4; i++){
                setColWidth($('#remoteView' + i), 0);
            }

            // Set remote 1 as default view
            setLargeView("remoteView1");
            break;

        default:
            showError("setCurrentUserLayout", "Unknown user layout ID", false);
    }
}

function setLargeView(view_id){
    /*if (currentLayoutId !== 1){
        console.warn("Trying to set large view, but wrong layout!");
        return;
    }*/

    // Remove current view
    let largeView = $("#largeView");
    if (largeView.children('div').length > 0){
        let view_id = largeView.children('div')[0].id;
        if (view_id.startsWith("local")){
            let localViews = $('#localViews');
            setColWidth(largeView.children('div'),12);
            localViews.append(largeView.children('div')[0]);
        }else{
            let remoteViews = $('#remoteRows1');
            setColWidth(largeView.children('div'),0);
            remoteViews.append(largeView.children('div')[0]);
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