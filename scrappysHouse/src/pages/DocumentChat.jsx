import { useMemo, useState } from "react";
import { useAuth } from "../auth/AuthProvider";
import ChatComposer from "../components/documentChat/ChatComposer";
import ChatPanelHeader from "../components/documentChat/ChatPanelHeader";
import ChatSidebar from "../components/documentChat/ChatSidebar";
import ChatThread from "../components/documentChat/ChatThread";

const chats = [
  {
    id: "policy-review",
    title: "Policy Review",
    documentCount: 4,
    updatedAt: "Today",
    preview: "Summarize the retention policy changes.",
  },
  {
    id: "q4-reports",
    title: "Q4 Reports",
    documentCount: 7,
    updatedAt: "Yesterday",
    preview: "Compare revenue notes across the uploaded PDFs.",
  },
  {
    id: "onboarding-docs",
    title: "Onboarding Docs",
    documentCount: 3,
    updatedAt: "May 14",
    preview: "Find the checklist for new engineering hires.",
  },
];

const chatMessages = {
  "policy-review": [
    {
      id: 1,
      role: "assistant",
      content:
        "Upload or select documents for this chat, then ask a focused question. I will answer using the retrieved document context.",
      sources: ["Getting started"],
    },
    {
      id: 2,
      role: "user",
      content: "What changed in the latest retention policy draft?",
    },
    {
      id: 3,
      role: "assistant",
      content:
        "The draft extends default retention for archived project records, adds a legal-hold exception, and clarifies who can approve early deletion requests.",
      sources: ["retention-policy-v3.pdf", "legal-hold-addendum.docx"],
    },
  ],
  "q4-reports": [
    {
      id: 1,
      role: "assistant",
      content:
        "I found several uploaded quarterly reports. Ask for a summary, comparison, or a specific citation across those files.",
      sources: ["q4-board-pack.pdf", "finance-summary.xlsx"],
    },
  ],
  "onboarding-docs": [
    {
      id: 1,
      role: "assistant",
      content:
        "This chat is ready to answer questions from the onboarding document set.",
      sources: ["engineering-onboarding.pdf"],
    },
  ],
};

export default function DocumentChat() {
  const { user } = useAuth();
  const [activeChatId, setActiveChatId] = useState(chats[0].id);
  const [draftMessage, setDraftMessage] = useState("");

  const activeChat = useMemo(
    () => chats.find((chat) => chat.id === activeChatId) ?? chats[0],
    [activeChatId]
  );

  const messages = chatMessages[activeChat.id] ?? [];

  const handleSubmit = (event) => {
    event.preventDefault();
    setDraftMessage("");
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-purple-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-7xl flex-col gap-4 px-4 py-6 lg:flex-row lg:gap-6 lg:py-8">
        <ChatSidebar
          chats={chats}
          activeChatId={activeChat.id}
          onSelectChat={setActiveChatId}
        />

        <section className="flex min-h-[680px] flex-1 flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white/90 shadow-xl dark:border-gray-700 dark:bg-gray-800/90">
          <ChatPanelHeader chat={activeChat} />
          <ChatThread
            messages={messages}
            username={user?.username ?? "your account"}
          />
          <ChatComposer
            value={draftMessage}
            onChange={setDraftMessage}
            onSubmit={handleSubmit}
          />
        </section>
      </div>
    </div>
  );
}
