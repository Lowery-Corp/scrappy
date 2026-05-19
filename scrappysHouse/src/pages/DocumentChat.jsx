import { useMemo, useState, useEffect } from "react";
import { useAuth } from "../auth/AuthProvider";
import { getUserConversations } from "../services/user_conversations";
import ChatComposer from "../components/documentChat/ChatComposer";
import ChatPanelHeader from "../components/documentChat/ChatPanelHeader";
import ChatSidebar from "../components/documentChat/ChatSidebar";
import ChatThread from "../components/documentChat/ChatThread";

export default function DocumentChat() {
  const { user } = useAuth();

  const [userChats, setUserChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [draftMessage, setDraftMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const loadUserConversations = async () => {
    try {
      setIsLoading(true);

      const conversations = await getUserConversations();
      console.log("Loaded user conversations:", conversations);

      const safeConversations = Array.isArray(conversations)
        ? conversations
        : [];

      setUserChats(safeConversations);

      setActiveChatId((currentActiveChatId) => {
        if (currentActiveChatId) {
          const stillExists = safeConversations.some(
            (chat) => chat.conversation_id === currentActiveChatId
          );

          if (stillExists) {
            return currentActiveChatId;
          }
        }

        return safeConversations.length > 0
          ? safeConversations[0].conversation_id
          : null;
      });
    } catch (error) {
      console.error("Failed to load user conversations:", error);
      setUserChats([]);
      setActiveChatId(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadUserConversations();
  }, []);

  const handleChatSync = async () => {
    await loadUserConversations();
  };

  const activeChat = useMemo(() => {
    if (userChats.length === 0) {
      return null;
    }

    return (
      userChats.find((chat) => chat.conversation_id === activeChatId) ??
      userChats[0]
    );
  }, [userChats, activeChatId]);

  const handleSubmit = (event) => {
    event.preventDefault();
    setDraftMessage("");
  };

  console.log("Rendering DocumentChat with activeChat:", activeChat);

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-purple-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-7xl flex-col gap-4 px-4 py-6 lg:flex-row lg:gap-6 lg:py-8">
        <ChatSidebar
          chats={userChats}
          activeChatId={activeChat?.conversation_id ?? null}
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