// Required packages:
// npm install react-easy-crop react-beautiful-dnd jspdf uuid

import React, { useRef, useState, useEffect } from 'react';
import Cropper from 'react-easy-crop';
import { jsPDF } from 'jspdf';
import { v4 as uuidv4 } from 'uuid';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';

interface ImageItem {
  id: string;
  dataUrl: string;
}

const DocScanner: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [images, setImages] = useState<ImageItem[]>([]);
  const [cropMode, setCropMode] = useState<string | null>(null);
  const [cropImage, setCropImage] = useState<string>('');
  const [croppedImageUrl, setCroppedImageUrl] = useState<string>('');
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [croppedAreaPixels, setCroppedAreaPixels] = useState<any>(null);

  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
      if (videoRef.current) videoRef.current.srcObject = stream;
    });
  }, []);

  const takePicture = () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video) return;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.drawImage(video, 0, 0);
    const dataUrl = canvas.toDataURL('image/jpeg');
    setImages([...images, { id: uuidv4(), dataUrl }]);
  };

  const deleteImage = (id: string) => {
    setImages(images.filter((img) => img.id !== id));
  };

  const onCropComplete = async (_: any, areaPixels: any) => {
    setCroppedAreaPixels(areaPixels);
  };

  const applyCrop = async () => {
    const image = new Image();
    image.src = cropImage;
    await new Promise((res) => (image.onload = res));
    const canvas = document.createElement('canvas');
    canvas.width = croppedAreaPixels.width;
    canvas.height = croppedAreaPixels.height;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.drawImage(
      image,
      croppedAreaPixels.x,
      croppedAreaPixels.y,
      croppedAreaPixels.width,
      croppedAreaPixels.height,
      0,
      0,
      croppedAreaPixels.width,
      croppedAreaPixels.height
    );
    const croppedUrl = canvas.toDataURL('image/jpeg');
    setImages((prev) =>
      prev.map((img) => (img.id === cropMode ? { id: img.id, dataUrl: croppedUrl } : img))
    );
    setCropMode(null);
  };

  const generatePDF = () => {
    const pdf = new jsPDF();
    images.forEach((img, i) => {
      if (i > 0) pdf.addPage();
      pdf.addImage(img.dataUrl, 'JPEG', 0, 0, 210, 297); // A4 size
    });
    pdf.save('document.pdf');
  };

  const onDragEnd = (result: any) => {
    if (!result.destination) return;
    const reordered = Array.from(images);
    const [moved] = reordered.splice(result.source.index, 1);
    reordered.splice(result.destination.index, 0, moved);
    setImages(reordered);
  };

  return (
    <div className="p-4 space-y-4">
      <div className="flex gap-4">
        <video ref={videoRef} autoPlay playsInline className="w-1/2 rounded shadow" />
        <button
          onClick={takePicture}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 h-10 self-start"
        >
          Take Picture
        </button>
      </div>
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      <DragDropContext onDragEnd={onDragEnd}>
        <Droppable droppableId="imageList" direction="horizontal">
          {(provided) => (
            <div
              className="flex gap-4 overflow-x-auto py-2"
              {...provided.droppableProps}
              ref={provided.innerRef}
            >
              {images.map((img, index) => (
                <Draggable draggableId={img.id} index={index} key={img.id}>
                  {(provided) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      {...provided.dragHandleProps}
                      className="relative"
                    >
                      <img src={img.dataUrl} alt="preview" className="w-40 h-auto rounded shadow" />
                      <div className="flex gap-1 absolute top-0 right-0">
                        <button onClick={() => setCropMode(img.id)} className="bg-yellow-400 px-2">✂️</button>
                        <button onClick={() => deleteImage(img.id)} className="bg-red-600 px-2 text-white">🗑️</button>
                      </div>
                    </div>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </DragDropContext>

      <button
        onClick={generatePDF}
        className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
      >
        Generate PDF
      </button>

      {cropMode && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
          <div className="bg-white p-4 rounded shadow-lg">
            <Cropper
              image={images.find((i) => i.id === cropMode)?.dataUrl || ''}
              crop={crop}
              zoom={zoom}
              //aspect={1}
              onCropChange={setCrop}
              onZoomChange={setZoom}
              onCropComplete={onCropComplete}
            />
            <div className="flex justify-end gap-2 mt-2">
              <button onClick={applyCrop} className="bg-blue-600 text-white px-4 py-1 rounded">Crop</button>
              <button onClick={() => setCropMode(null)} className="bg-gray-400 px-4 py-1 rounded">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocScanner;