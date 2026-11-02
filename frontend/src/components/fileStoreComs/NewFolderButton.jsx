export default function NewFolderButton({ onNewFolder, className }) {
  return (
    <button
      type="button"
      onClick={onNewFolder}
      className={className}
    >
      <span aria-hidden="true">＋</span> New folder
    </button>
  );
}
