import { api } from "./api";


const parseStreamEvent = (rawEvent) => {
  const lines = rawEvent.split("\n");
  let event = "message";
  const dataLines = [];

  for (const line of lines) {
    if (line.startsWith("event: ")) {
      event = line.slice(7);
    } else if (line.startsWith("data: ")) {
      dataLines.push(line.slice(6));
    }
  }

  if (dataLines.length === 0) {
    return null;
  }

  return {
    event,
    data: JSON.parse(dataLines.join("\n")),
  };
};

const readConversationStream = async (response, handlers = {}) => {
  if (!response.ok) {
    throw new Error(await response.text());
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("Streaming responses are not supported in this browser.");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";

    for (const rawEvent of events) {
      const parsedEvent = parseStreamEvent(rawEvent);
      if (!parsedEvent) {
        continue;
      }

      const handler = handlers[parsedEvent.event];
      if (handler) {
        handler(parsedEvent.data);
      }

      if (parsedEvent.event === "error") {
        throw new Error(parsedEvent.data.detail ?? "Streaming response failed.");
      }
    }
  }

  if (buffer.trim()) {
    const parsedEvent = parseStreamEvent(buffer);
    const handler = parsedEvent ? handlers[parsedEvent.event] : null;
    if (handler) {
      handler(parsedEvent.data);
    }
  }
};

const postConversationStream = async (path, body, handlers) => {
  const response = await fetch(`${api.defaults.baseURL ?? ""}${path}`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  await readConversationStream(response, handlers);
};


export const getUserConversations = async () => {
  try {
    const response = await api.get(`/api/v1/conversations`);
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

export const getConversationMessages = async (conversationId) => {
  try {
    const response = await api.get(`/api/v1/conversations/${conversationId}/messages`);
    return response.data;
  } catch (error) {
    console.error("Error fetching conversation messages:", error);
    throw error;
  }
}

export const createConversationStream = async (conversationData, handlers) => {
  await postConversationStream("/api/v1/conversations/stream", conversationData, handlers);
};

export const sendMessageStream = async (conversationId, messageData, handlers) => {
  await postConversationStream(
    `/api/v1/conversations/${conversationId}/messages/stream`,
    messageData,
    handlers
  );
};
