export default function ChatPanelHeader({ chat }) {
  const documentCount = chat?.relevant_file_ids?.length ?? 0;
  const conversationName = chat?.conversation_name ?? "New Conversation";

  return (
    <header className="border-b border-slate-200 px-5 py-4 text-left dark:border-slate-800">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-indigo-600 dark:text-indigo-300">
            {documentCount} indexed documents
          </p>

          <h2 className="m-0 truncate text-lg font-bold tracking-tight text-slate-950 dark:text-white">
            {conversationName}
          </h2>
        </div>
      </div>
    </header>
  );
}
