export default function SyncBlogButton({ onSync, className }) {
  return (
    <button
      onClick={onSync}
      className={className}
    >
      📁 Sync Blob
    </button>
  );
}