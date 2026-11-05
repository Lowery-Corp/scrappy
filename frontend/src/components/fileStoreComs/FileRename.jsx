import { useState } from "react";

export default function FileRename({ renameTarget, onClose, onConfirmRename }) {
  const [newName, setNewName] = useState(renameTarget?.name || "");

  const handleSubmit = async () => {
    if (newName.trim() && renameTarget) {
      await onConfirmRename(renameTarget, newName.trim());
      onClose();
    }
  };

  const handleClose = () => {
    setNewName("");
    onClose();
  };

  if (!renameTarget) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/45 p-4 backdrop-blur-sm" onMouseDown={(event) => event.target === event.currentTarget && handleClose()}>
      <div role="dialog" aria-modal="true" aria-labelledby="rename-title" className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-6 shadow-2xl dark:border-slate-700 dark:bg-slate-900">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-indigo-600 dark:text-indigo-300">File store</p>
        <h2 id="rename-title" className="mb-5 mt-1 text-xl font-bold tracking-tight text-slate-950 dark:text-white">
          Rename {renameTarget?.type === "folder" ? "Folder" : "File"}
        </h2>
        <input
          type="text"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          className="h-12 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-900 placeholder:text-slate-400 focus:border-indigo-500 focus:bg-white focus:outline-none focus:ring-4 focus:ring-indigo-500/10 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          autoFocus
        />
        <div className="mt-5 flex gap-3">
          <button
            onClick={handleClose}
            className="h-11 flex-1 rounded-xl border border-slate-200 px-4 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={!newName.trim()}
            className="h-11 flex-1 rounded-xl bg-indigo-600 px-4 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Rename
          </button>
        </div>
      </div>
    </div>
  );
}
