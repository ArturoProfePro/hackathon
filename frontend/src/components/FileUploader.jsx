import { useState } from 'react';

export const FileUploader = ({ onUpload }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (!file) return;

    await onUpload(file, setProgress);
  };

  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    await onUpload(file, setProgress);
  };

  return (
    <div className="mt-5">
      <div
        className={`border-2 h-full flex-row items-center relative justify-center w-full border-dashed p-6 rounded-xl text-center transition-all ${
          isDragging ? 'bg-blue-100 border-blue-500' : 'bg-[rgb(48,48,48)]'
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
      >
        <p className="text-white">Перетащи PDF сюда или нажми, чтобы выбрать</p>

        <input
          type="file"
          accept="application/pdf"
          onChange={handleFileSelect}
          className="opacity-0 absolute top-0 inset-0 cursor-pointer"
        />
      </div>

      {progress > 0 && progress < 100 && (
        <div className="mt-4">
          <p className="text-sm text-gray-700 mb-1">Загружается: {progress}%</p>
          <div className="w-full bg-gray-300 h-3 rounded-xl overflow-hidden">
            <div
              style={{ width: `${progress}%` }}
              className="h-full bg-blue-600 transition-all"
            ></div>
          </div>
        </div>
      )}
    </div>
  );
};
