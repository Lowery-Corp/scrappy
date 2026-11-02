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
      className={`relative overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm shadow-slate-900/5 transition-all dark:border-slate-800 dark:bg-slate-900 ${
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
            <div className="mb-2 text-2xl">⇧</div>
            <div className="text-sm font-semibold">Drop files to upload</div>
          </div>
        </div>
      )}

      {items.length === 0 ? (
        <div className="px-4 py-16 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-50 text-2xl text-indigo-600 dark:bg-indigo-500/10 dark:text-indigo-300">⌁</div>
          <h3 className="text-base font-semibold text-slate-900 dark:text-white">
            This folder is empty
          </h3>
          <p className="mx-auto mt-1 max-w-sm text-sm text-slate-500 dark:text-slate-400">
            Upload a document or create a folder to start organizing your workspace.
          </p>
        </div>
      ) : (
        <div>
          <div className="hidden grid-cols-[36px_minmax(0,1.8fr)_100px_100px_130px_130px_44px] items-center border-b border-slate-200 bg-slate-50 px-4 py-3 text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500 md:grid dark:border-slate-800 dark:bg-slate-950/50 dark:text-slate-400">
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
                className={`group grid grid-cols-[32px_minmax(0,1fr)_auto] grid-rows-[auto_auto] items-center gap-x-3 gap-y-1 px-4 py-3.5 transition md:grid-cols-[36px_minmax(0,1.8fr)_100px_100px_130px_130px_44px] md:grid-rows-1 md:gap-0 md:py-3 ${
                  isSelected
                    ? "bg-indigo-50/70 dark:bg-indigo-500/10"
                    : "bg-white hover:bg-slate-50 dark:bg-slate-900 dark:hover:bg-slate-800/70"
                } ${!isLast ? "border-b border-slate-100 dark:border-slate-800" : ""} ${
                  isLoading ? "opacity-70" : ""
                }`}
              >
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => onToggleSelection(item.id)}
                    onClick={(e) => e.stopPropagation()}
                    className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-800"
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
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-base dark:bg-slate-800">
                    {isFolder ? "▰" : getFileIcon(item.name)}
                  </div>

                  <div className="min-w-0">
                    <div className="truncate text-sm font-semibold text-slate-900 dark:text-white">
                      {item.name}
                    </div>
                    {isFolder && isLoading && (
                      <div className="mt-0.5 text-[11px] text-purple-600 dark:text-purple-400">
                        Loading...
                      </div>
                    )}
                  </div>
                </button>

                <div className="col-start-3 row-start-1 truncate text-right text-xs text-slate-500 md:col-auto md:row-auto md:pr-3 dark:text-slate-400">
                  {isFolder ? "—" : item.size}
                </div>

                <div className="col-start-2 row-start-2 pr-3 md:col-auto md:row-auto">
                  {isFolder ? (
                    <span className="text-xs text-slate-400 dark:text-slate-500">Folder</span>
                  ) : (
                    <span
                      className={`inline-flex max-w-full items-center rounded-full px-2 py-0.5 text-[11px] font-medium leading-5 ring-1 ring-inset ${getStatusBadgeClasses(item.status)}`}
                      title={formatStatus(item.status)}
                    >
                      <span className="truncate">{formatStatus(item.status)}</span>
                    </span>
                  )}
                </div>

                <div className="hidden truncate pr-3 text-xs text-slate-500 md:block dark:text-slate-400">
                  {item.createdAt}
                </div>

                <div className="hidden truncate pr-3 text-xs text-slate-500 md:block dark:text-slate-400">
                  {item.updatedAt ?? item.createdAt}
                </div>

                <div className="col-start-3 row-start-2 flex justify-end md:col-auto md:row-auto">
                  {!isFolder || !isLoading ? (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onStartRename(item);
                      }}
                      className="rounded-lg p-1.5 text-slate-400 transition hover:bg-slate-100 hover:text-indigo-600 md:opacity-0 md:group-hover:opacity-100 dark:hover:bg-slate-800"
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
