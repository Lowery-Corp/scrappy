import UploadFileButton from "./UploadFileButton";
import SyncBlogButton from "./SyncBlobButton";
import NewFolderButton from "./NewFolderButton";

export default function FileStoreHeader({
  onNewFolder,
  onSync,
  onFileUpload,
  hasOnlyOneFolderSelected,
  onOpenFolder,
  selectedItems,
  onDeleteSelected,
  currentPath,
  onPathChange,
  searchQuery,
  onSearchChange,
}) {
  const pathSegments = currentPath.split("/").filter(Boolean);

  return (
    <div className="mb-4 rounded-xl border border-gray-200 bg-white px-4 py-3 shadow-sm dark:border-gray-700 dark:bg-gray-800">
      <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
        <div className="min-w-0">
          <h1 className="text-xl font-semibold tracking-tight text-gray-900 dark:text-white">
            File Store
          </h1>

          <div className="mt-1 flex flex-wrap items-center gap-1 text-sm text-gray-500 dark:text-gray-400">
            <button
              onClick={() => onPathChange("/")}
              className="rounded-md px-1.5 py-0.5 transition hover:bg-gray-100 hover:text-purple-600 dark:hover:bg-gray-700 dark:hover:text-purple-400"
            >
              Home
            </button>

            {pathSegments.map((segment, index) => {
              const targetPath =
                "/" + pathSegments.slice(0, index + 1).join("/") + "/";

              return (
                <div key={index} className="flex min-w-0 items-center gap-1">
                  <span className="text-gray-400">/</span>
                  <button
                    onClick={() => onPathChange(targetPath)}
                    className="truncate rounded-md px-1.5 py-0.5 transition hover:bg-gray-100 hover:text-purple-600 dark:hover:bg-gray-700 dark:hover:text-purple-400"
                    title={segment}
                  >
                    {segment}
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        <div className="flex flex-col gap-2 lg:flex-row lg:items-center">
          <div className="relative w-full lg:w-72">
            <span className="pointer-events-none absolute inset-y-0 left-3 flex items-center text-sm text-gray-400 dark:text-gray-500">
              🔍
            </span>

            <input
              type="text"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Search files"
              className="
                h-9 w-full rounded-lg border border-gray-300 bg-white pl-9 pr-3
                text-sm text-gray-900 caret-gray-900
                placeholder:text-gray-400
                outline-none transition
                focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20
                dark:border-gray-600 dark:bg-gray-800
                dark:text-gray-100 dark:caret-gray-100
                dark:placeholder:text-gray-400
              "
            />
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <NewFolderButton
              onNewFolder={onNewFolder}
              className="inline-flex h-9 items-center rounded-lg bg-purple-600 px-3 text-sm font-medium text-white transition hover:bg-purple-700"
            />

            <SyncBlogButton
              onSync={onSync}
              className="inline-flex h-9 items-center rounded-lg bg-green-600 px-3 text-sm font-medium text-white transition hover:bg-green-700"
            />

            <UploadFileButton
              onFileUpload={onFileUpload}
              className="inline-flex h-9 cursor-pointer items-center rounded-lg bg-indigo-600 px-3 text-sm font-medium text-white transition hover:bg-indigo-700"
            />

            {hasOnlyOneFolderSelected && (
              <button
                onClick={onOpenFolder}
                className="inline-flex h-9 items-center rounded-lg bg-gray-900 px-3 text-sm font-medium text-white transition hover:bg-black dark:bg-gray-700 dark:hover:bg-gray-600"
              >
                Open
              </button>
            )}

            {selectedItems.length > 0 && (
              <button
                onClick={onDeleteSelected}
                className="inline-flex h-9 items-center rounded-lg bg-red-600 px-3 text-sm font-medium text-white transition hover:bg-red-700"
              >
                Delete
                <span className="ml-2 rounded-full bg-white/20 px-2 py-0.5 text-xs">
                  {selectedItems.length}
                </span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}