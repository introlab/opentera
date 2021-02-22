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
    constructor(filename = undefined){
        this.recorder = null;
        this.filename = filename;
    }

    startRecording(){
        this.addVideoToRecorder(getActiveStreams());
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
        this.recorder.getInternalRecorder().resetVideoStreams(getActiveStreams());
    }

    stopRecording(){
        if (!this.recorder) return;
        let self = this;
        this.recorder.stopRecording(function() {
            getSeekableBlob(self.recorder.getBlob(), function(seekableBlob) {

                //console.log(url);
                if (self.filename === undefined) {
                    //let url = URL.createObjectURL(seekableBlob);
                    //window.open(url);
                    invokeSaveAsDialog(seekableBlob);
                }else{
                    let file = new File([seekableBlob], self.filename);

                    let url = URL.createObjectURL(file);
                    window.open(url);
                }

                self.recorder = null;
            });
        });
    }
}



