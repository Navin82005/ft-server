import { apiConfig } from "../config";

const API_BASE = apiConfig.API_BASE;

export const fetchStatus = async () => {
    const res = await fetch(`${API_BASE}/status`);
    const body = await res.json();
    if (!res.ok) throw new Error(body.error || JSON.stringify(body));
    return body;
};

export const fetchFiles = async () => {
    const res = await fetch(`${API_BASE}/files`);
    const body = await res.json();
    if (!res.ok) throw new Error(body.error || JSON.stringify(body));
    return body.files || [];
};

export const fetchUploadedFiles = async () => {
    const res = await fetch(`${API_BASE}/uploaded-files`);
    const body = await res.json();
    if (!res.ok) throw new Error(body.error || JSON.stringify(body));
    return body.files || [];
};

export const searchFiles = async (query) => {
    const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
    const body = await res.json();
    return { status: res.status, body };
};

export const uploadFiles = async (formData) => {
    const res = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        body: formData,
    });
    const body = await res.json();
    if (!res.ok) throw new Error(body.error || JSON.stringify(body));
    return body;
};

export const downloadFileByPath = async (relPath) => {
    const url = `${API_BASE}/download?filepath=${encodeURIComponent(relPath)}`;

    const response = await fetch(url);
    if (!response.ok) throw new Error("Failed to download file");

    const blob = await response.blob();

    return { blob, filename: getFileNameFromPath(relPath) };
};

const getFileNameFromPath = (path) => {
    const segments = path.split("/");
    return segments.length ? segments[segments.length - 1] : "download";
};
