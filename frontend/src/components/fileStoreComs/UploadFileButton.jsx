import React, { useEffect, useRef, useState } from "react";

export default function UploadFileButton({ onFileUpload, className = "" }) {
  const [open, setOpen] = useState(false);
  const wrapperRef = useRef(null);
  const fileInputRef = useRef(null);
  const folderInputRef = useRef(null);

  const handleFiles = (event) => {
    const fileList = event.target.files;
    if (!fileList || fileList.length === 0) return;
    onFileUpload(Array.from(fileList));
    event.target.value = "";
    setOpen(false);
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!wrapperRef.current?.contains(event.target)) {
        setOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div ref={wrapperRef} className="relative inline-block">
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className={className}
      >
        📤 Upload
      </button>

      {open && (
        <div className="absolute left-0 top-full z-20 mt-2 min-w-[180px] overflow-hidden rounded-lg border border-indigo-200 bg-white shadow-lg">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="block w-full px-3 py-2 text-left text-sm font-medium text-slate-700 transition hover:bg-indigo-50 hover:text-indigo-700"
          >
            Upload Files
          </button>

          <button
            type="button"
            onClick={() => folderInputRef.current?.click()}
            className="block w-full border-t border-indigo-100 px-3 py-2 text-left text-sm font-medium text-slate-700 transition hover:bg-indigo-50 hover:text-indigo-700"
          >
            Upload Folder
          </button>
        </div>
      )}

      <input
        ref={fileInputRef}
        type="file"
        multiple
        className="hidden"
        onChange={handleFiles}
      />

      <input
        ref={folderInputRef}
        type="file"
        multiple
        webkitdirectory=""
        className="hidden"
        onChange={handleFiles}
      />
    </div>
  );
}