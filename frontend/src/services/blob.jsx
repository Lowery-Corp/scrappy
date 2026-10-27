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

export const createFolder = async (folderPath) => {
  const response = await api.post("/api/v1/blob/folder", null, {
    params: { folder_path: folderPath },
  });
  return response.data;
};

export const renamePath = async (sourcePath, destinationPath, isFolder) => {
  const response = await api.post("/api/v1/blob/rename", null, {
    params: {
      source_path: sourcePath,
      destination_path: destinationPath,
      is_folder: isFolder,
    },
  });
  return response.data;
};
