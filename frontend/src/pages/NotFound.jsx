import { Link } from "react-router";

export default function NotFound() {
  return (
    <div className="flex min-h-[calc(100vh-4.25rem)] items-center justify-center bg-slate-50 px-4 dark:bg-slate-950">
      <div className="max-w-md text-center">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-indigo-600 dark:text-indigo-300">404</p>
        <h1 className="mt-3 text-4xl font-bold tracking-tight text-slate-950 dark:text-white">Page not found</h1>
        <p className="mt-3 text-sm leading-6 text-slate-500 dark:text-slate-400">The page you’re looking for doesn’t exist or may have moved.</p>
        <Link to="/" className="mt-6 inline-flex rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700">
          Return to workspace
        </Link>
      </div>
    </div>
  );
}
