export default function ChatPanelHeader({ chat }) {
  const documentCount = chat?.relevant_file_ids?.length ?? 0;
  const conversationName = chat?.conversation_name ?? "New Conversation";

  return (
    <header className="border-b border-gray-200 p-5 text-left dark:border-gray-700">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm font-medium text-purple-600 dark:text-purple-400">
            {documentCount} indexed documents
          </p>

          <h2 className="m-0 text-2xl font-bold text-gray-900 dark:text-white">
            {conversationName}
          </h2>
        </div>
      </div>
    </header>
  );
}