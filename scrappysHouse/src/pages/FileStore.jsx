import { useState, useEffect } from "react";
import { useAuth } from "../auth/AuthProvider";
import { getBucketStructure, syncBucketStructure } from "../services/blob";

export default function FileStore() {
  const { user } = useAuth();
  const [files, setFiles] = useState([]);
  const [folders, setFolders] = useState([]);
  const [currentPath, setCurrentPath] = useState("/");
  const [selectedItems, setSelectedItems] = useState([]);
  const [showNewFolderModal, setShowNewFolderModal] = useState(false);
  const [showRenameModal, setShowRenameModal] = useState(false);
  const [newFolderName, setNewFolderName] = useState("");
  const [renameTarget, setRenameTarget] = useState(null);
  const [renameName, setRenameName] = useState("");
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [viewMode, setViewMode] = useState("list");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadFileStructure();
  }, [currentPath]);

  const handleSync = async () => {
    try {
      setIsLoading(true);
      await syncBucketStructure();
      await loadFileStructure();
    } catch (error) {
      console.error("Failed to sync bucket structure:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadFileStructure = async () => {
    try {
      setIsLoading(true);

      const response = await getBucketStructure();
      console.log("bucket structure response:", response);

      const structure = response?.bucket_structure ?? response ?? {};

      const currentFolder = getNodeAtPath(structure, currentPath);

      const nextFolders = [];
      const nextFiles = [];
      let idCounter = 1;

      Object.entries(currentFolder).forEach(([name, value]) => {
        const itemPath = currentPath === "/" ? `/${name}` : `${currentPath}${name}`;

        if (value && typeof value === "object") {
          nextFolders.push({
            id: `folder-${idCounter++}`,
            name,
            type: "folder",
            path: `${itemPath}`,
            createdAt: new Date().toISOString().split("T")[0],
          });
        } else {
          nextFiles.push({
            id: `file-${idCounter++}`,
            name,
            type: "file",
            size: "-",
            path: itemPath,
            createdAt: new Date().toISOString().split("T")[0],
          });
        }
      });

      setFolders(nextFolders);
      setFiles(nextFiles);
    } catch (error) {
      console.error("Failed to load bucket structure:", error);
      setFolders([]);
      setFiles([]);
    } finally {
      setIsLoading(false);
    }
  };

  const getNodeAtPath = (structure, path) => {
    if (!structure || path === "/") return structure || {};

    const parts = path.split("/").filter(Boolean);
    let current = structure;

    for (const part of parts) {
      if (!current?.[part] || typeof current[part] !== "object") {
        return {};
      }
      current = current[part];
    }

    return current;
  };

  const handleFileUpload = (uploadedFiles) => {
    Array.from(uploadedFiles).forEach((file, index) => {
      const fileId = Date.now() + index;
      setUploadProgress(prev => ({ ...prev, [fileId]: 0 }));

      const interval = setInterval(() => {
        setUploadProgress(prev => {
          const currentProgress = prev[fileId] || 0;
          if (currentProgress >= 100) {
            clearInterval(interval);
            setTimeout(() => {
              const newFile = {
                id: fileId,
                name: file.name,
                type: "file",
                size: (file.size / (1024 * 1024)).toFixed(1) + " MB",
                path: currentPath + file.name,
                createdAt: new Date().toISOString().split("T")[0],
              };
              setFiles(prev => [...prev, newFile]);
              setUploadProgress(prev => {
                const updated = { ...prev };
                delete updated[fileId];
                return updated;
              });
            }, 500);
            return prev;
          }
          return { ...prev, [fileId]: currentProgress + 10 };
        });
      }, 100);
    });
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const droppedFiles = e.dataTransfer.files;
    handleFileUpload(droppedFiles);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const createFolder = () => {
    if (newFolderName.trim()) {
      const newFolder = {
        id: Date.now(),
        name: newFolderName,
        type: "folder",
        path: currentPath + newFolderName,
        createdAt: new Date().toISOString().split("T")[0],
      };
      setFolders(prev => [...prev, newFolder]);
      setNewFolderName("");
      setShowNewFolderModal(false);
    }
  };

  const deleteSelected = () => {
    if (selectedItems.length > 0 && confirm(`Delete ${selectedItems.length} item(s)?`)) {
      setFiles(prev => prev.filter(file => !selectedItems.includes(file.id)));
      setFolders(prev => prev.filter(folder => !selectedItems.includes(folder.id)));
      setSelectedItems([]);
    }
  };

  const openSelectedFolder = () => {
    const selectedFolder = folders.find(folder => selectedItems.includes(folder.id));
    if (selectedFolder) {
      setCurrentPath(selectedFolder.path + "/");
      setSelectedItems([]);
    }
  };

  const startRename = (item) => {
    setRenameTarget(item);
    setRenameName(item.name);
    setShowRenameModal(true);
  };

  const confirmRename = () => {
    if (renameName.trim() && renameTarget) {
      if (renameTarget.type === "folder") {
        setFolders(prev => prev.map(folder =>
          folder.id === renameTarget.id ? { ...folder, name: renameName } : folder
        ));
      } else {
        setFiles(prev => prev.map(file =>
          file.id === renameTarget.id ? { ...file, name: renameName } : file
        ));
      }
      setShowRenameModal(false);
      setRenameTarget(null);
      setRenameName("");
    }
  };

  const toggleSelection = (itemId) => {
    setSelectedItems(prev =>
      prev.includes(itemId)
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const getFileIcon = (fileName) => {
    const ext = fileName.split(".").pop()?.toLowerCase();
    switch (ext) {
      case "pdf": return "📄";
      case "doc":
      case "docx": return "📝";
      case "xls":
      case "xlsx": return "📊";
      case "ppt":
      case "pptx": return "📈";
      case "jpg":
      case "jpeg":
      case "png":
      case "gif": return "🖼️";
      case "mp4":
      case "avi":
      case "mov": return "🎬";
      case "mp3":
      case "wav": return "🎵";
      case "zip":
      case "rar": return "📦";
      default: return "📄";
    }
  };

  const selectedFolders = selectedItems.filter(id =>
    folders.some(folder => folder.id === id)
  );
  const hasOnlyOneFolderSelected = selectedFolders.length === 1 && selectedItems.length === 1;

  const pathSegments = currentPath.split("/").filter(Boolean);

  return (
    <div>
      {isLoading && <div>Loading...</div>}
      <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-purple-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                File Store
              </h1>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setViewMode(viewMode === "grid" ? "list" : "grid")}
                  className="px-3 py-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  {viewMode === "grid" ? "📋" : "⊞"}
                </button>
                <button
                  onClick={() => setShowNewFolderModal(true)}
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                >
                  📁 New Folder
                </button>
                <button
                  onClick={() => handleSync()}
                  className="px-4 py-2 bg-green-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                >
                  📁 Sync Blob
                </button>
                <label className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors cursor-pointer">
                  📤 Upload
                  <input
                    type="file"
                    multiple
                    className="hidden"
                    onChange={(e) => handleFileUpload(e.target.files)}
                  />
                </label>
                {hasOnlyOneFolderSelected && (
                  <button
                    onClick={openSelectedFolder}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
                  >
                    📂 Open
                  </button>
                )}
                {selectedItems.length > 0 && (
                  <button
                    onClick={deleteSelected}
                    className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                  >
                    🗑️ Delete ({selectedItems.length})
                  </button>
                )}
              </div>
            </div>

            {/* Breadcrumb */}
            <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-300">
              <button
                onClick={() => setCurrentPath("/")}
                className="hover:text-purple-600 dark:hover:text-purple-400"
              >
                🏠 Home
              </button>
              {pathSegments.map((segment, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <span>/</span>
                  <button
                    onClick={() => setCurrentPath("/" + pathSegments.slice(0, index + 1).join("/") + "/")}
                    className="hover:text-purple-600 dark:hover:text-purple-400"
                  >
                    {segment}
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Upload Progress */}
          {Object.keys(uploadProgress).length > 0 && (
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
          )}

          {/* Drop Zone */}
          <div
            className={`bg-white dark:bg-gray-800 rounded-xl shadow-lg transition-all duration-300 ${
              isDragOver ? 'ring-4 ring-purple-500 bg-purple-50 dark:bg-purple-900/20' : ''
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
          >
            {isDragOver && (
              <div className="absolute inset-0 bg-purple-500/10 rounded-xl flex items-center justify-center z-10">
                <div className="text-center text-purple-600 dark:text-purple-400">
                  <div className="text-4xl mb-2">📤</div>
                  <div className="text-xl font-semibold">Drop files here to upload</div>
                </div>
              </div>
            )}

            {/* File Grid/List */}
            <div className="p-6">
              {folders.length === 0 && files.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">📁</div>
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                    No files or folders
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    Upload files or create folders to get started
                  </p>
                </div>
              ) : (
                <div className={viewMode === "grid"
                  ? "grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4"
                  : "space-y-2"
                }>
                  {/* ...existing code for folders and files... */}
                  {folders.map((folder) => (
                    <div
                      key={folder.id}
                      className={`${viewMode === "grid"
                        ? "p-4 rounded-lg border-2 cursor-pointer transition-all hover:shadow-md"
                        : "flex items-center p-3 rounded-lg border cursor-pointer transition-all hover:shadow-md"
                      } ${
                        selectedItems.includes(folder.id)
                          ? "border-purple-500 bg-purple-50 dark:bg-purple-900/20"
                          : "border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700/50"
                      }`}
                      onClick={() => toggleSelection(folder.id)}
                      onDoubleClick={() => setCurrentPath(folder.path + "/")}
                    >
                      {viewMode === "grid" ? (
                        <>
                          <div className="text-4xl mb-2 text-center">📁</div>
                          <div className="text-sm font-medium text-gray-900 dark:text-white text-center truncate">
                            {folder.name}
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-400 text-center mt-1">
                            {folder.createdAt}
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              startRename(folder);
                            }}
                            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 p-1 text-gray-500 hover:text-purple-600 transition-all"
                          >
                            ✏️
                          </button>
                        </>
                      ) : (
                        <>
                          <div className="text-2xl mr-3">📁</div>
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-medium text-gray-900 dark:text-white truncate">
                              {folder.name}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">
                              Folder • {folder.createdAt}
                            </div>
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              startRename(folder);
                            }}
                            className="p-1 text-gray-500 hover:text-purple-600 transition-colors"
                          >
                            ✏️
                          </button>
                        </>
                      )}
                    </div>
                  ))}

                  {/* Files */}
                  {files.map((file) => (
                    <div
                      key={file.id}
                      className={`${viewMode === "grid"
                        ? "p-4 rounded-lg border-2 cursor-pointer transition-all hover:shadow-md group relative"
                        : "flex items-center p-3 rounded-lg border cursor-pointer transition-all hover:shadow-md"
                      } ${
                        selectedItems.includes(file.id)
                          ? "border-purple-500 bg-purple-50 dark:bg-purple-900/20"
                          : "border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800"
                      }`}
                      onClick={() => toggleSelection(file.id)}
                    >
                      {viewMode === "grid" ? (
                        <>
                          <div className="text-4xl mb-2 text-center">{getFileIcon(file.name)}</div>
                          <div className="text-sm font-medium text-gray-900 dark:text-white text-center truncate">
                            {file.name}
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-400 text-center mt-1">
                            {file.size} • {file.createdAt}
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              startRename(file);
                            }}
                            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 p-1 text-gray-500 hover:text-purple-600 transition-all"
                          >
                            ✏️
                          </button>
                        </>
                      ) : (
                        <>
                          <div className="text-2xl mr-3">{getFileIcon(file.name)}</div>
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-medium text-gray-900 dark:text-white truncate">
                              {file.name}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">
                              {file.size} • {file.createdAt}
                            </div>
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              startRename(file);
                            }}
                            className="p-1 text-gray-500 hover:text-purple-600 transition-colors"
                          >
                            ✏️
                          </button>
                        </>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ...existing modal code... */}
        {/* New Folder Modal */}
        {showNewFolderModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-md">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                Create New Folder
              </h2>
              <input
                type="text"
                value={newFolderName}
                onChange={(e) => setNewFolderName(e.target.value)}
                placeholder="Folder name"
                className="w-full px-4 py-3 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent mb-4"
                onKeyPress={(e) => e.key === 'Enter' && createFolder()}
                autoFocus
              />
              <div className="flex space-x-3">
                <button
                  onClick={() => {
                    setShowNewFolderModal(false);
                    setNewFolderName("");
                  }}
                  className="flex-1 py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={createFolder}
                  disabled={!newFolderName.trim()}
                  className="flex-1 py-2 px-4 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
                >
                  Create
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Rename Modal */}
        {showRenameModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-md">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                Rename {renameTarget?.type === "folder" ? "Folder" : "File"}
              </h2>
              <input
                type="text"
                value={renameName}
                onChange={(e) => setRenameName(e.target.value)}
                className="w-full px-4 py-3 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent mb-4"
                onKeyPress={(e) => e.key === 'Enter' && confirmRename()}
                autoFocus
              />
              <div className="flex space-x-3">
                <button
                  onClick={() => {
                    setShowRenameModal(false);
                    setRenameTarget(null);
                    setRenameName("");
                  }}
                  className="flex-1 py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmRename}
                  disabled={!renameName.trim()}
                  className="flex-1 py-2 px-4 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
                >
                  Rename
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}