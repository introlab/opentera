var videoSources = [];
var currentVideoSourceIndex = 0;
var timerHandle = 0;

function initLocalVideo(tag){
	video = document.querySelector(tag);

	navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mediaDevices.getUserMedia || navigator.msGetUserMedia || navigator.oGetUserMedia;

	if (navigator.getUserMedia) {
		//navigator.getUserMedia({video: true, audio: false}, handleVideo, videoError);
		navigator.mediaDevices.getUserMedia({video: true, audio: false}).then(handleVideo).catch(videoError);
	}
}
function handleVideo(stream) {
	var video = document.getElementById("selfVideo");

	//console.log("Success! Device Name: " + stream.getVideoTracks()[0].label);
	video.srcObject = stream;
	//video.src = URL.createObjectURL(stream);

	fillVideoSourceList();
}

function videoError(e) {
	// do something
	console.error(e);
}


function fillVideoSourceList(){
	videoSources.length=0;
	var select = document.getElementById('videoSelect');
	select.options.length = 0;
	var count = 0;

	navigator.mediaDevices.enumerateDevices()
	.then(function(devices) {
		devices.forEach(function(device) {
			if (device.kind=="videoinput"){
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
			select.selectedIndex = currentVideoSourceIndex;
			//console.log(device.kind + ": " + device.label + " id = " + device.deviceId);
		});
	})
	.catch(function(err) {
		console.log(err.name + ": " + err.message);
	});
}

function updateVideoSource(){
	var select = document.getElementById('videoSelect');
	if (select.selectedIndex>=0){
		currentVideoSourceIndex = select.selectedIndex;
		var constraints = { deviceId: { exact: videoSources[currentVideoSourceIndex].deviceId } };
		//console.log(constraints);
		navigator.mediaDevices.getUserMedia({video: constraints}).then(handleVideo).catch(videoError);
	}
}

function selectVideoSource(source){
	video = JSON.parse(source);
	for (var i=0; i<videoSources.length; i++){
		if (videoSources[i].label.includes(video.name)){
			var select = document.getElementById('videoSelect');
			select.selectedIndex = i;
			updateVideoSource();
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
	return document.getElementById(id).style.height == "0%";
}