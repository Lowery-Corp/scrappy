export default function Unauthorized() {
  return (
    <div className="flex min-h-[calc(100vh-4.25rem)] items-center justify-center bg-slate-50 px-4 dark:bg-slate-950">
      <div className="max-w-md rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-amber-50 text-xl text-amber-600 dark:bg-amber-500/10 dark:text-amber-300">!</div>
        <h1 className="mt-5 text-2xl font-bold tracking-tight text-slate-950 dark:text-white">Access restricted</h1>
        <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">You do not have permission to view this page.</p>
      </div>
    </div>
  );
}
