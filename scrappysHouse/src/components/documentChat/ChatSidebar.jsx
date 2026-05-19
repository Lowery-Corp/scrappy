export default function ChatSidebar({ chats, activeChatId, onSelectChat }) {
  return (
    <aside className="flex w-full flex-col rounded-2xl border border-gray-200 bg-white/90 shadow-xl dark:border-gray-700 dark:bg-gray-800/90 lg:w-80">
      <div className="border-b border-gray-200 p-5 text-left dark:border-gray-700">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-sm font-medium text-purple-600 dark:text-purple-400">
              Document Chat
            </p>
            <h1 className="m-0 text-2xl font-bold text-gray-900 dark:text-white">
              Chats
            </h1>
          </div>
          <button
            type="button"
            className="rounded-md bg-purple-600 px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-purple-700"
          >
            New
          </button>
        </div>

        <label className="mt-4 block">
          <span className="sr-only">Search chats</span>
          <input
            type="search"
            placeholder="Search chats"
            className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 outline-none transition-colors placeholder:text-gray-400 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 dark:border-gray-600 dark:bg-gray-900 dark:text-gray-100 dark:focus:ring-purple-900"
          />
        </label>
      </div>

      <div className="flex gap-2 overflow-x-auto p-3 lg:flex-col lg:overflow-visible">
        {chats.map((chat) => {
          const isActive = chat.id === activeChatId;

          return (
            <button
              type="button"
              key={chat.conversation_name}
              onClick={() => onSelectChat(chat.id)}
              className={`min-w-72 rounded-xl border p-4 text-left transition-colors lg:min-w-0 ${
                isActive
                  ? "border-purple-300 bg-purple-50 shadow-sm dark:border-purple-700 dark:bg-purple-950/40"
                  : "border-transparent bg-transparent hover:bg-gray-50 dark:hover:bg-gray-700/60"
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <h2 className="m-0 text-base font-semibold text-gray-900 dark:text-white">
                  {chat.conversation_name}
                </h2>
                <span className="shrink-0 text-xs text-gray-500 dark:text-gray-400">
                  {chat.updated_at}
                </span>
              </div>
              <p className="mt-2 overflow-hidden text-ellipsis whitespace-nowrap text-sm text-gray-600 dark:text-gray-300">
                {chat.preview}
              </p>
              <div className="mt-3 inline-flex rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-600 dark:bg-gray-700 dark:text-gray-300">
                {chat.relevant_file_ids.length} documents
              </div>
            </button>
          );
        })}
      </div>
    </aside>
  );
}
