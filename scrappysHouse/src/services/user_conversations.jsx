import { api } from "./api";


export const getUserConversations = async () => {
  try {
    const params = {
      get_messages: false,
    }
    const response = await api.get(`/api/v1/conversations`, { params });
    return response.data;
  } catch (error) {
    console.error("Error fetching user conversations:", error);
    throw error;
  }
};

export const createConversation = async (conversationData) => {
  try {
    const response = await api.post("/api/v1/conversations", conversationData);
    return response.data;
  } catch (error) {
    console.error("Error creating conversation:", error);
    throw error;
  };
}

export const sendMessage = async (conversationId, messageData) => {
  try {
    const response = await api.post(`/api/v1/conversations/${conversationId}/messages`, messageData);
    return response.data;
  } catch (error) {
    console.error("Error sending message:", error);
    throw error;
  }
}

export const deleteConversations = async (conversationIds) => {
  try {
    const deletePromises = conversationIds.map((id) =>
      api.delete(`/api/v1/conversations/${id}`)
    );
    await Promise.all(deletePromises);
  } catch (error) {
    console.error("Error deleting conversations:", error);
    throw error;
  }
}