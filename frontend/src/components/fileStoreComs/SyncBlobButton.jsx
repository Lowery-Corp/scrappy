export default function SyncBlogButton({ onSync, className }) {
  return (
    <button
      type="button"
      onClick={onSync}
      className={className}
    >
      <span aria-hidden="true">↻</span> Sync storage
    </button>
  );
}
