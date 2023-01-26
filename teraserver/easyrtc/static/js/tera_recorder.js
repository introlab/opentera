const recorder_config = {
    // audio, video, canvas, gif
    type: 'video',

    // audio/webm
    // audio/webm;codecs=pcm
    // video/mp4
    // video/webm;codecs=vp9
    // video/webm;codecs=vp8
    // video/webm;codecs=h264
    // video/x-matroska;codecs=avc1
    // video/mpeg -- NOT supported by any browser, yet
    // audio/wav
    // audio/ogg  -- ONLY Firefox
    // demo: simple-demos/isTypeSupported.html
    // mimeType: 'video/webm;codecs=vp8',

    // MediaStreamRecorder, StereoAudioRecorder, WebAssemblyRecorder
    // CanvasRecorder, GifRecorder, WhammyRecorder
    recorderType: MultiStreamRecorder,

    // disable logs
    disableLogs: true,

    // get intervals based blobs
    // value in milliseconds
    timeSlice: 5000,

    // requires timeSlice above
    // returns blob via callback function
    ondataavailable: function(blob) {

        //console.log(URL.createObjectURL(blob));
        //console.log("Saving blob...");
        if (streamRecorder){
            streamRecorder.addDataToTempFile(blob);
        }
        //RecordRTC.writeToDisk({video: blob});
        /*streamRecorder.recorder.clearRecordedData();*/
    },

    discardBlobs: true, // Don't keep blobs in memory!


    // used by MultiStreamRecorder - to access HTMLCanvasElement
    elementClass: 'multi-streams-mixer',

    video: {
        width: 1280,
        height: 720
    }
};

let streamRecorder = null;

class TeraVideoRecorder
{
    constructor(){
        this.recorder = null;
        this.fileWriter = null;
        this.paused = false;
    }

    startRecording(){
        console.log("Starting local recording...");

        // Creating temporary video save file
        let self = this;
        window.webkitRequestFileSystem(TEMPORARY, 0, function (filesystem) {
            filesystem.root.getFile("temp.webm", {create: true}, function(fileEntry) {
                fileEntry.remove(function() {
                    filesystem.root.getFile("temp.webm", {create: true}, function(fileEntry) {
                        fileEntry.createWriter(function(fileWriter) {
                            self.fileWriter = fileWriter;
                            self.fileWriter.onwriteend = function(e) {
                                //console.log("Temp file written!");
                            };
                            self.fileWriter.onerror = self.errorHandler;
                        }, self.errorHandler);
                    }, self.errorHandler);
                }, self.errorHandler);
            }, self.errorHandler);
        }, {});

        this.paused = false;

        let streams = getActiveStreams();
        let stream;
        for (stream of streams)
            this.addVideoToRecorder([stream]);
    }

    errorHandler(e) {
        console.log(e)
    }

    addDataToTempFile(blob){
        if (this.fileWriter === null)
            return;
        this.fileWriter.write(blob);
        /*let self = this;
        getSeekableBlob(blob, function(seekableBlob) {
            self.fileWriter.write(seekableBlob);
        });*/
    }

    addVideoToRecorder(stream) {
        if (!this.recorder) {
            this.recorder = new MultiStreamRecorder(stream, recorder_config);//RecordRTC(stream, recorder_config);
            //this.recorder.startRecording();
            this.recorder.record();
        } else {
            //this.recorder.getInternalRecorder().addStreams(stream);
            this.recorder.addStreams(stream);
        }
    }

    refreshVideosInRecorder(){
        let streams = getActiveStreams();
        //this.recorder.getInternalRecorder().resetVideoStreams(streams);
        this.recorder.resetVideoStreams(streams);
    }

    pauseRecording(){
        if (this.paused){
            this.recorder.resume();
            this.paused = false;
        }else{
            this.recorder.pause();
            this.paused = true;
        }
    }

    stopRecording(){
        if (!this.recorder)
            return;

        this.paused = false;

        console.log("Stopping local recording.");

        let self = this;
        //this.recorder.stopRecording(function() {
        this.fileWriter = null;

        this.recorder.stop(function() {
            /*getSeekableBlob(self.recorder.getBlob(), function(seekableBlob) {
                //console.log(url);
                self.recorder = null;
                invokeSaveAsDialog(seekableBlob);
            });*/
            window.webkitRequestFileSystem(TEMPORARY, 0, function (filesystem) {
                filesystem.root.getFile("temp.webm", {create: true}, function(fileEntry) {
                        fileEntry.file(function (fileReader){
                            console.log(fileReader);
                            if (fileReader.size > 0){
                                getSeekableBlob(fileReader, function(seekableBlob) {
                                    invokeSaveAsDialog(seekableBlob);
                                    self.recorder.clearRecordedData();
                                    self.recorder = null;
                                    fileEntry.remove({},{});
                                });
                            }else{
                                invokeSaveAsDialog(fileReader);
                                self.recorder.clearRecordedData();
                                self.recorder = null;
                                fileEntry.remove({},{});
                            }

                        }, self.errorHandler);

                    }, self.errorHandler);
            }, {});



            });

        //});
    }
}



