import { useEffect, useRef } from "react";

export default function ChatThread({ messages, username }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: "end" });
  }, [messages]);

  return (
    <div className="min-h-0 flex-1 space-y-5 overflow-y-auto p-5 text-left">
      <div className="rounded-xl border border-dashed border-purple-300 bg-purple-50/80 p-4 dark:border-purple-800 dark:bg-purple-950/30">
        <p className="text-sm font-semibold text-purple-800 dark:text-purple-200">
          RAG workspace for {username}
        </p>
        <p className="mt-1 text-sm text-purple-700 dark:text-purple-300">
          Ask questions about uploaded files, compare documents, or request cited summaries.
        </p>
      </div>

      {messages.map((message) => {
        const isUser = message.sender_is_agent === false;
        const isLoading = message.is_loading === true;

        return (
          <div
            key={message.id}
            className={`flex ${isUser ? "justify-end" : "justify-start"}`}
          >
            <article
              className={`max-w-3xl rounded-2xl px-5 py-4 shadow-sm ${
                isUser
                  ? "bg-purple-600 text-white"
                  : "border border-gray-200 bg-gray-50 text-gray-800 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100"
              }`}
              aria-live={isLoading ? "polite" : undefined}
            >
              {isLoading ? (
                <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-300">
                  <span className="h-2 w-2 animate-pulse rounded-full bg-purple-500" />
                  <span className="h-2 w-2 animate-pulse rounded-full bg-purple-500 delay-100" />
                  <span className="h-2 w-2 animate-pulse rounded-full bg-purple-500 delay-200" />
                </div>
              ) : (
                <p className="text-sm leading-6">{message.message_text}</p>
              )}
              {!isUser && !isLoading && message.sources?.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {message.sources.map((source) => (
                    <span
                      key={source}
                      className="rounded-full bg-white px-3 py-1 text-xs font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-300"
                    >
                      {source}
                    </span>
                  ))}
                </div>
              )}
            </article>
          </div>
        );
      })}
      <div ref={bottomRef} aria-hidden="true" />
    </div>
  );
}
