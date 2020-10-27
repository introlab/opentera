var shownVideos = 0;
var needToCallOtherUsers;
var largeViewId = "#selfView";
var smallViewIds = ["#remoteView1","#remoteView2","#remoteView3","#remoteView4"];

//var localContact = {'easyid':0, 'name':'Unknown' + Math.floor(Math.random()*100),'uuid':'00000000-0000-0000-0000-000000000000'};
var localContact = {'easyid':0, 'name':'','uuid':'00000000-0000-0000-0000-000000000000'};
var remoteContacts = []; // Used to store informations about everyone that has connected (contactinfos)

var localPTZCapabilities = {'uuid':0, 'zoom':false,'presets':false,'settings':false};
var localCapabilities = {'video2':false};

var videoSources = [];
var audioSources = [];

//var videoStreams = [];
var currentVideoSourceIndex = -1;
var currentAudioSourceIndex = -1;
var currentMiniVideoSourceIndex = -1;
var currentMiniAudioSourceIndex = -1;

var easyids = ["0", "0", "0", "0", "0"]; //0 = Local, 1,2,3,4... = distants
var uuids = ["0", "0", "0", "0", "0"]; //0 = Local, 1,2,3,4... = distants
var titles = ["","","","",""];//0 = Local, 1,2,3,4... = distants
var timerHandle = 0;
var connected = false;

var debounceWheel = 0;
var accessDenied = true;

// Control flags
var deviceEnumCompleted = false;
var initialSourceSelect = false;
var teraConnected = false;
var isWeb = false;


function initSystem(){	
	var urlParams = new URLSearchParams(window.location.search);
	isWeb = (urlParams.get('source') == 'web');
	
	// This function is rendered in the main html document
	var port = getTeraPlusPort();
	var websocket_path =  "/websocket/" + port
	easyrtc.setSocketUrl(window.location.origin, {path: websocket_path});

	if (!isWeb){
		// Include files
		//include("qrc:///qtwebchannel/qwebchannel.js");
		//connectWebSockets();
	}
		
	deviceEnumCompleted = false;
	initialSourceSelect	=false;
	
	var local_uuid = urlParams.get('uuid');
	if (local_uuid)
		localContact.uuid = local_uuid;
		
	var local_name = urlParams.get('name');
	if (local_name)
		localContact.name = local_name;
	
	// Initialize
	initLocalVideo(); // Required to get devices labels
	fillDefaultSourceList();
	resetVideosPos();	
	
}


function include(filename)
{
   var head = document.getElementsByTagName('head')[0];

   var script = document.createElement('script');
   script.src = filename;
   script.type = 'text/javascript';

   head.appendChild(script)
}   

function triggerIceRestart() {
   var caller = easyrtc.getIthCaller(0);
   if( caller ) {
      easyrtc.renegotiate(caller);
   }
}



function iceCandidateFilter( iceCandidate, fromPeer) {
   var sdp = iceCandidate.candidate;
   if( sdp.indexOf("typ relay") > 0) { // is turn candidate
   	return iceCandidate;
   }
   else if( sdp.indexOf("typ srflx") > 0) { // is turn candidate
   	return iceCandidate;
   }
   else if( sdp.indexOf("typ host") > 0) { // is turn candidate
   	return iceCandidate;
   }
   else {
      console.log("Unrecognized type of ice candidate, passing through: " + sdp);
      return iceCandidate;
   }
}

function connect() {
	
	console.log("Connecting...");
	// Video settings
	var select = document.getElementById('videoSelect');

	/*var localFilter = easyrtc.buildLocalSdpFilter( {
		audioRecvBitrate:20, videoRecvBitrate:30 ,videoRecvCodec:"h264"
	});
	var remoteFilter = easyrtc.buildRemoteSdpFilter({
		audioSendBitrate: 20, videoSendBitrate:30 ,videoSendCodec:"h264"
	});*/
	
	//easyrtc.setSdpFilters(localFilter, remoteFilter);

	//Pre-connect Event listeners
	easyrtc.setRoomOccupantListener(updateRoomUsers);
	//easyrtc.setIceCandidateFilter(iceCandidateFilter);
	easyrtc.setRoomEntryListener(function(entry, roomName) {
		needToCallOtherUsers = true;
	});
	
	easyrtc.setStreamAcceptor(newStreamStarted);
	easyrtc.setOnStreamClosed(streamDisconnected);
	easyrtc.setPeerListener(dataReception);
			
	//Post-connect Event listeners	
	//easyrtc.setOnHangup(streamDisconnected);
	//easyrtc.setOnCall(newStreamStarted);
	
	//console.log("Connecting local media source: " + currentVideoSourceIndex + ", " + currentAudioSourceIndex);
	/*if (currentVideoSourceIndex<0)
		currentVideoSourceIndex=0;
		
	if (currentAudioSourceIndex<0)
		currentAudioSourceIndex=0;*/
	 //easyrtc.setVideoSource(videoSources[currentVideoSourceIndex].deviceId);
	 //easyrtc.setAudioSource(audioSources[currentAudioSourceIndex].deviceId);
/*
	 easyrtc._presetMediaConstraints={audio:{
            deviceId: {
                exact: audioSources[currentAudioSourceIndex].deviceId
            }},
            video: {
			deviceId: {
                exact: videoSources[currentVideoSourceIndex].deviceId
            }}
        }
	easyrtc.initMediaSource(
	function(stream){
		easyrtc.setVideoObjectSrc(document.getElementById("selfVideo"), stream);
		//easyrtc.connect("TeraPlus", loginSuccess, loginFailure);
		connected = true;
	
		updateVideoSource(true);
	},
	function(errorCode, errorText){
	console.error (errorCode + " - " +  errorText);
	});
*/
	connected = true;
	updateVideoSource(true);

	if (!isWeb){
		// Include files
		//include("qrc:///qtwebchannel/qwebchannel.js");
		//connectWebSockets();
	}
	
	
 }

function dataReception(sendercid,msgType,msgData,targeting) {
	console.log("dataReception : src=" + sendercid + " type=" + msgType + " data=" + msgData + " target=" + targeting.targetEasyrtcid);
	
	if (msgType=="contactInfo"){
		// Save contact info
		
		var found = false;
		for (var i=0; i<remoteContacts.length; i++){
			console.log(remoteContacts[i].easyid + " == " + sendercid + "?");
			if (remoteContacts[i].easyid===sendercid){
				remoteContacts[i] = msgData;
				found = true;
				console.log("Found contact - " + i);
				break;
			}
		}
		
		if (found==false && msgData.uuid != uuids[0]){
			remoteContacts[remoteContacts.length] = msgData;
			console.log("Not found - added: " + msgData.name + " " + sendercid + " " + localContact.easyid + " " + msgData.uuid);
		}
	
		updateRemoteContactsInfos();
	}
	
	if (msgType=="PTZRequest"){
		//console.error("PTZRequest");
		//console.error(msgData);
		if (teraConnected)
			SharedObject.imageClicked(localContact.uuid, msgData.x, msgData.y, msgData.w, msgData.h);
		else
			console.error("Not connected to client.");
	}
	
	if (msgType=="ZoomRequest"){
		//console.error("ZoomRequest");
		//console.error(msgData);
		if (teraConnected){
			if (msgData.value=="in")
				SharedObject.zoomInClicked(localContact.uuid);
			if (msgData.value=="out")
				SharedObject.zoomOutClicked(localContact.uuid);
			if (msgData.value=="min")
				SharedObject.zoomMinClicked(localContact.uuid);
			if (msgData.value=="max")
				SharedObject.zoomMaxClicked(localContact.uuid);
		}else
			console.error("Not connected to client.");
	}
	
	if (msgType=="PresetRequest"){
		//console.error("PresetRequest");
		//console.error(msgData);
		
		//SharedObject.gotoPresetClicked(msgData.event, localContact.uuid, msgData.preset);
		
		var event =[];
		
		if (msgData.set == "true"){
			event.shiftKey = true;
			event.ctrlKey = true;
		}
		
		gotoPreset(event, 0, msgData.preset);
	}
	
	if (msgType=="CamSettingsRequest"){
		//console.error("CamSettingsRequest");
		//console.error(msgData);
		//SharedObject.camSettingsClicked(localContact.uuid);
		if (teraConnected){
			for (var i=0; i<5; i++){
			console.log(easyids[i] + " == " + sendercid + "?");
				if (easyids[i] == sendercid){
					SharedObject.camSettingsClicked(uuids[i]);
					break;
				}
			}
		}else
			console.error("Not connected to client.");
	}
	
	if (msgType=="DataForwarding"){
		if (teraConnected)
			SharedObject.dataForwardReceived(msgData);
		else
			console.error("Not connected to client.");
	}
	
	if (msgType=="muteMicro"){
		console.log("muteMicro: " + msgData.subindex);
		muteMicro(0, msgData.subindex);
		/*if (msgData.subindex=="")
			muteMicro(0);	
		else
			muteMicro(-1);*/
	}
	
	if (msgType=="muteSpeaker"){
		muteSpeaker(0);
	}
	
	if (msgType=="addVideo"){
		addLocalSource2(0);
	}
	
	if (msgType=="removeVideo"){
		removeLocalSource2(0);
	}
	
	if (msgType=="updatePTZCapabilities"){
		setPTZCapabilities(msgData.uuid, msgData.zoom, msgData.presets, msgData.settings);
	}
	
	if (msgType=="updateCapabilities"){
		setCapabilities(sendercid, msgData.video2);
	}
	
	if (msgType=="updateStatus"){
		//console.log(msgData);
		if (msgData.micro != undefined){
			// Find index to update
			//console.error("Micro: " + msgData.micro);
			for (i=0; i<5; i++){
				if (easyids[i] == msgData.easyid){
					updateMicStatus(msgData.micro==="true", i,0);
				}
			}
		}
		
		if (msgData.micro2 != undefined){
			// Find index to update
			//console.error("Micro: " + msgData.micro);
			for (i=0; i<5; i++){
				if (easyids[i] == msgData.easyid){
					updateMicStatus(msgData.micro2==="true", i,1);
				}
			}
		}
		
		if (msgData.speaker != undefined){
			// Find index to update
			//console.error("Speaker: " + msgData.speaker);
			for (i=0; i<5; i++){
				if (easyids[i] == msgData.easyid){
					updateSpeakerStatus(msgData.speaker==="true", i);
				}
			}
		}
	}
}

/////////////////////////////////////////////////////////////////////////////////
// VIDEO / AUDIO DEVICES MANAGEMENT
/////////////////////////////////////////////////////////////////////////////////
// Get default devices - names won't be OK since no connection done yet.
var test;
function fillDefaultSourceList(){
	console.log("fillDefaultSourceList()");
	videoSources.length=0;
	audioSources.length=0;

	// Main video source selector
	var select = document.getElementById('videoSelect');
	select.options.length = 0;
	
	// Main audio source selector
	var audioSelect = document.getElementById('audioSelect');
	audioSelect.options.length = 0;
	
	// Secondary video source selector
	var select2 = document.getElementById('videoSelect2');
	select2.options.length = 0;
	select2.options[select2.options.length] = new Option("Aucune", 0);
	
	// Secondary audio source selector
	var audioSelect2 = document.getElementById('audioSelect2');
	audioSelect2.options.length = 0;
	audioSelect2.options[audioSelect2.options.length] = new Option("Aucune", 0);
	
	// Open a stream to ask for permissions and allow listing of full name of devices.
	navigator.mediaDevices.getUserMedia({ audio: true, video: true }).then(function(stream) {
		if (stream.stop !== undefined){
			console.log("stream.stop()");
			stream.stop();
		}else
			stream.getVideoTracks()[0].stop();
		navigator.mediaDevices.enumerateDevices()
		.then(function(devices) {
			devices.forEach(function(device) {
				if (device.kind=="videoinput"){
					videoSources[videoSources.length] = device;
					var name = device.label;
					if (name=="") name = "Camera #" + videoSources.length;
					//console.log("Adding video source: " + name);
					select.options[select.options.length] = new Option(name, device.deviceId);
					select2.options[select.options.length] = new Option(name, device.deviceId);
					
				}
				
				if (device.kind=="audioinput"){
					audioSources[audioSources.length] = device;
					//console.log(device);
					var name = device.label;
					//if (name=="") name = "Microphone #" + audioSources.length;
					if (name=="") name = device.deviceId;
					audioSelect.options[audioSelect.options.length] = new Option(name, device.deviceId);
					audioSelect2.options[audioSelect2.options.length] = new Option(name, device.deviceId);
				}
				
			}
			);
			// Ensure correct video is selected
			//updateVideoSource();
			select.selectedIndex = currentVideoSourceIndex;
			select2.selectedIndex = currentMiniVideoSourceIndex+1;
			audioSelect.selectedIndex = currentAudioSourceIndex;
			audioSelect2.selectedIndex = currentMiniAudioSourceIndex+1;
			

			deviceEnumCompleted = true;	
			if (!connected && (!teraConnected || (teraConnected && initialSourceSelect)))
				connect();
		})
		.catch(function(err) {
			console.error(err.name + ": " + err.message);
		});

		if (currentMiniVideoSourceIndex==-1 && currentMiniAudioSourceIndex==-1){
			//console.log("No secondary video for now.");
			hideElement("imgAddVid2");
			hideElement("miniMicStatus");
		}else{
			//console.log("Has secondary video source.");
			showElement("imgAddVid2");
		}
	})
	.catch(function(err) {
		console.error(err.name + ": " + err.message);
	});
}

function fillVideoSourceList(list){
	console.log("fillVideoSourceList() - Test");
	console.log(list);

	videoSources.length=0;
	var select = document.getElementById('videoSelect');
	select.options.length = 0;
	
	var select2 = document.getElementById('videoSelect2');
	select2.options.length = 0;
	select2.options[select2.options.length] = new Option("Aucune", 0);
		
	for (var i=0; i<list.length; i++){
		videoSources[i] = list[i];
		//select.options[select.options.length] = new Option(list[i].label.substring(0,list[i].label.length-12), list[i].id);
		select.options[select.options.length] = new Option(list[i].label, list[i].deviceId);
		select2.options[select2.options.length] = new Option(list[i].label, list[i].deviceId);
	}
	//select.options[select.options.length] = new Option("Capture écran", "0");
	select.selectedIndex = currentVideoSourceIndex;
	select2.selectedIndex = currentMiniVideoSourceIndex+1;
	
	/*if (select.options.length<2){
		hideElement("sourceselector"); // Hide if only one video source
	}else{
		showElement("sourceselector");
	}*/
}

function fillAudioSourceList(list){
	audioSources.length=0;
	console.log("fillAudioSourceList()");
	console.log(list);
	
	var select = document.getElementById('audioSelect');
	select.options.length = 0;
	
	var select2 = document.getElementById('audioSelect2');
	select2.options.length = 0;
	select2.options[select2.options.length] = new Option("Aucune", 0);

	for (var i=0; i<list.length; i++){
		audioSources[i] = list[i];
		var name = list[i].label;
		if (name=="") name = list[i].deviceId;
		select.options[select.options.length] = new Option(name, list[i].deviceId);
		select2.options[select2.options.length] = new Option(name, list[i].deviceId);
	}

	select.selectedIndex = currentAudioSourceIndex;
	select2.selectedIndex = currentMiniAudioSourceIndex+1;
}


/////////////////////////////////////////////////////////////////////////////////
// LOCAL STREAM MANAGEMENT
/////////////////////////////////////////////////////////////////////////////////
function updateVideoSource(force=false){
	var select = document.getElementById('videoSelect');
	var audioSelect = document.getElementById('audioSelect');

	console.log("updateVideoSource(" + force + ")");
	if (/*select.selectedIndex>=0 && */(select.selectedIndex != currentVideoSourceIndex || audioSelect.selectedIndex != currentAudioSourceIndex || force)){
		
		if (currentVideoSourceIndex == -1){
			console.log("No video specified - looking for default...");
			var found = false;
			for (var i=0; i<videoSources.length; i++){
				console.log("Video = " + videoSources[i].label + " ?");
				if (videoSources[i].label.toLowerCase().includes("avant") || videoSources[i].label.toLowerCase().includes("front")){
					console.log("Found source at: " + i);
					select.selectedIndex = i;
					found = true;
					break;
				}
			}
			if (!found){
				console.log("Default not found - using first one in the list.");
				select.selectedIndex = 0;
			}
		}
			
		if (currentAudioSourceIndex == -1)
			audioSelect.selectedIndex = 0; // Default audio
			
		currentVideoSourceIndex = select.selectedIndex;
		currentAudioSourceIndex = audioSelect.selectedIndex;
		
		if (connected){
			console.log("Updating video source...");
			//easyrtc.closeLocalMediaStream();
			easyrtc.disconnect();
			
			//easyrtc.setVideoSource(videoSources[currentVideoSourceIndex].deviceId);
			//easyrtc.setAudioSource(audioSources[currentAudioSourceIndex].deviceId);
			easyrtc._presetMediaConstraints={audio:{
            deviceId: {
					exact: audioSources[currentAudioSourceIndex].deviceId
				}},
				video: {
				deviceId: {
					exact: videoSources[currentVideoSourceIndex].deviceId
				}}
			}
			easyrtc.enableAudio(true);
			easyrtc.enableVideo(true);
			easyrtc.closeLocalMediaStream();
			easyrtc.initMediaSource(
			function(stream){
				if (stream.active){
					easyrtc.setVideoObjectSrc(document.getElementById("selfVideo"), stream);
					console.log("Connecting to session...");
					easyrtc.connect("TeraPlus", loginSuccess, loginFailure);
				}else{
					console.log("Got local stream - waiting for it to become active...");
				}
			},
			function(errorCode, errorText){
             console.error (errorCode + " - " +  errorText);
			});
			
		}else{
			
		
		}
	}else{
		
	}
	
	select = document.getElementById('videoSelect2');
	audioSelect = document.getElementById('audioSelect2');
	if (select.selectedIndex==0 && audioSelect.selectedIndex==0){
		//console.log("updateVideoSource: No secondary video for now.");
		hideElement("imgAddVid2");
		hideElement("miniMicStatus");
	}else{
		//console.log("updateVideoSource: Has secondary video source.");
		if (!isElementVisible("imgRemoveVid2"))
			showElement("imgAddVid2");
	}
}

function configChanged(){
	var select = document.getElementById('videoSelect2');
	var audioSelect = document.getElementById('audioSelect2');

	if (currentMiniVideoSourceIndex != select.selectedIndex-1 || currentMiniAudioSourceIndex != audioSelect.selectedIndex-1){
		// Secondary video source changed
		if (isElementVisible("selfVideo2")){
			// Change video source
			addLocalSource2(0);
		}
	}
	
	currentMiniVideoSourceIndex = select.selectedIndex-1;
	currentMiniAudioSourceIndex = audioSelect.selectedIndex-1;
	
	updateVideoSource();
	
	if (currentMiniVideoSourceIndex != -1 || currentMiniAudioSourceIndex != -1){
		localCapabilities.video2 = true;
	}else{
		localCapabilities.video2 = false;
	}
	
	broadcastlocalCapabilities();
}

/////////////////////////////////////////////////////////////////////////////////
// SECONDARY STREAM MANAGEMENT
/////////////////////////////////////////////////////////////////////////////////
function addLocalSource2(index){

	if (index != 0){
		// Send request to remote
		if (easyrtc.webSocketConnected){
			easyrtc.sendDataWS( easyids[index], 'addVideo', request, function(ackMesg) {
				//console.error("ackMsg:",ackMesg);
				if( ackMesg.msgType === 'error' ) {
					console.error(ackMesg.msgData.errorText);
				}
			});
		}
		
		// Change displayed icon
		hideElement(getAddVideoIconId(index));
		showElement(getRemoveVideoIconId(index));
		return;
	}

	// Set and display local secondary video source
	var select = document.getElementById('videoSelect2');
	var audioSelect = document.getElementById('audioSelect2');
	
	var media = {};
	if (currentMiniVideoSourceIndex>=0){
		//easyrtc.setVideoSource(videoSources[currentMiniVideoSourceIndex].deviceId);
		media.video = {deviceId: {exact: videoSources[currentMiniVideoSourceIndex].deviceId}};
		easyrtc.enableVideo(true);
	}else
		easyrtc.enableVideo(false);
		
	if (currentMiniAudioSourceIndex>=0){
		//easyrtc.setAudioSource(audioSources[currentMiniAudioSourceIndex].deviceId);
		media.audio = {deviceId: {exact: audioSources[currentMiniAudioSourceIndex].deviceId}};
		easyrtc.enableAudio(true);
	}else{
		easyrtc.enableAudio(false);
	}
	
	if (currentMiniVideoSourceIndex == -1 && currentMiniAudioSourceIndex == -1){
		// Nothing to show here, move on!
		removeLocalSource2();
		return;
	}
	
	easyrtc._presetMediaConstraints=media;
	
	easyrtc.initMediaSource(
		function(stream){
			easyrtc.setVideoObjectSrc(document.getElementById("selfVideo2"), stream);
			for (var i=1; i<4; i++){
				if (easyids[i]!=0){
					if (isElementVisible("selfVideo2")){
						easyrtc.addStreamToCall(easyids[i], "miniVideo",null);
					}
				}
			}
		},
	function(errorCode, errorText){
		console.error (errorCode + " - " +  errorText);
	}, "miniVideo");
			
	
	showElement("selfVideo2");
	hideElement("imgAddVid2");
	showElement("imgRemoveVid2");
	showElement("swapBtn");
	if (currentMiniAudioSourceIndex>=0){
		showElement("miniMicStatus");
		updateMicStatus(true, -1, 1);
		if (currentMiniVideoSourceIndex == -1){
			showElement("imgSpeaker");
			hideElement("swapBtn");
		}else
			hideElement("imgSpeaker");
	}else
		hideElement("miniMicStatus");
	
}

function removeLocalSource2(index){
	if (index != 0){
		// Send request to remote
		if (easyrtc.webSocketConnected){
			easyrtc.sendDataWS( easyids[index], 'removeVideo', request, function(ackMesg) {
				//console.error("ackMsg:",ackMesg);
				if( ackMesg.msgType === 'error' ) {
					console.error(ackMesg.msgData.errorText);
				}
			});
		}
		return;
	}

	easyrtc.setVideoObjectSrc(document.getElementById("selfVideo2"),"");
	easyrtc.disconnect();
	/*easyrtc.initMediaSource(
	function(stream){
		easyrtc.setVideoObjectSrc(document.getElementById("selfVideo"), stream);
		easyrtc.connect("TeraPlus", loginSuccess, loginFailure);
	},
	function(errorCode, errorText){
	 console.error (errorCode + " - " +  errorText);
	});*/
	updateVideoSource(true);
	
	hideElement("selfVideo2");
	if (currentMiniVideoSourceIndex == -1 && currentMiniAudioSourceIndex == -1){
		console.log("removeLocalSource2: Hiding secondary source indicator.");
		hideElement("imgAddVid2");
	}else{
		console.log("removeLocalSource2: Showing secondary source indicator.");
		showElement("imgAddVid2");
	}
	hideElement("imgRemoveVid2");
	hideElement("swapBtn");
	hideElement("miniMicStatus");
	hideElement("imgSpeaker");
	
	document.getElementById("selfVideo").className = "";
	document.getElementById("selfVideo2").className = "minivideo";
}

function swapLocalSources(){
	/*easyrtc.setVideoObjectSrc(document.getElementById("selfVideo"), videoStreams[currentMiniVideoSourceIndex]);
	easyrtc.setVideoObjectSrc(document.getElementById("selfVideo2"), videoStreams[currentVideoSourceIndex]);*/
	var tempName = document.getElementById("selfVideo").className;
	document.getElementById("selfVideo").className = document.getElementById("selfVideo2").className;
	document.getElementById("selfVideo2").className = tempName;
	var temp = currentVideoSourceIndex;
	currentVideoSourceIndex = currentMiniVideoSourceIndex;
	currentMiniVideoSourceIndex = temp;
	
	temp = currentAudioSourceIndex;
	currentAudioSourceIndex = currentMiniAudioSourceIndex;
	currentMiniAudioSourceIndex = temp;
}


function selectVideoSource(source){
	
	video = JSON.parse(source);
	console.log("Selecting Video: " + video.name + ", index: " + video.index + "(" + videoSources.length + " total)");
	//console.log(videoSources);
	var found = false;
	var select = document.getElementById('videoSelect');
	for (var i=0; i<videoSources.length; i++){
		console.log("Video = " + videoSources[i].label + " ?");
		if (videoSources[i].label.includes(video.name)){
			console.log("Found source at: " + i);
			
			select.selectedIndex = i;
			updateVideoSource(true);
			found = true;
			break;
		}
	}
	
	if (!found){
		if (video.index !== undefined){
			console.log("Selected by index.");
			select.selectedIndex = video.index;
			currentVideoSourceIndex = video.index;
			updateVideoSource(true);
		}
	}
	
	if (teraConnected && !connected && deviceEnumCompleted)
			connect();
			
	initialSourceSelect = true;
	
}

function selectAudioSource(source){
	
	audio = JSON.parse(source);
	console.log("Selecting Audio: " + audio.name + "(" + audioSources.length + " total)");
	//console.log(audioSources);
	var found = false;
	var select = document.getElementById('audioSelect');
	for (var i=0; i<audioSources.length; i++){
		var name = audioSources[i].label;
		if (name == "")
			name = audioSources[i].deviceId;
			
		console.log("Audio = " + name + " ?");
		if (name.includes(audio.name)){
			console.log("Found source at: " + i);
			
			select.selectedIndex = i;
			updateVideoSource(true);
			found = true;
			break;
		}
	}
	
	/*if (teraConnected && !connected && deviceEnumCompleted)
			connect();*/
			
	//initialSourceSelect = true;
	
}

function selectSecondSources(source){
	
	sources = JSON.parse(source);
	console.log("Selecting Second Sources: Video = " + sources.video + ", Audio = " + sources.audio);
	
	// Video
	var select = document.getElementById('videoSelect2');
	var found = false;
	if (sources.video != ""){
		for (var i=0; i<videoSources.length; i++){
			console.log("Video = " + videoSources[i].label + " ?");
			if (videoSources[i].label.includes(sources.video)){
				console.log("Found source at: " + i);
				
				select.selectedIndex = i + 1;
				currentMiniVideoSourceIndex = i;
				found = true;
				break;
			}
		}
	}
	
	if (!found){
		select.selectedIndex = 0;
		currentMiniVideoSourceIndex = -1;
	}
	
	// Audio
	select = document.getElementById('audioSelect2');
	found = false;
	if (sources.audio != ""){
		for (var i=0; i<audioSources.length; i++){
			console.log("Audio = " + audioSources[i].label + " ?");
			if (audioSources[i].label.includes(sources.audio)){
				console.log("Found source at: " + i);
				
				select.selectedIndex = i + 1;
				currentMiniAudioSourceIndex = i;
				found = true;
				break;
			}
		}
	}
	
	if (!found){
		select.selectedIndex = 0;
		currentMiniAudioSourceIndex = -1;
	}
	
	if (sources.audio != "" || sources.video != ""){
		showElement("imgAddVid2");
		localCapabilities.video2 = true;
	}else{
		hideElement("imgAddVid2");
		hideElement("miniMicStatus");
		localCapabilities.video2 = false;
	}
	
	broadcastlocalCapabilities();
	
	updateVideoSource();
}

function updateRemoteContactsInfos(){
	// Find target id to update
	//console.log("updateRemoteContactsInfos()");
	
	// Count number of streams for each contacts
	var streams = [];
	for (var i=0; i<remoteContacts.length; i++){
		streams[i] = 0;
		for (var j=1; j<5; j++){
			if (easyids[j]==remoteContacts[i].easyid){
				streams[i] = streams[i] + 1;
			}
		}
	}
	
	//console.log(streams[0]);
	
	for (var i=0; i<remoteContacts.length; i++){
		for (var j=1; j<5; j++){
			if (easyids[j]==remoteContacts[i].easyid){
				//console.log("Found at " + j);
				uuids[j] = remoteContacts[i].uuid;
				setTitle(j,remoteContacts[i].name);
				
				if (remoteContacts[i].ptz != undefined){
					// Set PTZ icon
					zoom_tag = "zoomButtons" + j;
					presets_tag = "presetButtons" + j;
					settings_tag = "settingsButton" + j;
					
					showElement(zoom_tag);
					showElement(settings_tag);
					
					// Update display
					if (remoteContacts[i].ptz.zoom)
						showElement(zoom_tag);
					else
						hideElement(zoom_tag);
						
					if (remoteContacts[i].ptz.presets)
						showElement(presets_tag);
					else
						hideElement(presets_tag);
					
					if (remoteContacts[i].ptz.settings)
						showElement(settings_tag);
					else
						hideElement(settings_tag);
				}
				
				var addIcon = getAddVideoIconId(j);
				var removeIcon = getRemoveVideoIconId(j);
				
				if (streams[i]==1){
					
					if (remoteContacts[i].capabilities != undefined){
						// Set secondary camera capability
						if (remoteContacts[i].capabilities.video2){
							if (!isElementVisible(removeIcon)){
								showElement(addIcon);
							}else{
								hideElement(addIcon);
							}
						}else{
							hideElement(addIcon);
						}
					}else{
						hideElement(addIcon);
						hideElement(removeIcon);
					}
				}else{
					hideElement(addIcon);
				}

			}
		}
	}
}

function setupSharedObjectCallbacks(channel) {

    //console.log("setupSharedObjectCallbacks");

    //connect to a signal
    channel.objects.SharedObject.newContactInformation.connect(updateContact);
	channel.objects.SharedObject.newVideoSource.connect(selectVideoSource);
	channel.objects.SharedObject.newAudioSource.connect(selectAudioSource);
	channel.objects.SharedObject.newDataForward.connect(forwardData);
	channel.objects.SharedObject.newSecondSources.connect(selectSecondSources);

    //Request contact info...
    channel.objects.SharedObject.getContactInformation();
	
	// Request current audio source
	channel.objects.SharedObject.getCurrentAudioSource();

	// Request current camera
	channel.objects.SharedObject.getCurrentVideoSource();
	
	// Request secondary sources
	channel.objects.SharedObject.getSecondSources();
	
	// Mirror effect
	if (channel.objects.SharedObject.getLocalMirror){
		channel.objects.SharedObject.setLocalMirrorSignal.connect(setLocalMirror);
		channel.objects.SharedObject.getLocalMirror();
	}else
		console.log("No mirror settings.");
	
}

function connectWebSockets() {
	var baseUrl = "ws://localhost:12345";
	console.log("Connecting to WebSocket server at " + baseUrl + ".");
	var socket = new WebSocket(baseUrl);

	socket.onclose = function()
	{
		console.error("web channel closed");
		teraConnected = false;
	};

	socket.onerror = function(error)
	{
		console.error("web channel error: " + error);
		
	};

	socket.onopen = function()
	{
		
		console.log("Websocket connected");
		
		
		new QWebChannel(socket, function(channel) {

		//global object
		window.SharedObject = channel.objects.SharedObject;
		
		setupSharedObjectCallbacks(channel);

		});
		teraConnected = true;

	}
}

function setLocalMirror(mirror)
{
	if (mirror){
		document.getElementById("selfVideo").className = "easyrtcMirror";
		document.getElementById("selfVideo2").className = "minivideo easyrtcMirror";
	}else{
		document.getElementById("selfVideo").className = "";
		document.getElementById("selfVideo2").className = "minivideo";
	}
	
}

function updateContact(contact)
{
    //Contact should be a JSON object
    console.log("Update contact : " + contact);
	var easyid = localContact.easyid;
    localContact = JSON.parse(contact);
	localContact.easyid = easyid;
	
	uuids[0] = localContact.uuid;
	localPTZCapabilities.uuid = localContact.uuid;
	//localCapabilities.uuid = localContact.uuid;
	setTitle(0, localContact.name);
	
}

 
 function updateRoomUsers(roomName, occupants, isPrimary) {
	shownVideos = 0;
	for(var easyrtcid in occupants) {
		if (easyrtcid !== easyids[0]){
			shownVideos++;
			if (needToCallOtherUsers) {
				easyrtc.call(
					easyrtcid,
					//newStreamStarted,
					null,
					//streamDisconnected,
					null,
					//null
					null,
					//easyrtc.getLocalMediaIds()
					null
				)
			}
			
			//sendContactInfo(easyrtcid);
			
			
		}

	}
	needToCallOtherUsers = false;

	resetVideosPos();
 }
 

function sendContactInfo(easyrtcid_target){
		console.log("sending contact info to :",easyrtcid_target);
		console.log(localContact.uuid + " - " + localContact.name);
		//send contact information to other users
		//localContact.easyid = easyids[0];
		if (easyrtc.webSocketConnected){
			easyrtc.sendDataWS( easyrtcid_target, 'contactInfo', localContact, function(ackMesg) {
				//console.error("ackMsg:",ackMesg);
				if( ackMesg.msgType === 'error' ) {
					console.error(ackMesg.msgData.errorText);
				}
			});
		}
}
 
function selectLargeView(id){
	// Find the requested id in the small view and replace it with the current large view
	var index = smallViewIds.indexOf(id);
	inactiveTimeout(); // Hide all controls
	if (index!=-1){
		showElement(getEnlargeButtonId(largeViewId));
		hideElement(getEnlargeButtonId(id));
		smallViewIds[index] = largeViewId;
		largeViewId = id;
		
	}
	resetVideosPos();
}

function getLargeViewId(){
	return largeViewId;
}

function getEnlargeButtonId(video_id){
	var btn = "";
	if (video_id=="#selfView") btn = "largeBtn";
	if (video_id.substr(0,2)=="#r") btn = "largeBtn" + video_id.substr(video_id.length-1,1);
	
	return btn;
}
 
function findFirstEmptyVideoSlot(){
	for (var i=1; i<4; i++){
		if (easyids[i]=="0"){
			return i;
		}
	}
	
	return -1;
}
var rStreamTest;

function newStreamStarted(callerEasyrtcid, stream, streamname){
	console.log ("New Stream from " + callerEasyrtcid + " - Stream " + streamname) ;
	
	if (isWeb){
		// Stops calling sound
		document.getElementById("audioCalling").pause();
	}
	
	//console.log(stream);
	rStreamTest = stream;	

	// Initialize
	//initLocalVideo(); // Required to get devices labels
	//fillDefaultSourceList();
	resetVideosPos();
		
	//if ($.isNumeric(stream)){
	/*if(stream.getVideoTracks().length == 0){
		// Audio only - show icons on correct "parent", if needed
		console.log("newStreamStarted, received only audio track");
		for (var i=1; i<5; i++){
			if (easyids[i] == callerEasyrtcid){
				showElement(getAudioSpeakerIconId(i));
				hideElement(getAddVideoIconId(i));
				showElement(getRemoveVideoIconId(i));
				showElement(getMic2IconId(i));
			}
		}
		return;
	}*/
	
	// Check if already have a stream with that name from that source
	var slot = -1;
	if (streamname=="default"){
		for (var i=1; i<4; i++){
			if (easyids[i] == callerEasyrtcid){
				console.error("Stream default already present for that source. Ignoring.");
				//slot = i;
				break;
			}
		}
	}

	// Find first empty slot
	if (slot==-1)
		slot = findFirstEmptyVideoSlot(); //stream+1
	else{
		// Stream was already there...
	}

	console.log ("Assigning slot " + slot);
	if (slot>=0){
		if (isWeb){
			// Starts connected sound
			document.getElementById("audioConnected").play()
		}
		//console.log("teraConnected = " + teraConnected);
		if (teraConnected){
			//if (SharedObject.newRemoteConnection != undefined){
				console.log("Sending newRemoteConnection()");
				SharedObject.newRemoteConnection();
			//}
		}
		hideElement(getAudioSpeakerIconId(slot));
		hideElement(getAddVideoIconId(slot));
		hideElement(getRemoveVideoIconId(slot));
		hideElement(getMic2IconId(slot));
		
		easyids[slot] = callerEasyrtcid;
		var video = getVideoId(slot);
		easyrtc.setVideoObjectSrc(document.getElementById(video), stream);
		$("#remoteView"+(slot)).parent().show();
		selectLargeView("#remoteView"+(slot));
		
		//shownVideos++;
	
		sendContactInfo(callerEasyrtcid);
		
		// Update video
		//var videoId = getVideoId(0);
		var videoId = getVideoId(slot);
		var video = document.getElementById(videoId);
		
		// Send status update to all
		var micEnabled = "false";
		//if (video.micEnabled || video.micEnabled==undefined)
		if (isMicActive(0,0))
			micEnabled="true";
		var mic2Enabled = "false";
		if (isMicActive(0,1))
			mic2Enabled="true";
			
		var spkEnabled = "false";
		if (video.volume=="1")
			spkEnabled = "true";
		
		// Sends PTZ capabilities
		broadcastlocalPTZCapabilities();
		
		// Sends other capabilities
		broadcastlocalCapabilities();
	
		request = {"easyid": easyids[0], "micro":micEnabled, "micro2":mic2Enabled, "speaker":spkEnabled};

		if (easyrtc.webSocketConnected){
			easyrtc.sendDataWS(callerEasyrtcid, 'updateStatus', request, function(ackMesg) {
				//console.error("ackMsg:",ackMesg);
				if( ackMesg.msgType === 'error' ) {
					console.error(ackMesg.msgData.errorText);
				}
			});
		}
		
		// Add second video, if present
		if (isElementVisible("selfVideo2")){
			console.log("Adding secondary video...");
			easyrtc.addStreamToCall(callerEasyrtcid, "miniVideo");
		}
		
		// Check if we need to display the remove video icon
		if (streamname=="miniVideo"){
			showElement(getRemoveVideoIconId(slot));
			hideElement(getAddVideoIconId(slot));
		}else{
			/*hideElement(getRemoveVideoIconId(slot));
			showElement(getAddVideoIconId(slot));*/
		}
		
		////////////////////////////////
				
		resetVideosPos();
	}else{
		console.error ("No more video slot available in this session.");
	}

	
	updateRemoteContactsInfos();
	
	
}

function streamDisconnected(callerEasyrtcid){
	
	if (accessDenied)
		return;
		
	// Find video slot used by that caller
	var slot = -1;
	for (var i=4; i>0; i--){
		if (easyids[i]==callerEasyrtcid){
			slot = i;
			break;
		}
	}
	
	if (slot == -1){
		console.error ("Stream disconnected: " + callerEasyrtcid  + " - NOT DISPLAYED!");
		return;
	}
	
	console.log ("Stream disconnected: " + callerEasyrtcid + " - Slot " + slot);
	
	if (isWeb){
			// Starts connected sound
			document.getElementById("audioDisconnected").play()
		}
		
	for (var i=slot+1; i<4; i++){
		// Shift all values to have a correct display
		easyids[i-1] = easyids[i];
		easyids[i] = "0";
		titles[i]="";
	}
	easyids[slot] = "0";
	titles[slot] = "";
	
	var removedViewId="#remoteView"+(slot);
	easyrtc.setVideoObjectSrc(document.getElementById(getVideoId(slot)), "");
	
	//console.log("'" + removedViewId + "' / '" + largeViewId + "'");
	
	if (largeViewId==removedViewId){
		if (shownVideos-1==0){
			//console.log("Setting large view as SelfView");
			selectLargeView("#selfView");
			// Reorder views
			smallViewIds = ["#remoteView1","#remoteView2","#remoteView3","#remoteView4"];
		}else{
			//console.log("Setting large view as something else");
			for (var i=0; i<shownVideos; i++){
				if (smallViewIds[i] != "#selfView"){
					selectLargeView(smallViewIds[i]);
					break;
				}
			}
		}
	}
	
	var toRemoveIndex=-1;
	for (var i=0; i<shownVideos; i++){
		if (smallViewIds[i] == removedViewId){
			toRemoveIndex = i;
			break;
		}
	}
	
	if (toRemoveIndex>=0){
		for (var i=toRemoveIndex+1; i<shownVideos; i++){
			var current = smallViewIds[i-1];
			smallViewIds[i-1] = smallViewIds[i];
			smallViewIds[i] = current;
		}
	}
	
	$(removedViewId).parent().hide();
	//shownVideos--;
	resetVideosPos();
}

function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function loginSuccess(easyrtcid) {

	/*if (easyrtc.getRoomFields("default").key.fieldValue !== undefined && easyrtc.getRoomFields("default").key.fieldValue !== ""){
		var key = getParameterByName("key");
		if (key != easyrtc.getRoomFields("default").key.fieldValue){
			easyrtc.closeLocalMediaStream();
			easyrtc.hangupAll();
			easyrtc.disconnect();
			document.getElementById("selfView").style = "display:none;";
			document.getElementById("deniedView").style = "display:block;";
			return;
		}
	}*/

	accessDenied = false;
	//easyrtc.getRoomFields("default").key.fieldValue;
	
	console.log("Login success! easyid = " + easyrtcid);
    //selfEasyrtcid = easyrtcid;
	easyids[0] = easyrtcid;
	localContact.easyid = easyrtcid;

	easyrtc.getVideoSourceList(fillVideoSourceList);
	easyrtc.getAudioSourceList(fillAudioSourceList);
			
	// Sends PTZ capabilities
	broadcastlocalPTZCapabilities();
	
	// Sends other capabilities
	broadcastlocalCapabilities();
	
	if (isWeb){
		// Starts calling sounds
		document.getElementById("audioCalling").play();
	}
	
	
}

function loginFailure(errorCode, message) {

	console.error("Login failure! easyid = " + easyrtcid +": " + message);
    easyrtc.showError(errorCode, message);
}


var video = document.querySelector("#selfVideo");
 
function initLocalVideo(){
	//video = document.querySelector(tag);
				 
	/*navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia || navigator.oGetUserMedia;
	 
	if (navigator.getUserMedia) {       
		navigator.getUserMedia({video: true, audio: true}, handleVideo, videoError);
	}*/
}

function handleVideo(stream) {
	//video.src = window.URL.createObjectURL(stream);
	//stream.getVideoTracks()[0].stop();
	//stream.getAudioTracks()[0].stop();
}
 
function videoError(e) {
	// do something
}

function openButtons(id) {
	//document.getElementById(id).style.height = "100%";
	showElement(id);
}

function closeButtons(id) {
	
	//document.getElementById(id).style.height = "0%";
	hideElement(id);
	stopInactiveTimer();
}

function hideElement(id){
	document.getElementById(id).style.display = "none";
}

function showElement(id){
	document.getElementById(id).style.display = "inline";
}

function isElementVisible(id){
	return document.getElementById(id).style.display == "inline";
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

function getVideoId(index){
	var videoId;
	if (index==0)
		videoId = "selfVideo";
	else
		if (index==-1)
			videoId = "selfVideo2";
		else
			videoId = "remoteVideo" + index;
		
	return videoId;
}

function getMicIconId(index, subindex){
	if (subindex>0)
		return getMic2IconId(index);

	var micIconId = "micStatus";
	if (index>0)
		micIconId = micIconId + index;
	else
		if (index==-1)
			micIconId = "miniMicStatus";
			
	return micIconId;
}

function getMic2IconId(index){
	var micIconId = "miniMicStatus";
	if (index>0)
		micIconId = micIconId + index;
			
	return micIconId;
}

function isMicActive(index, subindex){
	var micIcon = document.getElementById(getMicIconId(index,subindex));
	//console.log(micIcon.src);
	if (micIcon.src.includes("off"))
		return false;
		
	return true;
}

function getSpeakerIconId(index){
	var spkIconId = "speakerStatus";
	if (index>0)
		spkIconId = spkIconId + index;
		
	return spkIconId;
}

function getAudioSpeakerIconId(index){
	var spkIconId = "imgSpeaker";
	if (index>0)
		spkIconId = spkIconId + index;
		
	return spkIconId;
}

function getAddVideoIconId(index){
	var iconId = "imgAddVid2";
	if (index>0)
		iconId = iconId + "_" + index;
		
	return iconId;
}

function getRemoveVideoIconId(index){
	var iconId = "imgRemoveVid2";
	if (index>0)
		iconId = iconId + "_" + index;
		
	return iconId;
}

function getAudioSpeakerIconId(index){
	var spkIconId = "imgSpeaker";
	if (index>0)
		spkIconId = spkIconId + index;
		
	return spkIconId;
}

function muteMicro(index, subindex){
	//console.log("MuteMicro, index = " + index + ", subindex = " + subindex);
	var video = document.getElementById(getVideoId(index));
	var new_state = !isMicActive(index, subindex); //!video.micEnabled;
	/*if (video.micEnabled === undefined)
		new_state = false;*/
	updateMicStatus(new_state, index, subindex);
	
	var stream_name = "";
	if (index==-1)
		stream_name="miniVideo";
			
	var micro_value = "false";
	if (new_state)
		micro_value = "true";
		
	if (index==0){
		
		// Send display update request
		if (subindex==0)
			request = {"easyid": easyids[index], micro:micro_value};
		else
			request = {"easyid": easyids[index], micro2:micro_value};
		
		if (subindex==0)
			easyrtc.enableMicrophone(new_state);
		else
			easyrtc.enableMicrophone(new_state, "miniVideo");
		
		//console.log(request);
		if (easyrtc.webSocketConnected) {
			easyrtc.sendDataWS({"targetRoom": "default"}, 'updateStatus', request, function (ackMesg) {
				//console.error("ackMsg:",ackMesg);
				if (ackMesg.msgType === 'error') {
					console.error(ackMesg.msgData.errorText);
				}
			});
		}
	}else{
		// Request mute to someone else
		request = {"subindex": subindex};
		if (easyrtc.webSocketConnected){
			easyrtc.sendDataWS( easyids[index], 'muteMicro', request, function(ackMesg) {
				//console.error("ackMsg:",ackMesg);
				if( ackMesg.msgType === 'error' ) {
					console.error(ackMesg.msgData.errorText);
				}
			});
		}
	}
}

function updateMicStatus(status, index, subindex){
	//console.log("updateMicStatus, state = " + status + ", index=" + index + ", subindex=" + subindex);

	var micIconId = getMicIconId(index, subindex);
	
	var videoId = getVideoId(index);
			
	var video = document.getElementById(videoId);
	video.micEnabled = status;

	if (video.micEnabled){
		document.getElementById(micIconId).src="images/micro.png";
	}else{
		document.getElementById(micIconId).src="images/micro_off.png";
	}
}

function updateSpeakerStatus(status, index){

	var spkIconId = getSpeakerIconId(index);
	
	var videoId = getVideoId(index);
			
	var video = document.getElementById(videoId);
	if (status){
		video.volume = "1";
		document.getElementById(spkIconId).src="images/speaker.png";
	}else{
		video.volume = "0";
		document.getElementById(spkIconId).src="images/speaker_off.png";
	}

}


function muteSpeaker(index){
	var video = document.getElementById(getVideoId(index));
	var new_state = !(video.volume=="1");

	updateSpeakerStatus(new_state, index);
		
	if (index==0){
		// Send display update request
		if (new_state){
			request = {"easyid": easyids[index], "speaker":"true"};
			video.volume = "1";
		}else{
			request = {"easyid": easyids[index], "speaker":"false"};
			video.volume = "0";
		}

		if (easyrtc.webSocketConnected){
			easyrtc.sendDataWS({"targetRoom":"default"}, 'updateStatus', request, function(ackMesg) {
				//console.error("ackMsg:",ackMesg);
				if( ackMesg.msgType === 'error' ) {
					console.error(ackMesg.msgData.errorText);
				}
			});
		}
	}else{
		// Request mute to someone else
		if (easyrtc.webSocketConnected) {
			easyrtc.sendDataWS(easyids[index], 'muteSpeaker', "", function (ackMesg) {
				//console.error("ackMsg:",ackMesg);
				if (ackMesg.msgType === 'error') {
					console.error(ackMesg.msgData.errorText);
				}
			});
		}
	}
	
}

function muteVideo(){
	alert("TODO");
}
/*
function resetVideosPos(){
	if (accessDenied)
		return;
	var h = document.documentElement.clientHeight;//+15;
	var w = document.documentElement.clientWidth;
		
	$( largeViewId    ).dialog( "option", "height", h);
	if (shownVideos>0)
		$( largeViewId    ).dialog( "option", "width", 2 * (w) / 3);
	else
		$( largeViewId    ).dialog( "option", "width", w);
	
	//$( largeViewId ).dialog( "option", "position",  {my: "left top", at: "left top", of: window});
	$( largeViewId ).dialog( "option", "position",  {my: "right top", at: "right top", of: window});
	
	// Top-left video
	if (shownVideos>=1)
		$( smallViewIds[0] ).dialog( "option", "height", h / 2);
	else
		$( smallViewIds[0] ).dialog( "option", "height", h-1);
		
	if (shownVideos>2)
		$( smallViewIds[0] ).dialog( "option", "width",  ((w) / 3)/2);
	else
		$( smallViewIds[0] ).dialog( "option", "width",  ((w) / 3));
		
	//$( smallViewIds[0] ).dialog( "option", "position",  {my: "left top", at: "right top", of: largeViewId});
	$( smallViewIds[0] ).dialog( "option", "position",  {my: "right top", at: "left top", of: largeViewId});
	
	// Bottom-left video
	$( smallViewIds[1] ).dialog( "option", "height", h / 2);
	if (shownVideos>2)
		$( smallViewIds[1]  ).dialog( "option", "width",  ((w) / 3)/2);
	else
		$( smallViewIds[1]  ).dialog( "option", "width",  ((w) / 3));
	$( smallViewIds[1]  ).dialog( "option", "position",  {my: "left top", at: "left bottom+3", of: smallViewIds[0]});
	
	// Top-right video
	//if (shownVideos>3)
		$( smallViewIds[2] ).dialog( "option", "height", h / 2);
	//else
		//$( smallViewIds[2] ).dialog( "option", "height", h-1);
	$( smallViewIds[2]  ).dialog( "option", "width",  ((w-1) / 3)/2);
	$( smallViewIds[2]  ).dialog( "option", "position",  {my: "left top", at: "right top-4", of: smallViewIds[0]});
	
	
	// Bottom-right video
	$( smallViewIds[3] ).dialog( "option", "height", h / 2);
	$( smallViewIds[3] ).dialog( "option", "width",  ((w-1) / 3)/2);
	$( smallViewIds[3] ).dialog( "option", "position",  {my: "left top", at: "right bottom+3", of: smallViewIds[0]});
}*/

function setTitle(id, title){
	//console.error("Setting title " + id + ": " + title);
	//console.error(uuids);

	var label = "videoLabel";
	if (id!=0){
		label = label + id;
	}
	if (document.getElementById(label)){
		document.getElementById(label).innerText = title;
		titles[id] = title;
	}
}

function setEasyID(id, uuid){
	easyids[id] = uuid;
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
	closeButtons('enlargeButton');
	closeButtons('navButtons1');
	closeButtons('enlargeButton1');
	closeButtons('navButtons2');
	closeButtons('enlargeButton2');
	closeButtons('navButtons3');
	closeButtons('enlargeButton3');
	closeButtons('navButtons4');
	closeButtons('enlargeButton4');
	//hideElement('sourceselector');
}

function setPTZCapabilities(uuid, zoom, presets, settings){
	var zoom_tag = "zoomButtons0";
	var presets_tag = "presetButtons0";
	var settings_tag = "settingsButton0";
	
	var ptz = {'uuid':uuid, 'zoom':zoom,'presets':presets,'settings':settings};
	
	console.log("Setting PTZ Capabilities: " + uuid + " = " + zoom + " " + presets + " " + settings);
	
	if (uuid === 0){
		console.log(" -- UUID = 0, not valid!");
		return;
	}
	
	//if (uuid == uuids[0] || (uuids[0] == 0/* && teraConnected*/)){
	//if (uuid == uuids[0] || (uuids[0] == 0 && teraConnected)){
	if (uuid == uuids[0] || (uuids[0] == 0 && !isWeb)){
		console.log(" -- Local UUID - settings values.");
		// Setting local capabilities
		localPTZCapabilities.zoom = zoom;
		localPTZCapabilities.presets = presets;
		localPTZCapabilities.settings = settings;
		if (uuid !==0)
			localPTZCapabilities.uuid = uuid;
		
		// Update display
		if (zoom)
			showElement(zoom_tag);
		else
			hideElement(zoom_tag);
			
		if (presets)
			showElement(presets_tag);
		else
			hideElement(presets_tag);
		
		if (settings)
			showElement(settings_tag);
		else
			hideElement(settings_tag);

		// Send to remotes
		broadcastlocalPTZCapabilities();
		
		
	}else{
		console.log(" -- Remote UUID received: " + uuid + ", I am " + uuids[0]);
		// Find and update PTZ infos in remoteContacts
		for (var i=0; i<remoteContacts.length; i++){
			if (remoteContacts[i].uuid == uuid){
				remoteContacts[i].ptz = ptz;
				break;
			}
		}
		updateRemoteContactsInfos();
	}

}

function setCapabilities(easyid, video2){
	
	console.log("Setting Capabilities: " + easyid + " = " + video2);
	var cap = {'video2':video2};
	
		
	if (easyid == localContact.easyid){
		console.log(" -- Local ID - settings values.");
		localCapabilities.video2 = video2;
		
	}else{
		console.log(" -- Remote ID received: " + easyid + ", I am " + localContact.easyid);
		// Find and update capabilities in remoteContacts
		for (var i=0; i<remoteContacts.length; i++){
			if (remoteContacts[i].easyid == easyid){
				remoteContacts[i].capabilities = cap;
				break;
			}
		}
		updateRemoteContactsInfos();
	}

}


function broadcastlocalPTZCapabilities(){
		request = localPTZCapabilities;
		if (localPTZCapabilities.uuid != 0 || !teraConnected){
			console.log("Broadcasting PTZ capabilities " + localPTZCapabilities.uuid + " = " + localPTZCapabilities.zoom + " " + localPTZCapabilities.presets + " " + localPTZCapabilities.settings);
			if (easyrtc.webSocketConnected)
				easyrtc.sendDataWS({"targetRoom":"default"}, 'updatePTZCapabilities', request, function(ackMesg) {
					//console.error("ackMsg:",ackMesg);
					if( ackMesg.msgType === 'error' ) {
						console.error(ackMesg.msgData.errorText);
					}
				});
			else{
				console.log("Didn't broadcast: not connected yet!");
			}

		}else
			console.error("PREVENTED PTZ capabilities broadcasting : uuid = 0!");


}

function broadcastlocalCapabilities(){
		request = localCapabilities;

		if (easyrtc.webSocketConnected){
			easyrtc.sendDataWS({"targetRoom":"default"}, 'updateCapabilities', request, function(ackMesg) {
				//console.error("ackMsg:",ackMesg);
				if( ackMesg.msgType === 'error' ) {
					console.error(ackMesg.msgData.errorText);
				}
			});
		}
}


function displaySensorMute(uuid, show){
}

function getVideoCoords(event, index){
	
	var video = document.getElementById(getVideoId(index));
	var offsets = video.getBoundingClientRect();
	
	var video_dims = calculateContainsWindow(video);
	var real_video_width = (video.clientWidth * video_dims.destinationWidthPercentage);
	var bar_width = (video.clientWidth - real_video_width) / 2;
	
	var real_video_height = (video.clientHeight * video_dims.destinationHeightPercentage);
	var bar_height = (video.clientHeight - real_video_height) / 2;
	
	//alert("x=" + (event.clientX - offsets.left) + " y=" + (event.clientY - offsets.top) + " w=" + video.clientWidth + " h=" + video.clientHeight);
	if (index==0){
		if (teraConnected){
			console.log("Local PTZ request");
			//SharedObject.imageClicked(localContact.uuid, video.clientWidth - (event.clientX - offsets.left), event.clientY - offsets.top, video.clientWidth, video.clientHeight);
			SharedObject.imageClicked(localContact.uuid, (event.clientX - bar_width), event.clientY - bar_height, real_video_width, real_video_height);
			// Uncomment next line if using mirror image!
			//SharedObject.imageClicked(localContact.uuid, (event.clientX - offsets.left), event.clientY - offsets.top, video.clientWidth, video.clientHeight);
		}
	}else{
		// Send message to the other client
		console.log("PTZ request to :", easyids[index]);
		//send contact information to other users
		//request = {"x":event.clientX - offsets.left, "y": event.clientY - offsets.top, "w":video.clientWidth, "h": video.clientHeight};
		request = {"x": event.clientX - bar_width - offsets.left, "y": event.clientY - bar_height, "w": real_video_width, "h": real_video_height};
		if (easyrtc.webSocketConnected){
			easyrtc.sendDataWS( easyids[index], 'PTZRequest', request, function(ackMesg) {
				//console.error("ackMsg:",ackMesg);
				if( ackMesg.msgType === 'error' ) {
					console.error(ackMesg.msgData.errorText);
				}
			});
		}
		
	}
}

/*function getVideoCoords(event, index){
	var video = document.getElementById(getVideoId(index));
	var offsets = video.getBoundingClientRect();
	//alert("x=" + (event.clientX - offsets.left) + " y=" + (event.clientY - offsets.top) + " w=" + video.clientWidth + " h=" + video.clientHeight);
	if (index==0){
		if (teraConnected)
			SharedObject.imageClicked(localContact.uuid, video.clientWidth - (event.clientX - offsets.left), event.clientY - offsets.top, video.clientWidth, video.clientHeight);
			// Uncomment next line if using mirror image!
			//SharedObject.imageClicked(localContact.uuid, (event.clientX - offsets.left), event.clientY - offsets.top, video.clientWidth, video.clientHeight);
	}else{
		// Send message to the other client
		//console.error("PTZ request to :", easyids[index]);
		//send contact information to other users
		request = {"x":event.clientX - offsets.left, "y": event.clientY - offsets.top, "w":video.clientWidth, "h": video.clientHeight};
		if (easyrtc.webSocketConnected){
			easyrtc.sendDataWS( easyids[index], 'PTZRequest', request, function(ackMesg) {
				//console.error("ackMsg:",ackMesg);
				if( ackMesg.msgType === 'error' ) {
					console.error(ackMesg.msgData.errorText);
				}
			});
		}
		
	}
}

function getVideoCoords(event, videoId){
	var video = document.getElementById(videoId);
	
	var video_dims = calculateContainsWindow(video);
	var real_video_width = (video.clientWidth * video_dims.destinationWidthPercentage);
	var bar_width = (video.clientWidth - real_video_width) / 2;
	
	var real_video_height = (video.clientHeight * video_dims.destinationHeightPercentage);
	var bar_height = (video.clientHeight - real_video_height) / 2;
	
	//SharedObject.imageClicked(localContact.uuid, video.clientWidth - (event.clientX - video.offsetLeft), event.clientY - video.offsetTop, video.clientWidth, video.clientHeight);
	SharedObject.imageClicked(localContact.uuid, event.clientX - bar_width, event.clientY - bar_height, real_video_width, real_video_height);
}*/

function calculateContainsWindow(image) {
	
	var imageComputedStyle = window.getComputedStyle(image);
	var imageObjectFit = imageComputedStyle.getPropertyValue("object-fit");
	var coordinates = {};
	var imagePositions = imageComputedStyle.getPropertyValue("object-position").split(" ");
	var naturalWidth = image.naturalWidth;
	var naturalHeight= image.naturalHeight;
	if( image.tagName === "VIDEO" ) {
		naturalWidth= image.videoWidth;
		naturalHeight= image.videoHeight;
	}
	var horizontalPercentage = parseInt(imagePositions[0]) / 100;
	var verticalPercentage = parseInt(imagePositions[1]) / 100;
	var naturalRatio = naturalWidth / naturalHeight;
	var visibleRatio = image.clientWidth / image.clientHeight;
	if (imageObjectFit === "none")
	{
	  coordinates.sourceWidth = image.clientWidth;
	  coordinates.sourceHeight = image.clientHeight;
	  coordinates.sourceX = (naturalWidth - image.clientWidth) * horizontalPercentage;
	  coordinates.sourceY = (naturalHeight - image.clientHeight) * verticalPercentage;
	  coordinates.destinationWidthPercentage = 1;
	  coordinates.destinationHeightPercentage = 1;
	  coordinates.destinationXPercentage = 0;
	  coordinates.destinationYPercentage = 0;
	}
	else if (imageObjectFit === "contain" || imageObjectFit === "scale-down")
	{
	  // TODO: handle the "scale-down" appropriately, once its meaning will be clear
	  coordinates.sourceWidth = naturalWidth;
	  coordinates.sourceHeight = naturalHeight;
	  coordinates.sourceX = 0;
	  coordinates.sourceY = 0;
	  if (naturalRatio > visibleRatio)
	  {
		coordinates.destinationWidthPercentage = 1;
		coordinates.destinationHeightPercentage = (naturalHeight / image.clientHeight) / (naturalWidth / image.clientWidth);
		coordinates.destinationXPercentage = 0;
		coordinates.destinationYPercentage = (1 - coordinates.destinationHeightPercentage) * verticalPercentage;
	  }
	  else
	  {
		coordinates.destinationWidthPercentage = (naturalWidth / image.clientWidth) / (naturalHeight / image.clientHeight);
		coordinates.destinationHeightPercentage = 1;
		coordinates.destinationXPercentage = (1 - coordinates.destinationWidthPercentage) * horizontalPercentage;
		coordinates.destinationYPercentage = 0;
	  }
	}
	else if (imageObjectFit === "cover")
	{
	  if (naturalRatio > visibleRatio)
	  {
		coordinates.sourceWidth = naturalHeight * visibleRatio;
		coordinates.sourceHeight = naturalHeight;
		coordinates.sourceX = (naturalWidth - coordinates.sourceWidth) * horizontalPercentage;
		coordinates.sourceY = 0;
	  }
	  else
	  {
		coordinates.sourceWidth = naturalWidth;
		coordinates.sourceHeight = naturalWidth / visibleRatio;
		coordinates.sourceX = 0;
		coordinates.sourceY = (naturalHeight - coordinates.sourceHeight) * verticalPercentage;
	  }
	  coordinates.destinationWidthPercentage = 1;
	  coordinates.destinationHeightPercentage = 1;
	  coordinates.destinationXPercentage = 0;
	  coordinates.destinationYPercentage = 0;
	}
	else
	{
	  if (imageObjectFit !== "fill")
	  {
		console.error("unexpected 'object-fit' attribute with value '" + imageObjectFit + "' relative to");
	  }
	  coordinates.sourceWidth = naturalWidth;
	  coordinates.sourceHeight = naturalHeight;
	  coordinates.sourceX = 0;
	  coordinates.sourceY = 0;
	  coordinates.destinationWidthPercentage = 1;
	  coordinates.destinationHeightPercentage = 1;
	  coordinates.destinationXPercentage = 0;
	  coordinates.destinationYPercentage = 0;
	}
	return coordinates;
}

function manageMouseWheel(event, index){
	// Ignore events for 750 ms
	var currentTime = Date.now();
	
	if (currentTime > debounceWheel){
		if (event.deltaY > 0){
			zoomOut(index);
		}else{
			zoomIn(index);
		}
		debounceWheel = currentTime + 500;
	}
}

function zoomIn(index){
	if (index==0){
		if (teraConnected)
			SharedObject.zoomInClicked(localContact.uuid);
	}else{
		request = {"value":"in"};
		if (easyrtc.webSocketConnected) {
			easyrtc.sendDataWS(easyids[index], 'ZoomRequest', request, function (ackMesg) {
				//console.error("ackMsg:",ackMesg);
				if (ackMesg.msgType === 'error') {
					console.error(ackMesg.msgData.errorText);
				}
			});
		}
		
	}
	resetInactiveTimer();
}

function zoomOut(index){
	if (index==0){
		if (teraConnected)
			SharedObject.zoomOutClicked(localContact.uuid);
	}else{
		request = {"value":"out"};
		if (easyrtc.webSocketConnected) {
			easyrtc.sendDataWS(easyids[index], 'ZoomRequest', request, function (ackMesg) {
				//console.error("ackMsg:",ackMesg);
				if (ackMesg.msgType === 'error') {
					console.error(ackMesg.msgData.errorText);
				}
			});
		}
		
	}
	resetInactiveTimer();
}

function zoomMin(index){
	if (index==0){
		if (teraConnected)
			SharedObject.zoomMinClicked(localContact.uuid);
	}else{
		request = {"value":"min"};
		if (easyrtc.webSocketConnected) {
			easyrtc.sendDataWS(easyids[index], 'ZoomRequest', request, function (ackMesg) {
				//console.error("ackMsg:",ackMesg);
				if (ackMesg.msgType === 'error') {
					console.error(ackMesg.msgData.errorText);
				}
			});
		}
	}
}

function zoomMax(index){
	if (index==0){
		if (teraConnected)
			SharedObject.zoomMaxClicked(localContact.uuid);
	}else{
		request = {"value":"max"};
		if (easyrtc.webSocketConnected) {
			easyrtc.sendDataWS(easyids[index], 'ZoomRequest', request, function (ackMesg) {
				//console.error("ackMsg:",ackMesg);
				if (ackMesg.msgType === 'error') {
					console.error(ackMesg.msgData.errorText);
				}
			});
		}
	}
}

function gotoPreset(event, index, preset){
	console.log("gotoPreset: " + index + ", preset: " + preset + ", shift: " + event.shiftKey + ", ctrl: " + event.ctrlKey);
	if (index==0){
		if (teraConnected){
			if (event.shiftKey && event.ctrlKey)
				SharedObject.setPresetClicked(localContact.uuid, preset);
			else
				SharedObject.gotoPresetClicked(localContact.uuid, preset);
		}
	}else{
		var set = "false";
		if (event.shiftKey && event.ctrlKey)
			set = "true";
		request = {"preset":preset, "set":set};
		if (easyrtc.webSocketConnected) {
			easyrtc.sendDataWS(easyids[index], 'PresetRequest', request, function (ackMesg) {
				//console.error("ackMsg:",ackMesg);
				if (ackMesg.msgType === 'error') {
					console.error(ackMesg.msgData.errorText);
				}
			});
		}
		
	}
}

function camSettings(index){
	if (index==0){
		if (teraConnected)
			SharedObject.camSettingsClicked(uuids[index]);
	}else{
		request = "";
		if (easyrtc.webSocketConnected) {
			easyrtc.sendDataWS(easyids[index], 'CamSettingsRequest', request, function (ackMesg) {
				//console.error("ackMsg:",ackMesg);
				if (ackMesg.msgType === 'error') {
					console.error(ackMesg.msgData.errorText);
				}
			});
		}
		
	}
}

function forwardData(data)
{
    //Contact should be a JSON object
    console.log("Forwarding data : " + data);
    var settings = JSON.parse(data);
	
	if (settings.uuid != localContact.uuid){
		for (var i=0; i<5; i++){
			if (uuids[i] == settings.uuid){
				console.log("Forwarding to " + easyids[i]);
				if (easyrtc.webSocketConnected) {
					easyrtc.sendDataWS(easyids[i], 'DataForwarding', data, function (ackMesg) {
						//console.error("ackMsg:",ackMesg);
						if (ackMesg.msgType === 'error') {
							console.error(ackMesg.msgData.errorText);
						}
					});
				}
				break;
			}
		}
	}else{
		console.error("Wanted to forward settings to remote user, but received local user instead.");
	}
	
	
}

