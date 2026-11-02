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
      className="border-t border-slate-200 bg-white p-3 dark:border-slate-800 dark:bg-slate-900"
    >
      <div className="flex flex-col gap-2 rounded-2xl border border-slate-200 bg-slate-50 p-2 shadow-sm dark:border-slate-700 dark:bg-slate-950 md:flex-row md:items-end">
        <label className="flex-1">
          <span className="sr-only">Message</span>
          <textarea
            value={value}
            onChange={(event) => onChange(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your documents..."
            rows="2"
            className="min-h-14 w-full resize-none border-0 bg-transparent px-2 py-1 text-sm leading-6 text-slate-900 outline-none placeholder:text-slate-400 dark:text-slate-100"
          />
        </label>
        <button
          type="submit"
          disabled={!value.trim()}
          className="rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-slate-300 dark:disabled:bg-slate-700"
        >
          Send
        </button>
      </div>
    </form>
  );
}
