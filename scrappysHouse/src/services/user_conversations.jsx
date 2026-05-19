import { api } from "./api";


export const getUserConversations = async (userId) => {
  try {
    const response = await api.get(`/api/v1/conversations`);
    return response.data.data;
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
