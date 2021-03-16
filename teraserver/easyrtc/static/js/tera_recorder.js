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
    }

    startRecording(){
        console.log("Starting local recording...");
        let streams = getActiveStreams();
        let stream;
        for (stream of streams)
            this.addVideoToRecorder([stream]);
    }

    addVideoToRecorder(stream) {
        if (!this.recorder) {
            this.recorder = new RecordRTC(stream, recorder_config);
            this.recorder.startRecording();
        } else {
            this.recorder.getInternalRecorder().addStreams(stream);
        }
    }

    refreshVideosInRecorder(){
        let streams = getActiveStreams();
        this.recorder.getInternalRecorder().resetVideoStreams(streams);
    }

    stopRecording(){
        if (!this.recorder)
            return;

        console.log("Stopping local recording.");
        let self = this;
        this.recorder.stopRecording(function() {
            getSeekableBlob(self.recorder.getBlob(), function(seekableBlob) {
                //console.log(url);
                self.recorder = null;
                invokeSaveAsDialog(seekableBlob);
            });
        });
    }
}



