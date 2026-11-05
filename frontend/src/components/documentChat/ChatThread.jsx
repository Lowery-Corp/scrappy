import { useEffect, useRef } from "react";
import MarkdownMessage from "./MarkdownMessage";

export default function ChatThread({ messages, username }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: "end" });
  }, [messages]);

  return (
    <div className="min-h-0 flex-1 space-y-4 overflow-y-auto bg-slate-50/70 px-4 py-5 text-left dark:bg-slate-950/40 sm:px-6">
      {messages.length === 0 && (
        <div className="rounded-2xl border border-dashed border-indigo-200 bg-indigo-50/80 px-4 py-3 dark:border-indigo-900 dark:bg-indigo-950/30">
          <p className="text-sm font-semibold text-indigo-900 dark:text-indigo-200">
            RAG workspace for {username}
          </p>
          <p className="mt-1 text-xs leading-5 text-indigo-700 dark:text-indigo-300">
            Ask questions about uploaded files, compare documents, or request cited summaries.
          </p>
        </div>
      )}

      {messages.map((message) => {
        const isUser = message.sender_is_agent === false;
        const isLoading = message.is_loading === true;

        return (
          <div
            key={message.id}
            className={`flex ${isUser ? "justify-end" : "justify-start"}`}
          >
            <article
              className={`max-w-[85%] rounded-2xl px-4 py-3 shadow-sm ${
                isUser
                  ? "bg-indigo-600 text-white shadow-indigo-600/10"
                  : "border border-slate-200 bg-white text-slate-800 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
              }`}
              aria-live={isLoading ? "polite" : undefined}
            >
              {isLoading ? (
                <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-300">
                  <span className="h-2 w-2 animate-pulse rounded-full bg-indigo-500" />
                  <span className="h-2 w-2 animate-pulse rounded-full bg-indigo-500 delay-100" />
                  <span className="h-2 w-2 animate-pulse rounded-full bg-indigo-500 delay-200" />
                </div>
              ) : isUser ? (
                <p className="whitespace-pre-wrap text-sm leading-5">
                  {message.message_text}
                </p>
              ) : (
                <MarkdownMessage text={message.message_text} />
              )}
              {!isUser && !isLoading && message.sources?.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {message.sources.map((source) => (
                    <span
                      key={source}
                      className="rounded-full bg-white px-2 py-0.5 text-xs font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-300"
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
