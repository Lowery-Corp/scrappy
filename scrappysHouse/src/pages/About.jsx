const capabilities = [
  {
    title: "Private workspace",
    stat: "Files",
    description:
      "Upload, browse, organize, sync, and delete documents through a protected store backed by per-user object storage and database metadata.",
    color:
      "border-violet-200 bg-violet-50 text-violet-900 shadow-violet-200/70 dark:border-violet-800 dark:bg-violet-950/40 dark:text-violet-100 dark:shadow-violet-950/30",
    accent: "bg-violet-500",
  },
  {
    title: "Document chat",
    stat: "Ask",
    description:
      "Attach ready documents to conversations, ask questions, compare material, and keep the selected sources tied to chat history.",
    color:
      "border-sky-200 bg-sky-50 text-sky-900 shadow-sky-200/70 dark:border-sky-800 dark:bg-sky-950/40 dark:text-sky-100 dark:shadow-sky-950/30",
    accent: "bg-sky-500",
  },
  {
    title: "Processing flow",
    stat: "Ready",
    description:
      "Track uploads through jobs and metadata so ingestion, chunking, indexing, and readiness can run outside the main interface.",
    color:
      "border-emerald-200 bg-emerald-50 text-emerald-900 shadow-emerald-200/70 dark:border-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-100 dark:shadow-emerald-950/30",
    accent: "bg-emerald-500",
  },
  {
    title: "Scoped access",
    stat: "Auth",
    description:
      "Protected routes, HTTP-only session cookies, and role-aware screens keep each account focused on its own files and tools.",
    color:
      "border-amber-200 bg-amber-50 text-amber-900 shadow-amber-200/70 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-100 dark:shadow-amber-950/30",
    accent: "bg-amber-500",
  },
];

const structure = [
  {
    name: "scrappysHouse",
    role: "React frontend",
    details:
      "Vite, React Router, Tailwind CSS, and Axios power the browser experience for login, files, chat, admin views, and shared UI.",
  },
  {
    name: "scrappysScrapyard",
    role: "FastAPI backend",
    details:
      "API routes expose authentication, blob storage, file metadata, jobs, chunks, conversations, messages, and health checks.",
  },
  {
    name: "PostgreSQL",
    role: "Metadata",
    details:
      "SQLAlchemy models and Alembic migrations manage file stores, uploaded records, processing jobs, chunks, conversations, and logs.",
  },
  {
    name: "Object storage",
    role: "File content",
    details:
      "MinIO-compatible storage keeps raw user files in per-user buckets while the database stores searchable metadata.",
  },
  {
    name: "Redis, RabbitMQ, and Celery",
    role: "Caching and workers",
    details:
      "Redis supports backend caching, while RabbitMQ and Celery run file jobs for offloaded parsing, chunking, embedding, and readiness updates.",
  },
];

function Bubble({ item, className = "" }) {
  return (
    <article
      tabIndex={0}
      className={[
        "group relative z-0 flex aspect-square w-full max-w-64 flex-col items-center justify-center overflow-hidden rounded-full border p-6 text-center shadow-sm outline-none transition-all duration-300 hover:z-10 hover:-translate-y-1 hover:scale-105 hover:shadow-xl focus:z-10 focus:scale-105 focus-visible:-translate-y-1 focus-visible:ring-4 focus-visible:ring-purple-200 dark:focus-visible:ring-purple-900",
        item.color,
        className,
      ].join(" " )}
    >
      <span
        className={["absolute right-8 top-8 h-3 w-3 rounded-full", item.accent].join(" " )}
      />
      <div className="transition-transform duration-300 group-hover:-translate-y-14 group-focus:-translate-y-14">
        <p className="text-xs font-semibold uppercase tracking-normal opacity-70">
          {item.stat || item.role}
        </p>
        <h2 className="mt-2 max-w-44 text-xl font-semibold leading-tight text-inherit">
          {item.title || item.name}
        </h2>
      </div>
      <p className="absolute inset-x-7 bottom-7 translate-y-3 text-sm leading-5 opacity-0 transition-all duration-300 group-hover:translate-y-0 group-hover:opacity-100 group-focus:translate-y-0 group-focus:opacity-100">
        {item.description || item.details}
      </p>
    </article>
  );
}

export default function About() {
  return (
    <div className="min-h-[calc(100vh-4rem)] overflow-hidden bg-slate-50 px-4 py-10 text-gray-900 dark:bg-gray-900 dark:text-gray-100 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-6xl flex-col items-center gap-12 text-center">
        <section className="flex max-w-4xl flex-col items-center">
          <p className="text-sm font-semibold uppercase tracking-normal text-purple-700 dark:text-purple-300">
            About Scrappy
          </p>
          <h1 className="mt-4 max-w-4xl text-balance text-4xl font-semibold leading-tight tracking-normal text-gray-950 dark:text-white sm:text-5xl">
            A centered workspace for files, search, and document chat.
          </h1>
          <p className="mt-5 max-w-3xl text-base leading-7 text-gray-700 dark:text-gray-300">
            Scrappy stores user documents, processes them into searchable
            metadata, and turns ready files into context for AI-assisted
            conversations. Go from upload to analysis without leaving the app.
          </p>
        </section>

        <section className="grid w-full max-w-5xl grid-cols-1 place-items-center gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {capabilities.map((capability, index) => (
            <Bubble
              key={capability.title}
              item={capability}
              className={index % 2 === 0 ? "lg:mt-8" : "lg:mb-8"}
            />
          ))}
        </section>

        <section className="flex max-w-3xl flex-col items-center gap-3">
          <h2 className="text-2xl font-semibold text-gray-950 dark:text-white">
            What The App Is For
          </h2>
          <p className="text-sm leading-6 text-gray-700 dark:text-gray-300">
            Scrappy is meant for document-heavy work: reviewing internal files,
            asking questions about uploaded PDFs, comparing source material,
            building summaries, and keeping chat history connected to the files
            that informed each conversation.
          </p>
          <p className="text-sm leading-6 text-gray-700 dark:text-gray-300">
            Admin-facing metadata and job endpoints support inspection and
            repair of the ingestion flow when files need operational attention.
          </p>
        </section>

        <section className="flex w-full flex-col items-center gap-5">
          <div className="max-w-3xl">
            <h2 className="text-2xl font-semibold text-gray-950 dark:text-white">
              App Structure
            </h2>
            <p className="mt-3 text-sm leading-6 text-gray-600 dark:text-gray-300">
              The repository is split into focused layers so UI behavior, API
              contracts, persistence, and background work can evolve cleanly.
            </p>
          </div>

          <div className="w-full max-w-5xl overflow-hidden rounded-lg border border-gray-200 bg-white text-left shadow-sm dark:border-gray-700 dark:bg-gray-800">
            <div className="grid grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(0,2fr)] border-b border-gray-200 bg-gray-100 px-4 py-2 text-xs font-semibold uppercase tracking-normal text-gray-500 dark:border-gray-700 dark:bg-gray-900/50 dark:text-gray-400">
              <div>Layer</div>
              <div>Role</div>
              <div>Responsibility</div>
            </div>

            {structure.map((item) => (
              <div
                key={item.name}
                className="grid grid-cols-1 gap-2 border-b border-gray-100 px-4 py-4 text-sm last:border-b-0 dark:border-gray-700 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(0,2fr)] md:gap-3 md:py-3"
              >
                <div className="font-medium text-gray-950 dark:text-white">
                  {item.name}
                </div>
                <div className="text-gray-600 dark:text-gray-300">
                  {item.role}
                </div>
                <div className="leading-6 text-gray-600 dark:text-gray-300">
                  {item.details}
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
