import { useState, useEffect } from "react";
import { useAuth } from "../auth/AuthProvider";
import { getBucketStructure, syncBucketStructure, uploadFile } from "../services/blob";
import CreateFolder from "../components/fileStoreComs/CreateFolder";
import FileRename from "../components/fileStoreComs/FileRename";
import UploadProgress from "../components/fileStoreComs/UploadProgress";
import FileStoreHeader from "../components/fileStoreComs/FileStoreHeader";
import FileDisplay from "../components/fileStoreComs/FileDisplay";

export default function FileStore() {
  const { user } = useAuth();
  const [files, setFiles] = useState([]);
  const [folders, setFolders] = useState([]);
  const [currentPath, setCurrentPath] = useState("/");
  const [selectedItems, setSelectedItems] = useState([]);
  const [showNewFolderModal, setShowNewFolderModal] = useState(false);
  const [renameTarget, setRenameTarget] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadFileStructure();
  }, [currentPath]);

  const normalizedQuery = searchQuery.trim().toLowerCase();

  const filteredFolders = folders.filter((folder) =>
    folder.name.toLowerCase().includes(normalizedQuery)
  );

  const filteredFiles = files.filter((file) =>
    file.name.toLowerCase().includes(normalizedQuery)
  );

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
            path: itemPath,
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

  const handleFileUpload = async (uploadedFiles) => {
    const filesArray = Array.from(uploadedFiles);

    for (const file of filesArray) {
      const fileId = `upload-${Date.now()}-${file.name}`;

      setUploadProgress((prev) => ({
        ...prev,
        [fileId]: 0,
      }));

      try {
        const response = await uploadFile(file, (progressEvent) => {
          const total = progressEvent.total || file.size || 1;
          const percent = Math.round((progressEvent.loaded * 100) / total);

          setUploadProgress((prev) => ({
            ...prev,
            [fileId]: percent,
          }));
        });

        const newFile = {
          id: `file-${Date.now()}-${file.name}`,
          name: file.name,
          type: "file",
          size: (file.size / (1024 * 1024)).toFixed(1) + " MB",
          path: currentPath + file.name,
          createdAt: new Date().toISOString().split("T")[0],
          ...(response || {}),
        };

        setFiles((prev) => [...prev, newFile]);
      } catch (error) {
        console.error(`Failed to upload ${file.name}:`, error);
      } finally {
        setUploadProgress((prev) => {
          const updated = { ...prev };
          delete updated[fileId];
          return updated;
        });
      }
    }
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

  const createFolder = (folderName) => {
    const newFolder = {
      id: `folder-${Date.now()}`,
      name: folderName,
      type: "folder",
      path: currentPath + folderName,
      createdAt: new Date().toISOString().split("T")[0],
    };

    setFolders((prev) => [...prev, newFolder]);
  };

  const deleteSelected = () => {
    if (selectedItems.length > 0 && confirm(`Delete ${selectedItems.length} item(s)?`)) {
      setFiles((prev) => prev.filter((file) => !selectedItems.includes(file.id)));
      setFolders((prev) => prev.filter((folder) => !selectedItems.includes(folder.id)));
      setSelectedItems([]);
    }
  };

  const openSelectedFolder = () => {
    const selectedFolder = folders.find((folder) => selectedItems.includes(folder.id));

    if (selectedFolder) {
      setCurrentPath(selectedFolder.path + "/");
      setSelectedItems([]);
    }
  };

  const startRename = (item) => {
    setRenameTarget(item);
  };

  const confirmRename = (target, newName) => {
    if (target.type === "folder") {
      setFolders((prev) =>
        prev.map((folder) =>
          folder.id === target.id ? { ...folder, name: newName } : folder
        )
      );
    } else {
      setFiles((prev) =>
        prev.map((file) =>
          file.id === target.id ? { ...file, name: newName } : file
        )
      );
    }

    setRenameTarget(null);
  };

  const toggleSelection = (itemId) => {
    setSelectedItems((prev) =>
      prev.includes(itemId)
        ? prev.filter((id) => id !== itemId)
        : [...prev, itemId]
    );
  };

  const selectedFolders = selectedItems.filter((id) =>
    folders.some((folder) => folder.id === id)
  );

  const hasOnlyOneFolderSelected =
    selectedFolders.length === 1 && selectedItems.length === 1;

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-purple-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        {isLoading && (
          <div className="mb-4 text-sm text-gray-600 dark:text-gray-300">
            Loading...
          </div>
        )}

        <FileStoreHeader
          onNewFolder={() => setShowNewFolderModal(true)}
          onSync={handleSync}
          onFileUpload={handleFileUpload}
          hasOnlyOneFolderSelected={hasOnlyOneFolderSelected}
          onOpenFolder={openSelectedFolder}
          selectedItems={selectedItems}
          onDeleteSelected={deleteSelected}
          currentPath={currentPath}
          onPathChange={setCurrentPath}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
        />

        <UploadProgress uploadProgress={uploadProgress} />

        <FileDisplay
          folders={filteredFolders}
          files={filteredFiles}
          selectedItems={selectedItems}
          onToggleSelection={toggleSelection}
          onDoubleClickFolder={setCurrentPath}
          onStartRename={startRename}
          isDragOver={isDragOver}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        />
      </div>

      <CreateFolder
        isVisible={showNewFolderModal}
        onClose={() => setShowNewFolderModal(false)}
        onCreateFolder={createFolder}
      />

      <FileRename
        renameTarget={renameTarget}
        onClose={() => setRenameTarget(null)}
        onConfirmRename={confirmRename}
      />
    </div>
  );
}