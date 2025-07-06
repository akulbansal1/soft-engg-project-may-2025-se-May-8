import React, { useEffect, useRef, useState } from 'react';

const CameraInput: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [mirror, setMirror] = useState(false);
  const [bw, setBW] = useState(false);
  const [saturation, setSaturation] = useState(100); // 100%
  const [brightness, setBrightness] = useState(100); // 100%
  const [invert, setInvert] = useState(false);

  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    });

    const interval = setInterval(() => {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      if (!video || !canvas) return;

      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      if (mirror) {
        ctx.translate(canvas.width, 0);
        ctx.scale(-1, 1);
      }

      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      if (mirror) {
        ctx.setTransform(1, 0, 0, 1, 0, 0); // Reset transform
      }

      let imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      let data = imageData.data;
        if (invert) {
                for (let i = 0; i < data.length; i += 4) {
                    data[i]     = 255 - data[i];
                    data[i + 1] = 255 - data[i + 1];
                    data[i + 2] = 255 - data[i + 2];
                }
            }
      // Apply B&W filter or saturation + brightness
      for (let i = 0; i < data.length; i += 4) {
        let r = data[i], g = data[i + 1], b = data[i + 2];

        if (bw) {
          const gray = 0.3 * r + 0.59 * g + 0.11 * b;
          data[i] = data[i + 1] = data[i + 2] = gray;
        } else {
          // Saturation (simple linear adjustment)
          const avg = (r + g + b) / 3;
          data[i]     = avg + (r - avg) * (saturation / 100);
          data[i + 1] = avg + (g - avg) * (saturation / 100);
          data[i + 2] = avg + (b - avg) * (saturation / 100);
        }

        // Brightness
        data[i]     = Math.min(255, data[i] * (brightness / 100));
        data[i + 1] = Math.min(255, data[i + 1] * (brightness / 100));
        data[i + 2] = Math.min(255, data[i + 2] * (brightness / 100));
      }
      
      
      ctx.putImageData(imageData, 0, 0);
    }, 30); // ~30fps

    return () => clearInterval(interval);
  }, [mirror, bw, saturation, brightness]);

  return (
    <div className="flex flex-col items-center space-y-4 p-4">
      <canvas ref={canvasRef} className="rounded shadow max-w-full" />
      <video ref={videoRef} style={{ display: 'none' }} autoPlay playsInline />

      <div className="flex flex-wrap justify-center gap-4">
        <label>
          <input type="checkbox" checked={mirror} onChange={() => setMirror(!mirror)} />
          Mirror
        </label>

        <label>
          <input type="checkbox" checked={bw} onChange={() => setBW(!bw)} />
          B&W
        </label>

        <label>
            <input type="checkbox" checked={invert} onChange={() => setInvert(!invert)} />
            Inverse Colors
        </label>

        <label>
          Saturation:
          <input
            type="range"
            min="0"
            max="200"
            value={saturation}
            onChange={(e) => setSaturation(+e.target.value)}
          />
          {saturation}%
        </label>

        <label>
          Brightness:
          <input
            type="range"
            min="0"
            max="200"
            value={brightness}
            onChange={(e) => setBrightness(+e.target.value)}
          />
          {brightness}%
        </label>
      </div>
    </div>
  );
};

export default CameraInput;
