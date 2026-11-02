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

    const handleEscape = (event) => {
      if (event.key === "Escape") setOpen(false);
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  return (
    <div ref={wrapperRef} className="relative inline-block">
      <button
        type="button"
        aria-expanded={open}
        aria-haspopup="menu"
        onClick={() => setOpen((prev) => !prev)}
        className={className}
      >
        <span aria-hidden="true">↑</span> Upload
      </button>

      {open && (
        <div role="menu" className="absolute left-0 top-full z-20 mt-2 min-w-[190px] overflow-hidden rounded-xl border border-slate-200 bg-white p-1 shadow-xl shadow-slate-900/10 dark:border-slate-700 dark:bg-slate-900">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="block w-full rounded-lg px-3 py-2 text-left text-sm font-medium text-slate-700 transition hover:bg-indigo-50 hover:text-indigo-700 dark:text-slate-200 dark:hover:bg-indigo-500/10 dark:hover:text-indigo-300"
          >
            Upload Files
          </button>

          <button
            type="button"
            onClick={() => folderInputRef.current?.click()}
            className="mt-1 block w-full rounded-lg border-t border-slate-100 px-3 py-2 text-left text-sm font-medium text-slate-700 transition hover:bg-indigo-50 hover:text-indigo-700 dark:border-slate-800 dark:text-slate-200 dark:hover:bg-indigo-500/10 dark:hover:text-indigo-300"
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
