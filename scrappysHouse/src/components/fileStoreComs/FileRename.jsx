import { useState } from "react";

export default function FileRename({ renameTarget, onClose, onConfirmRename }) {
  const [newName, setNewName] = useState(renameTarget?.name || "");

  const handleSubmit = () => {
    if (newName.trim() && renameTarget) {
      onConfirmRename(renameTarget, newName);
      onClose();
    }
  };

  const handleClose = () => {
    setNewName("");
    onClose();
  };

  if (!renameTarget) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-md">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          Rename {renameTarget?.type === "folder" ? "Folder" : "File"}
        </h2>
        <input
          type="text"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          className="w-full px-4 py-3 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent mb-4"
          onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
          autoFocus
        />
        <div className="flex space-x-3">
          <button
            onClick={handleClose}
            className="flex-1 py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={!newName.trim()}
            className="flex-1 py-2 px-4 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
          >
            Rename
          </button>
        </div>
      </div>
    </div>
  );
}