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
    <div className="mb-5 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm shadow-slate-900/5 dark:border-slate-800 dark:bg-slate-900 sm:p-5">
      <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-indigo-600 dark:text-indigo-300">
            Workspace
          </p>
          <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-950 dark:text-white">
            File store
          </h1>

          <div className="mt-1 flex flex-wrap items-center gap-1 text-sm text-gray-500 dark:text-gray-400">
            <button
              onClick={() => onPathChange("/")}
            className="rounded-md px-1.5 py-0.5 font-medium transition hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-800 dark:hover:text-indigo-300"
            >
              Home
            </button>

            {pathSegments.map((segment, index) => {
              const targetPath =
                "/" + pathSegments.slice(0, index + 1).join("/") + "/";

              return (
                <div key={index} className="flex min-w-0 items-center gap-1">
                  <span className="text-slate-300 dark:text-slate-600">/</span>
                  <button
                    onClick={() => onPathChange(targetPath)}
                    className="truncate rounded-md px-1.5 py-0.5 font-medium transition hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-800 dark:hover:text-indigo-300"
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
              <span aria-hidden="true">⌕</span>
            </span>

            <input
              type="text"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Search files"
              className="
                h-10 w-full rounded-xl border border-slate-200 bg-slate-50 pl-9 pr-3
                text-sm text-slate-900 caret-slate-900
                placeholder:text-gray-400
                outline-none transition
                focus:border-indigo-500 focus:bg-white focus:ring-4 focus:ring-indigo-500/10
                dark:border-slate-700 dark:bg-slate-800
                dark:text-slate-100 dark:caret-slate-100
                dark:placeholder:text-gray-400
              "
            />
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <NewFolderButton
              onNewFolder={onNewFolder}
              className="inline-flex h-10 items-center rounded-xl bg-indigo-600 px-3.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700"
            />

            <SyncBlogButton
              onSync={onSync}
              className="inline-flex h-10 items-center rounded-xl border border-slate-200 bg-white px-3.5 text-sm font-semibold text-slate-700 transition hover:border-indigo-200 hover:bg-indigo-50 hover:text-indigo-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:border-indigo-500/50 dark:hover:bg-indigo-500/10 dark:hover:text-indigo-300"
            />

            <UploadFileButton
              onFileUpload={onFileUpload}
              className="inline-flex h-10 cursor-pointer items-center rounded-xl bg-slate-900 px-3.5 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-700 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-200"
            />

            {hasOnlyOneFolderSelected && (
              <button
                onClick={onOpenFolder}
                className="inline-flex h-10 items-center rounded-xl border border-slate-200 bg-white px-3.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
              >
                Open
              </button>
            )}

            {selectedItems.length > 0 && (
              <button
                onClick={onDeleteSelected}
                className="inline-flex h-10 items-center rounded-xl bg-rose-600 px-3.5 text-sm font-semibold text-white transition hover:bg-rose-700"
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
