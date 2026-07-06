import { useMemo, useState } from "react";

export default function ChatSidebar({
  chats,
  activeChatId,
  onSelectChat,
  newChat,
  deleteChat,
  multiSelectMode,
  setMultiSelectMode,
  multipleSelectedChatIds,
  setMultipleSelectedChatIds,
}) {
  const [searchQuery, setSearchQuery] = useState("");
  const userChats = useMemo(() => (Array.isArray(chats) ? chats : []), [chats]);
  const normalizedSearchQuery = searchQuery.trim().toLowerCase();

  const filteredChats = useMemo(() => {
    if (!normalizedSearchQuery) {
      return userChats;
    }

    return userChats.filter((chat) => {
      const chatName = chat.conversation_name || "New Chat";
      const chatPreview = chat.preview || "";

      return `${chatName} ${chatPreview}`
        .toLowerCase()
        .includes(normalizedSearchQuery);
    });
  }, [userChats, normalizedSearchQuery]);

  const filteredChatIds = filteredChats.map((chat) => chat.conversation_id);
  const allFilteredChatsSelected =
    filteredChatIds.length > 0 &&
    filteredChatIds.every((chatId) => multipleSelectedChatIds.includes(chatId));

  const toggleChatSelection = (chatId) => {
    setMultipleSelectedChatIds((previousChatIds) =>
      previousChatIds.includes(chatId)
        ? previousChatIds.filter((selectedChatId) => selectedChatId !== chatId)
        : [...previousChatIds, chatId],
    );
  };

  const toggleSelectAll = () => {
    setMultipleSelectedChatIds((previousChatIds) => {
      if (allFilteredChatsSelected) {
        return previousChatIds.filter(
          (selectedChatId) => !filteredChatIds.includes(selectedChatId),
        );
      }

      return Array.from(new Set([...previousChatIds, ...filteredChatIds]));
    });
  };

  return (
    <aside className="flex w-full flex-col rounded-xl border border-gray-200 bg-white/95 shadow-lg dark:border-gray-700 dark:bg-gray-800/95 lg:w-72 xl:w-80">
      <div className="border-b border-gray-200 p-3 text-left dark:border-gray-700">
        <div className="flex items-center justify-between gap-2">
          <div>
            <p className="text-xs font-medium text-purple-600 dark:text-purple-400">
              Document Chat
            </p>
            <h1 className="m-0 text-xl font-semibold text-gray-900 dark:text-white">
              Chats
            </h1>
          </div>

          <button
            type="button"
            className="rounded-md bg-purple-600 px-2.5 py-1.5 text-sm font-medium text-white transition-colors hover:bg-purple-700"
            onClick={() => newChat()}
          >
            New
          </button>
        </div>

        <label className="mt-3 block">
          <span className="sr-only">Search chats</span>
          <input
            type="search"
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
            placeholder="Search chats"
            className="h-9 w-full rounded-md border border-gray-300 bg-white px-2.5 text-sm text-gray-900 outline-none transition-colors placeholder:text-gray-400 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 dark:border-gray-600 dark:bg-gray-900 dark:text-gray-100 dark:focus:ring-purple-900"
          />
        </label>

        {/* Multi-select actions */}
        <div className="mt-3 flex items-center justify-between gap-2">
          <button
            type="button"
            className="rounded-md border border-gray-300 px-2.5 py-1.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
            onClick={() => {
              // toggle multi-select mode
              setMultiSelectMode(!multiSelectMode);
              if (multiSelectMode) {
                setMultipleSelectedChatIds([]);
              }
            }}
          >
            {multiSelectMode ? "Cancel" : "Select"}
          </button>

          {multiSelectMode && (
            <div className="flex items-center gap-2">
              <button
                type="button"
                className="rounded-md border border-gray-300 px-2.5 py-1.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
                onClick={toggleSelectAll}
                disabled={filteredChatIds.length === 0}
              >
                {allFilteredChatsSelected ? "Clear all" : "Select all"}
              </button>

              <button
                type="button"
                disabled={multipleSelectedChatIds.length === 0}
                className="rounded-md bg-red-600 px-2.5 py-1.5 text-sm font-medium text-white transition-colors hover:bg-red-700 disabled:cursor-not-allowed disabled:bg-red-300 dark:disabled:bg-red-900"
                onClick={() => {
                  if (multipleSelectedChatIds.length === 0) return;
                  deleteChat(multipleSelectedChatIds);
                  setMultipleSelectedChatIds([]);
                }}
              >
                Delete
                {multipleSelectedChatIds.length > 0
                  ? ` (${multipleSelectedChatIds.length})`
                  : ""}
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="flex gap-2 overflow-x-auto p-2 lg:flex-col lg:overflow-visible">
        {filteredChats.map((chat) => {
          const isActive = chat.conversation_id === activeChatId;
          const chatName = chat.conversation_name || "New Chat";
          const chatPreview = chat.preview || "No messages yet.";
          const updatedAt = new Date(chat.updated_at).toLocaleString();
          const relevantFilesCount = chat.relevant_file_ids?.length ?? 0;
          const chatId = chat.conversation_id;

          const isSelected = multipleSelectedChatIds.includes(chatId);

          return (
            <div
              key={chatId}
              className={`group min-w-64 rounded-lg border px-3 py-2.5 text-left transition-colors lg:min-w-0 ${
                isActive
                  ? "border-purple-300 bg-purple-50 shadow-sm dark:border-purple-700 dark:bg-purple-950/40"
                  : "border-transparent bg-transparent hover:bg-gray-50 dark:hover:bg-gray-700/60"
              } ${
                isSelected
                  ? "ring-2 ring-red-400 dark:ring-red-500"
                  : ""
              }`}
            >
              <div className="flex items-start gap-2">
                {multiSelectMode && (
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => toggleChatSelection(chatId)}
                    className="mt-1 h-4 w-4 shrink-0 rounded border-gray-300 text-purple-600 focus:ring-purple-500 dark:border-gray-600 dark:bg-gray-900"
                    aria-label={`Select ${chatName}`}
                  />
                )}

                <button
                  type="button"
                  onClick={() => onSelectChat(chatId)}
                  className="min-w-0 flex-1 text-left"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h2 className="m-0 overflow-hidden text-ellipsis whitespace-nowrap text-sm font-semibold text-gray-900 dark:text-white">
                      {chatName}
                    </h2>

                    <span className="shrink-0 text-xs text-gray-500 dark:text-gray-400">
                      {updatedAt}
                    </span>
                  </div>

                  <p className="mt-1 overflow-hidden text-ellipsis whitespace-nowrap text-xs text-gray-600 dark:text-gray-300">
                    {chatPreview}
                  </p>
                </button>
              </div>

              <div className="mt-2 flex items-center justify-between gap-2">
                <div className="inline-flex rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600 dark:bg-gray-700 dark:text-gray-300">
                  {relevantFilesCount} documents
                </div>

                {!multiSelectMode && (
                  <button
                    type="button"
                    className="rounded-md px-2 py-1 text-xs font-medium text-red-600 opacity-100 transition-colors hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/40 lg:opacity-0 lg:group-hover:opacity-100"
                    onClick={() => deleteChat([chatId])}
                    aria-label={`Delete ${chatName}`}
                  >
                    Delete
                  </button>
                )}
              </div>
            </div>
          );
        })}

        {filteredChats.length === 0 && (
          <p className="px-2 py-3 text-sm text-gray-500 dark:text-gray-400">
            {searchQuery ? "No chats match your search." : "No chats yet."}
          </p>
        )}
      </div>
    </aside>
  );
}