export default function ChatComposer({ value, onChange, onSubmit }) {
  return (
    <form
      onSubmit={onSubmit}
      className="border-t border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800"
    >
      <div className="flex flex-col gap-3 rounded-xl border border-gray-200 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-900 md:flex-row md:items-end">
        <label className="flex-1">
          <span className="sr-only">Message</span>
          <textarea
            value={value}
            onChange={(event) => onChange(event.target.value)}
            placeholder="Ask a question about your documents..."
            rows="3"
            className="min-h-24 w-full resize-none border-0 bg-transparent text-sm text-gray-900 outline-none placeholder:text-gray-400 dark:text-gray-100"
          />
        </label>
        <button
          type="submit"
          disabled={!value.trim()}
          className="rounded-md bg-purple-600 px-5 py-3 text-sm font-medium text-white transition-colors hover:bg-purple-700 disabled:cursor-not-allowed disabled:bg-gray-300 dark:disabled:bg-gray-700"
        >
          Send
        </button>
      </div>
    </form>
  );
}
