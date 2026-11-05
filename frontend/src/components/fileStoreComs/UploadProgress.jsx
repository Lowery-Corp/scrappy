export default function UploadProgress({ uploadProgress, fileUploadCounter }) {
  if (Object.keys(uploadProgress).length === 0) return null;

  return (
    <div className="mb-5 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <h3 className="mb-3 text-sm font-semibold text-slate-900 dark:text-white">
        Uploading Files... {fileUploadCounter !== null ? `(${fileUploadCounter} remaining)` : ""}
      </h3>
      {Object.entries(uploadProgress).map(([fileId, progress]) => (
        <div key={fileId} className="mb-2">
          <div className="mb-1 flex justify-between text-xs font-medium text-slate-500 dark:text-slate-400">
            <span>Uploading...</span>
            <span>{progress}%</span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
            <div
              className="h-2 rounded-full bg-indigo-600 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
