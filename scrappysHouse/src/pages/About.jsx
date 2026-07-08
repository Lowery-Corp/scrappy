const capabilities = [
  {
    title: "Private file workspace",
    description:
      "Users can upload, browse, organize, sync, and delete files through a protected file store backed by per-user object storage and database metadata.",
  },
  {
    title: "Document chat",
    description:
      "Ready documents can be attached to conversations so users can ask questions, compare material, and keep context across chat sessions.",
  },
  {
    title: "Processing pipeline",
    description:
      "Uploaded files are tracked through metadata records and file jobs so ingestion, chunking, indexing, and readiness can be handled outside the UI.",
  },
  {
    title: "Authenticated access",
    description:
      "The app uses protected routes, HTTP-only session cookies, and role-aware screens so user data stays scoped to the signed-in account.",
  },
];

const structure = [
  {
    name: "scrappysHouse",
    role: "React frontend",
    details:
      "Vite, React Router, Tailwind CSS, and Axios power the browser experience for login, the file store, document chat, admin views, and shared UI components.",
  },
  {
    name: "scrappysScrapyard",
    role: "FastAPI backend",
    details:
      "FastAPI routes expose authentication, blob storage, file metadata, file jobs, file chunks, conversations, messages, and health checks under /api/v1.",
  },
  {
    name: "PostgreSQL",
    role: "Persistent metadata",
    details:
      "SQLAlchemy models and Alembic migrations manage user file stores, uploaded file records, processing jobs, document chunks, conversations, logs, and related application state.",
  },
  {
    name: "Object storage",
    role: "Uploaded file content",
    details:
      "MinIO-compatible storage keeps the raw user files in per-user buckets while PostgreSQL stores the searchable metadata and folder structure.",
  },
  {
    name: "Redis and workers",
    role: "Support services",
    details:
      "Redis supports backend caching, while file jobs can be queued for offloaded ingestion work such as parsing, chunking, embedding, and readiness updates.",
  },
];

export default function About() {
  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gray-50 px-4 py-8 text-gray-900 dark:bg-gray-900 dark:text-gray-100 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-5xl space-y-8">
        <section className="space-y-4">
          <p className="text-sm font-medium uppercase text-purple-700 dark:text-purple-300">
            About Scrappy
          </p>
          <div className="max-w-3xl space-y-4">
            <h1 className="text-3xl font-semibold tracking-normal text-gray-950 dark:text-white sm:text-4xl">
              A file workspace and document chat system for searchable knowledge.
            </h1>
            <p className="text-base leading-7 text-gray-700 dark:text-gray-300">
              Scrappy is a full-stack application for storing user documents,
              processing them into searchable metadata, and using those files as
              context in AI-assisted conversations. It combines a secure file
              store, document ingestion workflow, and conversation interface so
              users can move from upload to analysis without leaving the app.
            </p>
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-2">
          {capabilities.map((capability) => (
            <article
              key={capability.title}
              className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-800"
            >
              <h2 className="text-base font-semibold text-gray-950 dark:text-white">
                {capability.title}
              </h2>
              <p className="mt-2 text-sm leading-6 text-gray-600 dark:text-gray-300">
                {capability.description}
              </p>
            </article>
          ))}
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-gray-950 dark:text-white">
            What The App Is For
          </h2>
          <div className="space-y-3 text-sm leading-6 text-gray-700 dark:text-gray-300">
            <p>
              The core purpose of Scrappy is to make document-heavy work easier
              to manage and query. A user can upload files into a personal store,
              wait for processing to mark usable documents as ready, then select
              those files in the document chat sidebar as context for a
              conversation.
            </p>
            <p>
              This makes the app useful for reviewing internal documents, asking
              questions about uploaded PDFs, comparing source material, building
              summaries, and keeping chat history tied to the files that informed
              each conversation. Admin-facing metadata and job endpoints support
              inspection and repair of the ingestion flow when files need
              operational attention.
            </p>
          </div>
        </section>

        <section className="space-y-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-950 dark:text-white">
              App Structure
            </h2>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-gray-600 dark:text-gray-300">
              The repository is split into a browser client, an API service, and
              supporting infrastructure. Each layer has a focused responsibility
              so UI behavior, API contracts, persistence, and background work can
              evolve independently.
            </p>
          </div>

          <div className="overflow-hidden rounded-lg border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
            <div className="grid grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(0,2fr)] border-b border-gray-200 bg-gray-100 px-4 py-2 text-xs font-semibold uppercase text-gray-500 dark:border-gray-700 dark:bg-gray-900/50 dark:text-gray-400">
              <div>Layer</div>
              <div>Role</div>
              <div>Responsibility</div>
            </div>

            {structure.map((item) => (
              <div
                key={item.name}
                className="grid grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(0,2fr)] gap-3 border-b border-gray-100 px-4 py-3 text-sm last:border-b-0 dark:border-gray-700"
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
