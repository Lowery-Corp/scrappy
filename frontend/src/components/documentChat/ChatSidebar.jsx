import { useMemo, useState } from "react";

const getChatPreview = (chat) => {
  const directPreview =
    chat?.preview ||
    chat?.last_message?.message_text ||
    chat?.latest_message?.message_text ||
    chat?.last_message_text ||
    chat?.latest_message_text;

  if (directPreview?.trim()) {
    return directPreview.trim();
  }

  if (!Array.isArray(chat?.conversation_messages)) {
    return "";
  }

  const latestMessage = [...chat.conversation_messages]
    .reverse()
    .find((message) => message?.message_text?.trim());

  return latestMessage?.message_text.trim() ?? "";
};

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
      const chatPreview = getChatPreview(chat);

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
    <aside className="flex w-full flex-col rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900 lg:h-[calc(100vh-4.25rem)] lg:w-80 lg:shrink-0 lg:rounded-none lg:border-y-0 lg:border-l-0 lg:shadow-none xl:w--[22rem]">
      <div className="border-b border-slate-200 p-4 text-left dark:border-slate-800">
        <div className="flex items-center justify-between gap-2">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-indigo-600 dark:text-indigo-300">
              Document Chat
            </p>
            <h1 className="m-0 text-xl font-bold tracking-tight text-slate-950 dark:text-white">
              Chats
            </h1>
          </div>

          <button
            type="button"
            className="rounded-lg bg-indigo-600 px-2.5 py-1.5 text-xs font-semibold text-white transition hover:bg-indigo-700"
            onClick={() => newChat()}
          >
            New
          </button>
        </div>

        <label className="mt-2 block">
          <span className="sr-only">Search chats</span>
          <input
            type="search"
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
            placeholder="Search chats"
            className="h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:bg-white focus:ring-4 focus:ring-indigo-500/10 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100 dark:focus:bg-slate-950"
          />
        </label>

        {/* Multi-select actions */}
        <div className="mt-2 flex items-center justify-between gap-1.5">
          <button
            type="button"
            className="rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
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
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                className="rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
                onClick={toggleSelectAll}
                disabled={filteredChatIds.length === 0}
              >
                {allFilteredChatsSelected ? "Clear all" : "Select all"}
              </button>

              <button
                type="button"
                disabled={multipleSelectedChatIds.length === 0}
                className="rounded-lg bg-rose-600 px-2.5 py-1.5 text-xs font-semibold text-white transition hover:bg-rose-700 disabled:cursor-not-allowed disabled:bg-rose-300 dark:disabled:bg-rose-900"
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

      <div className="flex gap-1.5 overflow-x-auto p-1.5 lg:min-h-0 lg:flex-1 lg:flex-col lg:overflow-y-auto lg:overflow-x-hidden">
        {filteredChats.map((chat) => {
          const isActive = chat.conversation_id === activeChatId;
          const chatName = chat.conversation_name || "New Chat";
          const chatPreview = getChatPreview(chat) || "No messages yet.";
          const updatedAt = new Date(chat.updated_at).toLocaleString();
          const relevantFilesCount = chat.relevant_file_ids?.length ?? 0;
          const chatId = chat.conversation_id;

          const isSelected = multipleSelectedChatIds.includes(chatId);

          return (
            <div
              key={chatId}
              className={`group min-w-56 rounded-md border px-2 py-1.5 text-left transition-colors lg:min-w-0 ${
                isActive
                  ? "border-indigo-200 bg-indigo-50 shadow-sm dark:border-indigo-800 dark:bg-indigo-950/40"
                  : "border-transparent bg-transparent hover:bg-slate-50 dark:hover:bg-slate-800/60"
              } ${
                isSelected
                  ? "ring-2 ring-red-400 dark:ring-red-500"
                  : ""
              }`}
            >
              <div className="flex items-start gap-1.5">
                {multiSelectMode && (
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => toggleChatSelection(chatId)}
                    className="mt-0.5 h-3.5 w-3.5 shrink-0 rounded border-gray-300 text-purple-600 focus:ring-purple-500 dark:border-gray-600 dark:bg-gray-900"
                    aria-label={`Select ${chatName}`}
                  />
                )}

                <button
                  type="button"
                  onClick={() => onSelectChat(chatId)}
                  className="min-w-0 flex-1 text-left"
                >
                  <div className="flex items-start justify-between gap-1.5">
                    <h2 className="m-0 overflow-hidden text-ellipsis whitespace-nowrap text-[13px] font-semibold text-gray-900 dark:text-white">
                      {chatName}
                    </h2>

                    <span className="shrink-0 text-[10px] leading-4 text-gray-500 dark:text-gray-400">
                      {updatedAt}
                    </span>
                  </div>

                  <p className="mt-0.5 overflow-hidden text-ellipsis whitespace-nowrap text-[11px] text-gray-600 dark:text-gray-300">
                    {chatPreview}
                  </p>
                </button>
              </div>

              <div className="mt-1.5 flex items-center justify-between gap-1.5">
                <div className="inline-flex rounded-full bg-gray-100 px-1.5 py-0.5 text-[10px] font-medium text-gray-600 dark:bg-gray-700 dark:text-gray-300">
                  {relevantFilesCount} documents
                </div>

                {!multiSelectMode && (
                  <button
                    type="button"
                    className="rounded-md px-1.5 py-0.5 text-[11px] font-medium text-red-600 opacity-100 transition-colors hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/40 lg:opacity-0 lg:group-hover:opacity-100"
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
