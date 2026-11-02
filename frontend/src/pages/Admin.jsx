export default function Admin() {
  return (
    <div className="min-h-[calc(100vh-4.25rem)] bg-slate-50 px-4 py-8 dark:bg-slate-950 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-5xl">
        <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-indigo-600 dark:text-indigo-300">Administration</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950 dark:text-white">Admin workspace</h1>
          <p className="mt-3 max-w-xl text-sm leading-6 text-slate-500 dark:text-slate-400">You have the permissions needed to manage Scrappy resources.</p>
        </div>
      </div>
    </div>
  );
}
