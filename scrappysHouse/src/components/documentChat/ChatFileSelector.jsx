import { useCallback, useMemo, useState } from "react";

export default function ChatFileSelector({
  selectedChatId,
  userFiles,
  selectedFileIds,
  onFileSelect,
}) {
  const [searchQuery, setSearchQuery] = useState("");

  const getFileName = useCallback((file) => {
    return file.name || String(file.storage_key).split("/").pop() || "Untitled File";
  }, []);

  const removeNonePdfFiles = useCallback(
    (files) => {
      return files.filter((file) => {
        const fileName = getFileName(file);
        const fileExtension = fileName.split(".").pop().toLowerCase();
        return fileExtension === "pdf";
      });
    },
    [getFileName],
  );

  const sortFilesByName = useCallback((files) => {
    return [...files].sort((a, b) => {
      const nameA = (a.name || "").toLowerCase();
      const nameB = (b.name || "").toLowerCase();

      if (nameA < nameB) return -1;
      if (nameA > nameB) return 1;

      return 0;
    });
  }, []);

  const selectedFiles = useMemo(() => {
    const parsedSelectedFiles = userFiles.filter((file) =>
      selectedFileIds.includes(file.file_id),
    );

    const selectedFilesWithNames = parsedSelectedFiles.map((file) => ({
      ...file,
      name: getFileName(file),
    }));

    const filteredPdfFiles = removeNonePdfFiles(selectedFilesWithNames);

    return sortFilesByName(filteredPdfFiles);
  }, [getFileName, removeNonePdfFiles, selectedFileIds, sortFilesByName, userFiles]);

  const files = useMemo(() => {
    const notSelectedFiles = userFiles.filter(
      (file) => !selectedFileIds.includes(file.file_id),
    );

    const filesWithNames = notSelectedFiles.map((file) => ({
      ...file,
      name: getFileName(file),
    }));

    const filteredPdfFiles = removeNonePdfFiles(filesWithNames);

    return sortFilesByName(filteredPdfFiles);
  }, [getFileName, removeNonePdfFiles, selectedFileIds, sortFilesByName, userFiles]);

  const normalizedSearchQuery = searchQuery.trim().toLowerCase();

  const filteredSelectedFiles = selectedFiles.filter((file) =>
    file.name.toLowerCase().includes(normalizedSearchQuery),
  );

  const filteredFiles = files.filter((file) =>
    file.name.toLowerCase().includes(normalizedSearchQuery),
  );

  return (
    <aside className="flex w-full flex-col overflow-hidden rounded-xl border border-gray-200 bg-white/95 shadow-lg dark:border-gray-700 dark:bg-gray-800/95 lg:h-[calc(100vh-4rem)] lg:w-72 lg:shrink-0 lg:rounded-none lg:border-y-0 lg:border-r-0 lg:shadow-none xl:w-80">
      <div className="shrink-0 border-b border-gray-200 p-3 text-left dark:border-gray-700">
        <div className="flex items-center justify-between gap-2">
          <h2 className="m-0 text-base font-medium text-gray-900 dark:text-white">
            Your Files
          </h2>

          <button
            type="button"
            className="w-full rounded-md border border-purple-200 bg-purple-50 px-2.5 py-1.5 text-xs font-medium text-purple-700 transition-colors hover:bg-purple-100 dark:border-purple-800 dark:bg-purple-950/40 dark:text-purple-200 dark:hover:bg-purple-900/50 md:w-auto"
          >
            Upload
          </button>
        </div>

        <label className="mt-3 block">
          <span className="sr-only">Search Files</span>
          <input
            type="search"
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
            placeholder="Search files..."
            className="h-9 w-full rounded-md border border-gray-300 bg-white px-2.5 text-sm text-gray-900 outline-none transition-colors placeholder:text-gray-400 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 dark:border-gray-600 dark:bg-gray-900 dark:text-gray-100 dark:focus:ring-purple-900"
          />
        </label>
      </div>

      <div className="max-h-[28%] shrink-0 overflow-hidden border-b border-gray-200 px-3 py-2 text-left dark:border-gray-700">
        { selectedChatId ?
          <>
            <h2 className="m-0 px-2 text-xs font-normal tracking-wide text-gray-500 dark:text-gray-400">
              Selected Files
            </h2>
            <div className="mt-1.5 max-h-[calc(100%-1.25rem)] overflow-y-auto pr-1">
              {filteredSelectedFiles.length > 0 ? (
                <div className="space-y-1">
                  {filteredSelectedFiles.map((file) => {
                    const fileId = file.file_id;
                    const fileName = file.name;
                    const isSelected = false;
                    const isActive = false;
                    const updatedAt = "2 days ago";

                    return (
                      <div
                        key={fileId}
                        className={`group min-w-56 rounded-md border px-2 py-1 text-left transition-colors lg:min-w-0 ${
                          isActive
                            ? "border-purple-300 bg-purple-50 dark:border-purple-700 dark:bg-purple-950/40"
                            : "border-transparent bg-transparent hover:bg-gray-50 dark:hover:bg-gray-700/60"
                        } ${isSelected ? "ring-1 ring-red-400 dark:ring-red-500" : ""}`}
                      >
                        <button
                          type="button"
                          onClick={() => onFileSelect(fileId)}
                          className="w-full min-w-0 text-left"
                        >
                          <div className="flex items-center justify-between gap-2">
                            <p className="m-0 min-w-0 overflow-hidden text-ellipsis whitespace-nowrap text-xs font-normal text-gray-800 dark:text-gray-100">
                              {fileName}
                            </p>

                            <span className="hidden shrink-0 text-xs font-normal text-gray-400 dark:text-gray-500 xl:inline">
                              {updatedAt}
                            </span>
                          </div>
                        </button>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-xs font-normal text-gray-400 dark:text-gray-500">
                  {searchQuery
                    ? "No selected files match your search"
                    : "No files selected"}
                </p>
              )}
            </div>
          </>
        : <p className="text-xs font-normal text-gray-400 dark:text-gray-500">
            Select files to attach to your new chat.
          </p>
        }
      </div>

      <div className="flex min-h-0 flex-1 flex-col overflow-hidden p-2">
        <h2 className="m-0 shrink-0 px-2 text-xs font-normal tracking-wide text-gray-500 dark:text-gray-400">
          All Files
        </h2>

        <div className="mt-1.5 min-h-0 flex-1 overflow-y-auto pr-1">
          {filteredFiles.length > 0 ? (
            <div className="flex gap-1 lg:flex-col">
              {filteredFiles.map((file) => {
                const fileId = file.file_id;
                const fileName = file.name;
                const isSelected = false;
                const isActive = false;
                const updatedAt = "2 days ago";

                return (
                  <div
                    key={fileId}
                    className={`group min-w-56 rounded-md border px-2 py-1 text-left transition-colors lg:min-w-0 ${
                      isActive
                        ? "border-purple-300 bg-purple-50 dark:border-purple-700 dark:bg-purple-950/40"
                        : "border-transparent bg-transparent hover:bg-gray-50 dark:hover:bg-gray-700/60"
                    } ${isSelected ? "ring-1 ring-red-400 dark:ring-red-500" : ""}`}
                  >
                    <button
                      type="button"
                      onClick={() => onFileSelect(fileId)}
                      className="w-full min-w-0 text-left"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <p className="m-0 min-w-0 overflow-hidden text-ellipsis whitespace-nowrap text-xs font-normal text-gray-800 dark:text-gray-100">
                          {fileName}
                        </p>

                        <span className="hidden shrink-0 text-xs font-normal text-gray-400 dark:text-gray-500 xl:inline">
                          {updatedAt}
                        </span>
                      </div>
                    </button>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="px-2 py-1 text-xs font-normal text-gray-400 dark:text-gray-500">
              {searchQuery ? "No files match your search" : "No available files"}
            </p>
          )}
        </div>
      </div>
    </aside>
  );
}