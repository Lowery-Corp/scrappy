const createOptimisticMessage = ({
    messageText,
    senderIsAgent,
    isLoading = false,
}) => ({
    id: `optimistic-${Date.now()}-${Math.random()}`,
    user_conversation_id: 0,
    message_text: messageText,
    sender_is_agent: senderIsAgent,
    llm_message_id: null,
    created_at: new Date().toISOString(),
    is_loading: isLoading,
});

export default createOptimisticMessage;


