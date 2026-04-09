import { api } from "./api";

export const getBucketStructure = async () => {
  try {
    const response = await api.get("/api/v1/blob");
    return response.data;
  } catch (error) {
    console.error("Error fetching bucket structure:", error);
    throw error;
  }
};

export const syncBucketStructure = async () => {
  try {
    const response = await api.post("/api/v1/blob/sync");
    return response.data;
  } catch (error) {
    console.error("Error syncing bucket structure:", error);
    throw error;
  }
};

export const uploadFile = async (file, onUploadProgress) => {
  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/api/v1/blob/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress,
    });

    return response.data;
  } catch (error) {
    console.error("Error uploading file:", error);
    throw error;
  }
};