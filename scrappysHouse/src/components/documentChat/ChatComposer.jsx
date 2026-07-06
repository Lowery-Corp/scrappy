export default function ChatComposer({ value, onChange, onSubmit }) {
  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      event.currentTarget.form?.requestSubmit();
    }
  };

  return (
    <form
      onSubmit={onSubmit}
      className="border-t border-gray-200 bg-white p-2 dark:border-gray-700 dark:bg-gray-800"
    >
      <div className="flex flex-col gap-2 rounded-lg border border-gray-200 bg-gray-50 p-2 dark:border-gray-700 dark:bg-gray-900 md:flex-row md:items-end">
        <label className="flex-1">
          <span className="sr-only">Message</span>
          <textarea
            value={value}
            onChange={(event) => onChange(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your documents..."
            rows="2"
            className="min-h-14 w-full resize-none border-0 bg-transparent text-sm leading-5 text-gray-900 outline-none placeholder:text-gray-400 dark:text-gray-100"
          />
        </label>
        <button
          type="submit"
          disabled={!value.trim()}
          className="rounded-md bg-purple-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-purple-700 disabled:cursor-not-allowed disabled:bg-gray-300 dark:disabled:bg-gray-700"
        >
          Send
        </button>
      </div>
    </form>
  );
}
