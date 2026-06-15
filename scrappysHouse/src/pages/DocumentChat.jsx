import { useMemo, useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";
import { getUserConversations, getConversationMessages, createConversation, deleteConversations, sendMessage } from "../services/user_conversations";
import ChatComposer from "../components/documentChat/ChatComposer";
import ChatPanelHeader from "../components/documentChat/ChatPanelHeader";
import ChatSidebar from "../components/documentChat/ChatSidebar";
import ChatThread from "../components/documentChat/ChatThread";

const createOptimisticMessage = ({ messageText, senderIsAgent, isLoading = false }) => ({
  id: `optimistic-${Date.now()}-${Math.random()}`,
  user_conversation_id: 0,
  message_text: messageText,
  sender_is_agent: senderIsAgent,
  llm_message_id: null,
  created_at: new Date().toISOString(),
  is_loading: isLoading,
});

export default function DocumentChat() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { conversationId } = useParams();

  const [userChats, setUserChats] = useState([]);
  const [draftMessage, setDraftMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [multipleSelectedChatIds, setMultipleSelectedChatIds] = useState([]);
  const [multiSelectMode, setMultiSelectMode] = useState(false);
  const activeChatId = conversationId && conversationId !== "new" ? conversationId : null;

  const handleChatReset = () => {
    setMessages([]);
    navigate(`/chat/new`);
  }

  const loadUserConversations = async () => {
    try {
      const conversations = await getUserConversations();

      const safeConversations = Array.isArray(conversations)
        ? conversations
        : [];

      setUserChats(safeConversations);
      if (conversationId && conversationId !== "new") {
        const conversationMessages = await getConversationMessages(conversationId);
        setMessages(conversationMessages);
      } else {
        setMessages([]);
      }
    } catch (error) {
      console.error("Failed to load user conversations:", error);
      setUserChats([]);
    }
  };

  useEffect(() => {
    loadUserConversations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [conversationId]);

  // TODO: add websocket or polling to sync chats in real-time
  const handleConversionSync = async () => {
    await loadUserConversations();
  };

  const activeChat = useMemo(() => {
    if (userChats.length === 0) {
      return null;
    }

    return (
      userChats.find((chat) => chat.conversation_id === activeChatId)
      // userChats[0]
    );
  }, [userChats, activeChatId]);

  const handleNewMessage = async (message) => {
    const trimmedMessage = message.trim();

    if (!trimmedMessage) {
      return;
    }

    const optimisticUserMessage = createOptimisticMessage({
      messageText: trimmedMessage,
      senderIsAgent: false,
    });
    const optimisticAgentMessage = createOptimisticMessage({
      messageText: "",
      senderIsAgent: true,
      isLoading: true,
    });

    setDraftMessage("");
    setMessages((previousMessages) => [
      ...previousMessages,
      optimisticUserMessage,
      optimisticAgentMessage,
    ]);

    if (!activeChatId) {
      try {
        const data = await createConversation({
          user_message: { message_text: trimmedMessage, sender_is_agent: false },
          relevant_file_ids: [],
        });

        setUserChats((previousChats) => [
          data,
          ...previousChats.filter(
            (chat) => chat.conversation_id !== data.conversation_id
          ),
        ]);
        setMessages(data.conversation_messages ?? []);
        navigate(`/chat/${data.conversation_id}`, { replace: true });
      } catch (error) {
        console.error("Failed to send message:", error);
        setMessages((previousMessages) =>
          previousMessages.map((message) =>
            message.id === optimisticAgentMessage.id
              ? {
                  ...message,
                  message_text: "Failed to get a response.",
                  is_loading: false,
                }
              : message
          )
        );
      }
    } else {
      try {
        const createdMessage = await sendMessage(activeChatId, {
          message_text: trimmedMessage,
          sender_is_agent: false,
        });

        setMessages((previousMessages) =>
          previousMessages.map((message) =>
            message.id === optimisticAgentMessage.id ? createdMessage : message
          )
        );
        await handleConversionSync();
      } catch (error) {
        console.error("Failed to send message:", error);
        setMessages((previousMessages) =>
          previousMessages.map((message) =>
            message.id === optimisticAgentMessage.id
              ? {
                  ...message,
                  message_text: "Failed to get a response.",
                  is_loading: false,
                }
              : message
          )
        );
      }
    }
  }

  const handleSubmit = (event) => {
    event.preventDefault();
    handleNewMessage(draftMessage);
  };

  const newChat = () => {
    if (!user) {
      console.warn("No user found, cannot create new chat");
      navigate("/login");
      return false;
    }

    handleChatReset();

    return true;
  }

  const deleteChat = (conversationIds) => {

    for (const conversationId of conversationIds) {
      const index = userChats.findIndex(
        (chat) => chat.conversation_id === conversationId
      );
      if (index !== -1) {
        userChats.splice(index, 1);
        setUserChats([...userChats]);
      }
    }
    deleteConversations(conversationIds).then(() => {
      handleChatReset();
    }).catch((error) => {
      console.error("Failed to delete conversations:", error);
    });
  };

  const handleSelectChat = async (conversationId) => {
    navigate(`/chat/${conversationId}`);
    const conversationMessages = await getConversationMessages(conversationId);
    setMessages(conversationMessages);
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-purple-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-7xl flex-col gap-4 px-4 py-6 lg:flex-row lg:gap-6 lg:py-8">
        <ChatSidebar
          chats={userChats}
          activeChatId={activeChat?.conversation_id ?? null}
          onSelectChat={handleSelectChat}
          newChat={newChat}
          deleteChat={deleteChat}
          setMultipleSelectedChatIds={setMultipleSelectedChatIds}
          multipleSelectedChatIds={multipleSelectedChatIds}
          multiSelectMode={multiSelectMode}
          setMultiSelectMode={setMultiSelectMode}
        />

        <section className="flex h-[calc(100vh-7rem)] min-h-[520px] flex-1 flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white/90 shadow-xl dark:border-gray-700 dark:bg-gray-800/90 lg:h-[calc(100vh-8rem)]">
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