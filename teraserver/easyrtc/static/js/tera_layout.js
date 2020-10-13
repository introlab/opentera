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
    let remoteRows1 = $("#remoteRows1");
    let remoteRows2 = $("#remoteRows2");
    let remoteViews = $("#remoteViews");
    let localViews = $("#localViews");


    if (remote_num === 0){
        remoteViews.hide();
        setRowWidth12(localViews);
        return;
    }else {
        remoteViews.show();
        setRowWidth4(localViews);
    }

    switch(remote_num){
        case 1:
            remoteView1.show();
            remoteView3.hide();
            setRowWidth12(remoteView1);

            setRowHeight100(remoteRows1);
            remoteRows1.show();
            remoteRows2.hide();
            break;
        case 2:
            remoteView1.show();
            remoteView3.hide();
            setRowWidth12(remoteView1);
            setRowHeight50(remoteRows1);

            remoteView2.show();
            setRowWidth12(remoteView2);
            setRowHeight50(remoteRows2);
            remoteView4.hide();
            remoteRows1.show();
            remoteRows2.show();
            break;
        case 3:
            remoteView1.show();
            remoteView3.show();
            setRowWidth6(remoteView1);
            setRowWidth6(remoteView3);
            setRowHeight50(remoteRows1);

            remoteView2.show();
            remoteView4.hide();
            setRowWidth12(remoteView2);
            setRowHeight50(remoteRows2);

            remoteRows1.show();
            remoteRows2.show();
            break;
        case 4:
            remoteView1.show();
            remoteView3.show();
            setRowWidth6(remoteView1);
            setRowWidth6(remoteView3);
            setRowHeight50(remoteRows1);

            remoteView2.show();
            remoteView4.show();
            setRowWidth6(remoteView2);
            setRowWidth6(remoteView4);
            setRowHeight50(remoteRows2);

            remoteRows1.show();
            remoteRows2.show();
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
                setRowHeight80(selfViewRow1);
                setRowHeight20(toolsView);
                toolsView.show();
            }else{
                setRowHeight100(selfViewRow1);
                toolsView.hide();
            }
            selfViewRow2.hide();
            break;
        case 2:
            if (remote_num>0){
                setRowHeight40(selfViewRow1);
                setRowHeight40(selfViewRow2);
                setRowHeight20(toolsView);
                toolsView.show();
            }else{
                setRowHeight50(selfViewRow1);
                setRowHeight50(selfViewRow2);
                toolsView.hide();
            }

            selfViewRow2.show();
            break;
        default:
            console.error('Unknown local view number, don\'t know how to set the layout!');
    }
}

function setRowWidth12(row){
    row.removeClass('col-4 col-6').addClass('col-12');
}

function setRowWidth6(row){
    row.removeClass('col-4 col-12').addClass('col-6');
}

function setRowWidth4(row){
    row.removeClass('col-6 col-12').addClass('col-4');
}

function setRowHeight20(row){
    row.removeClass('h-33 h-40 h-50 h-67 h-80 h-100').addClass('h-20');
}

function setRowHeight33(row){
    row.removeClass('h-20 h-40 h-50 h-67 h-80 h-100').addClass('h-33');
}

function setRowHeight40(row){
    row.removeClass('h-20 h-33 h-50 h-67 h-80 h-100').addClass('h-40');
}

function setRowHeight50(row){
    row.removeClass('h-20 h-33 h-40 h-67 h-80 h-100').addClass('h-50');
}

function setRowHeight67(row){
    row.removeClass('h-20 h-33 h-40 h-50 h-80 h-100').addClass('h-67');
}

function setRowHeight80(row){
    row.removeClass('h-20 h-33 h-40 h-50 h-67 h-100').addClass('h-80');
}

function setRowHeight100(row){
    row.removeClass('h-20 h-33 h-40 h-67 h-50 h-80').addClass('h-100');
}

function showLayout(show){
    (show === true) ? $('#mainContainer').show() : $('#mainContainer').hide();
}