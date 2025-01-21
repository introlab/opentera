let unblurredTrack = undefined;

// Blur local video. Only first local stream is supported for now.
function blur(enable = true, refresh_stream = false) {
    if ( (enable && unblurredTrack !== undefined) || (!enable && unblurredTrack === undefined)) {
        //console.error("Blur: Can't unblur or blur a stream that's already blurred or unblurred.")
        return;
    }

    let videoTrack = localStreams[0].stream.getVideoTracks()[0];
    const canvas = new OffscreenCanvas(localStreams[0].stream.getVideoTracks()[0].getSettings().width,
        localStreams[0].stream.getVideoTracks()[0].getSettings().height);
    const ctx = canvas.getContext("2d");

    if (!enable){
        videoTrack.stop();
        localStreams[0].stream.removeTrack(videoTrack);
        localStreams[0].stream.addTrack(unblurredTrack);
        unblurredTrack = undefined;
    }else{
        const selfieSegmentation = new SelfieSegmentation({
            locateFile: (file) =>
                `https://cdn.jsdelivr.net/npm/@mediapipe/selfie_segmentation/${file}`,
        });

        selfieSegmentation.setOptions({
            modelSelection: 0
        });

        selfieSegmentation.onResults(function(results){
            ctx.save();
            ctx.clearRect(
                0,
                0,
                canvas.width,
                canvas.height
            );
            ctx.drawImage(
                results.segmentationMask,
                0,
                0,
                canvas.width,
                canvas.height
            );

            ctx.globalCompositeOperation = "source-in";
            ctx.drawImage(
                results.image,
                0,
                0,
                canvas.width,
                canvas.height
            );

            // Only overwrite missing pixels.
            ctx.globalCompositeOperation = "destination-atop";
            ctx.filter = `blur(10px)`;
            ctx.drawImage(
                results.image,
                0,
                0,
                canvas.width,
                canvas.height
            );
            ctx.restore();
        });

        const trackProcessor = new MediaStreamTrackProcessor({ track: videoTrack });
        const trackGenerator = new MediaStreamTrackGenerator({ kind: 'video' });

        const transformer = new TransformStream({
            async transform(videoFrame, controller) {
                videoFrame.width = videoFrame.displayWidth;
                videoFrame.height = videoFrame.displayHeight;
                await selfieSegmentation.send({ image: videoFrame });

                const timestamp = videoFrame.timestamp;
                const newFrame = new VideoFrame(canvas, {timestamp});

                videoFrame.close();
                controller.enqueue(newFrame);
            }
        });

        trackProcessor.readable.pipeThrough(transformer).pipeTo(trackGenerator.writable);

        let processedStream = localStreams[0].stream;
        unblurredTrack = videoTrack;
        processedStream.removeTrack(unblurredTrack);
        processedStream.addTrack(trackGenerator);
    }
    if (refresh_stream)
        localVideoStreamSuccess(localStreams[0].stream);
}
