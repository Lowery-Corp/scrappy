import { useMemo, useRef, useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";
import {
  addFilesToConversation,
  getUserConversations,
  getConversationMessages,
  createConversationStream,
  deleteConversations,
  sendMessageStream,
} from "../services/user_conversations";
import { getUserFiles } from "../services/user_files";
import ChatComposer from "../components/documentChat/ChatComposer";
import ChatPanelHeader from "../components/documentChat/ChatPanelHeader";
import ChatSidebar from "../components/documentChat/ChatSidebar";
import ChatThread from "../components/documentChat/ChatThread";
import ChatFileSelector from "../components/documentChat/ChatFileSelector";
import createOptimisticMessage from "../components/documentChat/OptimisticMessage";
import PopupBanner from "../components/helpers/PopupBanner";

const getMessagePreview = (conversationMessages = []) => {
  if (!Array.isArray(conversationMessages)) {
    return "";
  }

  const latestMessage = [...conversationMessages]
    .reverse()
    .find((message) => message?.message_text?.trim());

  return latestMessage?.message_text.trim() ?? "";
};

const withConversationPreview = (conversation, fallbackPreview = "") => ({
  ...conversation,
  preview:
    conversation?.preview ||
    getMessagePreview(conversation?.conversation_messages) ||
    fallbackPreview,
});

const mergeConversationPreviews = (conversations, previousChats) =>
  conversations.map((conversation) => {
    const previousChat = previousChats.find(
      (chat) => chat.conversation_id === conversation.conversation_id,
    );

    return withConversationPreview(
      {
        ...conversation,
        conversation_messages:
          conversation.conversation_messages ??
          previousChat?.conversation_messages,
      },
      previousChat?.preview,
    );
  });

export default function DocumentChat() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { conversationId } = useParams();

  const [userFiles, setUserFiles] = useState([]);
  const [selectedFileIds, setSelectedFilesIds] = useState([]);
  const [userChats, setUserChats] = useState([]);
  const [draftMessage, setDraftMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [multipleSelectedChatIds, setMultipleSelectedChatIds] = useState([]);
  const [multiSelectMode, setMultiSelectMode] = useState(false);

  const activeChatId =
    conversationId && conversationId !== "new" ? conversationId : null;

  const streamingConversationId = useRef(null);

  const activeChat = useMemo(() => {
    if (!activeChatId || userChats.length === 0) {
      return null;
    }

    return (
      userChats.find((chat) => chat.conversation_id === activeChatId) ?? null
    );
  }, [userChats, activeChatId]);

  const activeChatFileCount = selectedFileIds.length;

  const updateConversationPreview = (
    targetConversationId,
    conversationMessages,
  ) => {
    const preview = getMessagePreview(conversationMessages);

    if (!preview) {
      return;
    }

    setUserChats((previousChats) =>
      previousChats.map((chat) =>
        chat.conversation_id === targetConversationId
          ? {
              ...chat,
              preview,
              conversation_messages: conversationMessages,
            }
          : chat,
      ),
    );
  };

  const handleChatReset = () => {
    setMessages([]);
    setSelectedFilesIds([]);
    navigate("/chat/new");
  };

  const loadUserConversations = async () => {
    try {
      const conversations = await getUserConversations();

      const safeConversations = Array.isArray(conversations)
        ? conversations
        : [];

      setUserChats((previousChats) =>
        mergeConversationPreviews(safeConversations, previousChats),
      );

      if (conversationId && conversationId !== "new") {
        const selectedConversation =
          safeConversations.find(
            (chat) => chat.conversation_id === conversationId,
          ) ?? null;

        setSelectedFilesIds(selectedConversation?.relevant_file_ids ?? []);

        if (streamingConversationId.current === conversationId) {
          return;
        }

        const conversationMessages = await getConversationMessages(
          conversationId,
        );

        setMessages(conversationMessages);
      updateConversationPreview(conversationId, conversationMessages);
      } else {
        setMessages([]);
        setSelectedFilesIds([]);
      }
    } catch (error) {
      console.error("Failed to load user conversations:", error);
      setUserChats([]);
    }
  };

  useEffect(() => {
    let shouldIgnore = false;

    const loadChatPageData = async () => {
      try {
        const [conversations, user_file_data] = await Promise.all([
          getUserConversations(),
          getUserFiles(),
        ]);

        if (shouldIgnore) {
          return;
        }

        const safeConversations = Array.isArray(conversations)
          ? conversations
          : [];

        setUserChats((previousChats) =>
          mergeConversationPreviews(safeConversations, previousChats),
        );
        const userFiles = user_file_data.files
        setUserFiles(Array.isArray(userFiles) ? userFiles : []);

        if (conversationId && conversationId !== "new") {
          if (streamingConversationId.current === conversationId) {
            return;
          }

          const selectedConversation =
            safeConversations.find(
              (chat) => chat.conversation_id === conversationId,
            ) ?? null;
          const conversationMessages = await getConversationMessages(
            conversationId,
          );

          if (shouldIgnore) {
            return;
          }

          setSelectedFilesIds(selectedConversation?.relevant_file_ids ?? []);
          setMessages(conversationMessages);
          updateConversationPreview(conversationId, conversationMessages);
        } else {
          setMessages([]);
          setSelectedFilesIds([]);
        }
      } catch (error) {
        if (shouldIgnore) {
          return;
        }

        console.error("Failed to load chat page data:", error);
        setUserChats([]);
        setUserFiles([]);
      }
    };

    loadChatPageData();

    return () => {
      shouldIgnore = true;
    };
  }, [conversationId]);

  const handleConversionSync = async () => {
    await loadUserConversations();
  };

  const handleNewMessage = async (message) => {
    const trimmedMessage = message.trim();

    // if (selectedFileIds.length < 1){
    //   popupMessage("Please select at least one file before sending a message.", "warning");
    //   return;
    // }

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

    const appendAgentDelta = ({ text }) => {
      setMessages((previousMessages) =>
        previousMessages.map((message) =>
          message.id === optimisticAgentMessage.id
            ? {
                ...message,
                message_text: `${message.message_text}${text}`,
                is_loading: false,
              }
            : message,
        ),
      );
    };

    const replaceAgentMessage = (agentMessage) => {
      setMessages((previousMessages) =>
        previousMessages.map((message) =>
          message.id === optimisticAgentMessage.id ? agentMessage : message,
        ),
      );

      const targetConversationId =
        activeChatId ?? streamingConversationId.current;
      const preview = agentMessage?.message_text?.trim();

      if (targetConversationId && preview) {
        setUserChats((previousChats) =>
          previousChats.map((chat) =>
            chat.conversation_id === targetConversationId
              ? { ...chat, preview }
              : chat,
          ),
        );
      }
    };

    const showAgentError = () => {
      setMessages((previousMessages) =>
        previousMessages.map((message) =>
          message.id === optimisticAgentMessage.id
            ? {
                ...message,
                message_text: "Failed to get a response.",
                is_loading: false,
              }
            : message,
        ),
      );
    };

    setDraftMessage("");
    setMessages((previousMessages) => [
      ...previousMessages,
      optimisticUserMessage,
      optimisticAgentMessage,
    ]);

    if (activeChatId) {
      setUserChats((previousChats) =>
        previousChats.map((chat) =>
          chat.conversation_id === activeChatId
            ? { ...chat, preview: trimmedMessage }
            : chat,
        ),
      );
    }

    if (!activeChatId) {
      try {
        await createConversationStream(
          {
            user_message: {
              message_text: trimmedMessage,
              sender_is_agent: false,
            },
            relevant_file_ids: selectedFileIds,
          },
          {
            conversation: (conversation) => {
              streamingConversationId.current = conversation.conversation_id;

              setUserChats((previousChats) => [
                withConversationPreview(conversation, trimmedMessage),
                ...previousChats.filter(
                  (chat) =>
                    chat.conversation_id !== conversation.conversation_id,
                ),
              ]);

              setMessages([
                ...(conversation.conversation_messages ?? []),
                optimisticAgentMessage,
              ]);

              navigate(`/chat/${conversation.conversation_id}`, {
                replace: true,
              });
            },
            delta: appendAgentDelta,
            message: replaceAgentMessage,
            done: () => {
              streamingConversationId.current = null;
            },
          },
        );
      } catch (error) {
        streamingConversationId.current = null;
        console.error("Failed to send message:", error);
        showAgentError();
      }
    } else {
      try {
        await sendMessageStream(
          activeChatId,
          {
            message_text: trimmedMessage,
            sender_is_agent: false,
          },
          {
            user_message: (createdUserMessage) => {
              setMessages((previousMessages) =>
                previousMessages.map((message) =>
                  message.id === optimisticUserMessage.id
                    ? createdUserMessage
                    : message,
                ),
              );

              const preview = createdUserMessage?.message_text?.trim();

              if (preview) {
                setUserChats((previousChats) =>
                  previousChats.map((chat) =>
                    chat.conversation_id === activeChatId
                      ? { ...chat, preview }
                      : chat,
                  ),
                );
              }
            },
            delta: appendAgentDelta,
            message: replaceAgentMessage,
          },
        );

        await handleConversionSync();
      } catch (error) {
        console.error("Failed to send message:", error);
        showAgentError();
      }
    }
  };

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
  };

  const deleteChat = (conversationIds) => {
    setUserChats((previousChats) =>
      previousChats.filter(
        (chat) => !conversationIds.includes(chat.conversation_id),
      ),
    );

    deleteConversations(conversationIds)
      .then(() => {
        handleChatReset();
      })
      .catch((error) => {
        console.error("Failed to delete conversations:", error);
        loadUserConversations();
      });
  };

  const handleSelectChat = async (conversationId) => {
    const selectedChat =
      userChats.find((chat) => chat.conversation_id === conversationId) ??
      null;

    setSelectedFilesIds(selectedChat?.relevant_file_ids ?? []);

    navigate(`/chat/${conversationId}`);

    try {
      const conversationMessages = await getConversationMessages(conversationId);
      setMessages(conversationMessages);
      updateConversationPreview(conversationId, conversationMessages);
    } catch (error) {
      console.error("Failed to load conversation messages:", error);
      setMessages([]);
    }
  };

  const updateChatFiles = async (conversationId, fileId) => {
    const updatedConversation = await addFilesToConversation(
      conversationId,
      fileId,
    );

    if (updatedConversation?.relevant_file_ids) {
      setUserChats((previousChats) =>
        previousChats.map((chat) =>
          chat.conversation_id === conversationId
            ? {
                ...chat,
                relevant_file_ids: updatedConversation.relevant_file_ids,
              }
            : chat,
        ),
      );

      setSelectedFilesIds(updatedConversation.relevant_file_ids);
    }

    return updatedConversation;
  };

  const handleFileSelect = async (fileId) => {
    if (!activeChatId) {
      setSelectedFilesIds((previousSelectedFileIds) =>
        previousSelectedFileIds.includes(fileId)
          ? previousSelectedFileIds.filter((id) => id !== fileId)
          : [...previousSelectedFileIds, fileId],
      );
      return;
    }

    const previousSelectedFileIds = selectedFileIds;

    const nextSelectedFileIds = previousSelectedFileIds.includes(fileId)
      ? previousSelectedFileIds.filter((id) => id !== fileId)
      : [...previousSelectedFileIds, fileId];

    setSelectedFilesIds(nextSelectedFileIds);

    setUserChats((previousChats) =>
      previousChats.map((chat) =>
        chat.conversation_id === activeChatId
          ? {
              ...chat,
              relevant_file_ids: nextSelectedFileIds,
            }
          : chat,
      ),
    );

    try {
      await updateChatFiles(activeChatId, fileId);
    } catch (error) {
      console.error("Failed to update files on conversation:", error);

      setSelectedFilesIds(previousSelectedFileIds);

      setUserChats((previousChats) =>
        previousChats.map((chat) =>
          chat.conversation_id === activeChatId
            ? {
                ...chat,
                relevant_file_ids: previousSelectedFileIds,
              }
            : chat,
        ),
      );
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-purple-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <PopupBanner />
      <div className="flex min-h-[calc(100vh-4rem)] w-full flex-col gap-2 px-2 py-2 lg:flex-row lg:gap-0 lg:p-0">
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

        <section className="flex h-[calc(100vh-5rem)] min-h-[480px] flex-1 flex-col overflow-hidden rounded-xl border border-gray-200 bg-white/95 shadow-lg dark:border-gray-700 dark:bg-gray-800/95 lg:h-[calc(100vh-4rem)] lg:min-w-0 lg:rounded-none lg:border-y-0 lg:shadow-none">
          <ChatPanelHeader
            chat={activeChat}
            activeChatFileCount={activeChatFileCount}
          />

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

        <ChatFileSelector
          selectedChatId={activeChat?.conversation_id ?? "new"}
          userFiles={userFiles}
          selectedFileIds={selectedFileIds}
          onFileSelect={handleFileSelect}
        />
      </div>
    </div>
  );
}