import { api } from "./api";

export const loginUser = async (username, password) => {
  try {
    const data = { username, password };
    const response = await api.post("/api/v1/auth/login", data);
    console.log(response);
    return response.data;
  } catch (error) {
    console.error("Error logging in user:", error);
    throw error;
  }
};

export const registerUser = async (username, password) => {
  try {
    const response = await api.post("/api/v1/auth/register", {
      username,
      password,
    });
    return response.data;
  } catch (error) {
    console.error("Error registering user:", error);
    throw error;
  }
};

export const logoutUser = async () => {
  try {
    const response = await api.post("/api/v1/auth/logout");
    return response.data;
  } catch (error) {
    console.error("Error logging out user:", error);
    throw error;
  }
};
