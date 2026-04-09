export default function UploadProgress({ uploadProgress }) {
  if (Object.keys(uploadProgress).length === 0) return null;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
        Uploading Files...
      </h3>
      {Object.entries(uploadProgress).map(([fileId, progress]) => (
        <div key={fileId} className="mb-2">
          <div className="flex justify-between text-sm text-gray-600 dark:text-gray-300 mb-1">
            <span>Uploading...</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-purple-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}