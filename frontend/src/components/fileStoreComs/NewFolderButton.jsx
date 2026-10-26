export default function NewFolderButton({ onNewFolder, className }) {
  return (
    <button
      onClick={onNewFolder}
      className={className}
    >
      📁 New Folder
    </button>
  );
}