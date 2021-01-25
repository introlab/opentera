let videoSources = [];
let currentVideoSourceIndex = 0;
let timerHandle = 0;

function initLocalVideo(){
	navigator.getUserMedia = navigator.mediaDevices.getUserMedia || navigator.getUserMedia ||
		navigator.webkitGetUserMedia || navigator.msGetUserMedia || navigator.oGetUserMedia;

	if (navigator.getUserMedia) {
		//navigator.getUserMedia({video: true, audio: false}, handleVideo, videoError);
		navigator.mediaDevices.getUserMedia({video: {facingMode: "user" },
			audio: false}).then(initialHandleVideo).catch(videoError);
	}
}

function initialHandleVideo(stream){
	handleVideo(stream);

	fillVideoSourceList(stream.getVideoTracks()[0].label);

}

function handleVideo(stream) {
	let video = document.getElementById("selfVideo");

	//console.log("Success! Device Name: " + stream.getVideoTracks()[0].label);
	video.srcObject = stream;

}

function videoError(err) {
	// do something
	showError("videoError()",
		"Impossible d'accéder à la caméra ou au micro.<br><br>Le message d'erreur est:<br>" + err.name + " - " + err.message, true);
}


function fillVideoSourceList(selected_source=undefined){
	videoSources.length=0;
	let select = document.getElementById('videoSelect');
	select.options.length = 0;
	let count = 0;

	navigator.mediaDevices.enumerateDevices()
	.then(function(devices) {
		devices.forEach(function(device) {
			if (device.kind === "videoinput"){
				videoSources[videoSources.length] = device;
				//select.options[select.options.length] = new Option(device.label.substring(0,device.label.length-12), device.id);
				select.options[select.options.length] = new Option(device.label, device.id);
				count++;
				if (count<2){
					hideElement("videoSelect"); // Hide if only one video source
				}else{
					showElement("videoSelect");
				}
			}
			//console.log(device.kind + ": " + device.label + " id = " + device.deviceId);
		});
		if (selected_source !== undefined){
			selectVideoSource(selected_source);
		}else{
			select.selectedIndex = currentVideoSourceIndex;
		}
	})
	.catch(function(err) {
		console.log(err.name + ": " + err.message);
	});
}

function updateVideoSource(){
	let select = document.getElementById('videoSelect');
	if (select.selectedIndex>=0){
		currentVideoSourceIndex = select.selectedIndex;
		let constraints = { deviceId: { exact: videoSources[currentVideoSourceIndex].deviceId } };
		//console.log(constraints);
		navigator.mediaDevices.getUserMedia({video: constraints}).then(handleVideo).catch(videoError);
	}
}

function selectVideoSource(source){
	console.log("Selecting " + source);
	for (let i=0; i<videoSources.length; i++){
		console.log(source + " = " + videoSources[i].label + " ?");
		if (videoSources[i].label.includes(source)){
			let select = document.getElementById('videoSelect');
			select.selectedIndex = i;
			currentVideoSourceIndex = i;
			//updateVideoSource();
			break;
		}
	}
}


function resetInactiveTimer(){

	stopInactiveTimer();

	timerHandle = setTimeout(inactiveTimeout, 3000);
}

function stopInactiveTimer(){
	if (timerHandle != 0){
		clearTimeout(timerHandle);
		timerHandle = 0;
	}
}

function inactiveTimeout(){
	closeButtons('navButtons');
}


function openButtons(id) {
	document.getElementById(id).style.height = "100%";
}

function closeButtons(id) {
	document.getElementById(id).style.height = "0%";
	stopInactiveTimer();
}

function toggleButtons(id) {
	if (isButtonsClosed(id))
		openButtons(id);
	else
		closeButtons(id);

}

function isButtonsClosed(id){
	return document.getElementById(id).style.height === "0%";
}

function showError(err_context, err_msg, ui_display, show_retry=true){
	console.error(err_context + ": " + err_msg);

	if (ui_display === true){
		$('#errorDialogText')[0].innerHTML = err_msg;
		$('#errorDialog').modal('show');
		(show_retry) ? $('#errorRefresh').show() : $('#errorRefresh').hide();
	}
}