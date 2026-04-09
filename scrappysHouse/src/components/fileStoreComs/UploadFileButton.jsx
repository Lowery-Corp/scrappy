export default function UploadFileButton({ onFileUpload, className }) {
  return (
    <label className={className}>
      📤 Upload
      <input
        type="file"
        multiple
        className="hidden"
        onChange={(e) => onFileUpload(e.target.files)}
      />
    </label>
  );
}