import { useState } from "react";

export default function FileDisplay({
  folders,
  files,
  selectedItems,
  onToggleSelection,
  onDoubleClickFolder,
  onStartRename,
  isDragOver,
  onDrop,
  onDragOver,
  onDragLeave,
}) {
  const [loadingFolderId, setLoadingFolderId] = useState(null);

  const getFileIcon = (fileName) => {
    const ext = fileName.split(".").pop()?.toLowerCase();

    switch (ext) {
      case "pdf":
        return "📄";
      case "doc":
      case "docx":
        return "📝";
      case "xls":
      case "xlsx":
        return "📊";
      case "ppt":
      case "pptx":
        return "📈";
      case "jpg":
      case "jpeg":
      case "png":
      case "gif":
        return "🖼️";
      case "mp4":
      case "avi":
      case "mov":
        return "🎬";
      case "mp3":
      case "wav":
        return "🎵";
      case "zip":
      case "rar":
        return "📦";
      default:
        return "📄";
    }
  };

  const getStatusBadgeClasses = (status) => {
    switch (String(status || "").toLowerCase()) {
      case "uploaded":
        return "bg-blue-50 text-blue-700 ring-blue-600/20 dark:bg-blue-400/10 dark:text-blue-300 dark:ring-blue-400/30";
      case "processing":
        return "bg-amber-50 text-amber-700 ring-amber-600/20 dark:bg-amber-400/10 dark:text-amber-300 dark:ring-amber-400/30";
      case "ready":
        return "bg-emerald-50 text-emerald-700 ring-emerald-600/20 dark:bg-emerald-400/10 dark:text-emerald-300 dark:ring-emerald-400/30";
      case "error":
        return "bg-rose-50 text-rose-700 ring-rose-600/20 dark:bg-rose-400/10 dark:text-rose-300 dark:ring-rose-400/30";
      default:
        return "bg-gray-100 text-gray-700 ring-gray-500/20 dark:bg-gray-700 dark:text-gray-300 dark:ring-gray-500/30";
    }
  };

  const formatStatus = (status) => {
    const normalizedStatus = String(status || "unknown").toLowerCase();
    return normalizedStatus.charAt(0).toUpperCase() + normalizedStatus.slice(1);
  };

  const handleFolderClick = async (folder) => {
    try {
      setLoadingFolderId(folder.id);
      await Promise.resolve(onDoubleClickFolder(folder.path + "/"));
    } finally {
      setLoadingFolderId(null);
    }
  };

  const items = [
    ...folders.map((folder) => ({ ...folder, itemType: "folder" })),
    ...files.map((file) => ({ ...file, itemType: "file" })),
  ];

  return (
    <div
      className={`relative overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm transition-all dark:border-gray-700 dark:bg-gray-800 ${
        isDragOver
          ? "ring-2 ring-purple-500 bg-purple-50 dark:bg-purple-900/10"
          : ""
      }`}
      onDrop={onDrop}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
    >
      {isDragOver && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-purple-500/10 backdrop-blur-[1px]">
          <div className="text-center text-purple-600 dark:text-purple-400">
            <div className="mb-1 text-2xl">📤</div>
            <div className="text-sm font-medium">Drop files to upload</div>
          </div>
        </div>
      )}

      {items.length === 0 ? (
        <div className="px-4 py-10 text-center">
          <div className="mb-2 text-3xl">📁</div>
          <h3 className="text-base font-semibold text-gray-900 dark:text-white">
            No files or folders
          </h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Upload files or create a folder to get started
          </p>
        </div>
      ) : (
        <div>
          <div className="grid grid-cols-[36px_minmax(0,1.8fr)_100px_100px_130px_130px_44px] items-center border-b border-gray-200 bg-gray-50 px-3 py-2 text-[11px] font-semibold uppercase tracking-wide text-gray-500 dark:border-gray-700 dark:bg-gray-900/40 dark:text-gray-400">
            <div />
            <div>Name</div>
            <div>Size</div>
            <div>Status</div>
            <div>Created</div>
            <div>Updated</div>
            <div />
          </div>

          {items.map((item, index) => {
            const isLast = index === items.length - 1;
            const isFolder = item.itemType === "folder";
            const isLoading = isFolder && loadingFolderId === item.id;
            const isSelected = selectedItems.includes(item.id);

            return (
              <div
                key={item.id}
                className={`group grid grid-cols-[36px_minmax(0,1.8fr)_100px_100px_130px_130px_44px] items-center gap-0 px-3 py-2 ${
                  isSelected
                    ? "bg-purple-50 dark:bg-purple-900/20"
                    : "bg-white hover:bg-gray-50 dark:bg-gray-800 dark:hover:bg-gray-700/40"
                } ${!isLast ? "border-b border-gray-200 dark:border-gray-700" : ""} ${
                  isLoading ? "opacity-70" : ""
                }`}
              >
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => onToggleSelection(item.id)}
                    onClick={(e) => e.stopPropagation()}
                    className="h-4 w-4 rounded border-gray-300 text-purple-600 focus:ring-purple-500 dark:border-gray-600 dark:bg-gray-700"
                    aria-label={`Select ${item.name}`}
                  />
                </div>

                <button
                  type="button"
                  onClick={() => {
                    if (isFolder) {
                      handleFolderClick(item);
                    }
                  }}
                  className={`flex min-w-0 items-center gap-3 text-left ${
                    isFolder ? "cursor-pointer" : "cursor-default"
                  }`}
                >
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-gray-100 text-base dark:bg-gray-700">
                    {isFolder ? "📁" : getFileIcon(item.name)}
                  </div>

                  <div className="min-w-0">
                    <div className="truncate text-sm font-medium text-gray-900 dark:text-white">
                      {item.name}
                    </div>
                    {isFolder && isLoading && (
                      <div className="mt-0.5 text-[11px] text-purple-600 dark:text-purple-400">
                        Loading...
                      </div>
                    )}
                  </div>
                </button>

                <div className="truncate pr-3 text-xs text-gray-500 dark:text-gray-400">
                  {isFolder ? "—" : item.size}
                </div>

                <div className="pr-3">
                  {isFolder ? (
                    <span className="text-xs text-gray-500 dark:text-gray-400">—</span>
                  ) : (
                    <span
                      className={`inline-flex max-w-full items-center rounded-full px-2 py-0.5 text-[11px] font-medium leading-5 ring-1 ring-inset ${getStatusBadgeClasses(item.status)}`}
                      title={formatStatus(item.status)}
                    >
                      <span className="truncate">{formatStatus(item.status)}</span>
                    </span>
                  )}
                </div>

                <div className="truncate pr-3 text-xs text-gray-500 dark:text-gray-400">
                  {item.createdAt}
                </div>

                <div className="truncate pr-3 text-xs text-gray-500 dark:text-gray-400">
                  {item.updatedAt ?? item.createdAt}
                </div>

                <div className="flex justify-end">
                  {!isFolder || !isLoading ? (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onStartRename(item);
                      }}
                      className="rounded-md p-1 text-gray-400 opacity-0 transition hover:bg-gray-100 hover:text-purple-600 group-hover:opacity-100 dark:hover:bg-gray-700"
                      aria-label={`Rename ${item.name}`}
                    >
                      ✏️
                    </button>
                  ) : null}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}