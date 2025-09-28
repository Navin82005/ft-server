import React, { useState, useEffect, useRef } from "react";
import Header from "./components/Header";
import SearchBar from "./components/SearchBar";
import SearchResults from "./components/SearchResults";
import FileTable from "./components/FileTable";
import UploadForm from "./components/UploadForm";
import Footer from "./components/Footer";

import {
  fetchStatus,
  fetchFiles,
  fetchUploadedFiles,
  searchFiles,
  uploadFiles,
  downloadFileByPath
} from "./service/api.mjs";
import { cleanPath } from "./utils/common_utils.mjs";

/**
 * Main App component for the File Server Dashboard.
 * 
 * Manages global state, handlers for fetching status, files, searches,
 * file uploads, and coordinating UI behavior.
 * 
 * @component
 * @returns {JSX.Element} The rendered file server dashboard UI
 */
const App = () => {
  const [status, setStatus] = useState(null);
  const [files, setFiles] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [choices, setChoices] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef();

  useEffect(() => {
    fetchFiles();
    fetchUploadedFiles();
    const id = setInterval(() => fetchStatus(), 10000);
    return () => clearInterval(id);
  }, []);


  const onFetchFiles = async () => {
    setLoading(true);
    try {
      const files = await fetchFiles();
      setFiles(files);
    } catch (error) {
      setError(`Files error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };


  const onFetchUploadedFiles = async () => {
    try {
      const uploaded = await fetchUploadedFiles();
      setUploadedFiles(uploaded);
    } catch (error) {
      console.warn("uploaded-files error", error.message);
    }
  };

  const onDoSearch = async (e) => {
    e && e.preventDefault();
    setSearchResults([]);
    setChoices(null);
    if (!query || query.trim().length < 2) {
      setError("Please enter at least 2 characters to search");
      return;
    }
    setLoading(true);
    try {
      const { status: resStatus, body } = await searchFiles(query);
      if (resStatus === 300) {
        setChoices(body.choices || []);
        setError(null);
        return;
      }
      if (resStatus >= 400) throw new Error(body.error || JSON.stringify(body));
      setSearchResults(body.results || []);
      setError(null);
    } catch (error) {
      setError(`Search error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const onHandleUpload = async (e) => {
    e.preventDefault();
    const files = fileInputRef.current.files;
    if (!files || files.length === 0) {
      setError("No files selected for upload");
      return;
    }
    setError(null);

    const form = new FormData();
    for (const f of files) form.append("file", f);

    setLoading(true);
    try {
      const body = await uploadFiles(form);
      setMessage(body.message || "Upload successful");
      await onFetchUploadedFiles();
      fileInputRef.current.value = null;
    } catch (error) {
      setError(`Upload failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const onDownloadByPath = async (relPath) => {
    try {
      const { blob, filename } = await downloadFileByPath(relPath);

      // Create a local URL of the file blob
      const url = window.URL.createObjectURL(new Blob([blob]));

      // Create a temporary anchor element to trigger download
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename); // Set the file name
      document.body.appendChild(link);
      link.click();

      // Cleanup
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Download failed:", error);
      // Optionally show error UI
    }
  };

  const renderFileRow = (f, index) => (
    <tr key={`${f.name}-${index}`} className="odd:bg-gray-50 hover:bg-indigo-50 transition">
      <td className="px-4 py-3 truncate max-w-xs">{f.name}</td>
      <td className="px-4 py-3">{f.size}</td>
      <td className="px-4 py-3 truncate max-w-xs">{cleanPath(f.path)}</td>
      <td className="px-4 py-3">{f.modified || "-"}</td>
      <td className="px-4 py-3">
        <button
          className="px-3 py-1 rounded-md bg-indigo-600 text-white text-sm font-semibold shadow hover:bg-indigo-700 transition"
          onClick={() => onDownloadByPath(f.path)}
        >
          Download
        </button>
      </td>
    </tr>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br w-screen from-indigo-50 via-white to-pink-50 p-8 font-sans text-gray-900">
      <div className="max-w-6xl mx-auto bg-white rounded-lg shadow-lg p-8">
        <Header status={status} />
        <SearchBar
          query={query}
          setQuery={setQuery}
          doSearch={onDoSearch}
          loading={loading}
          setSearchResults={setSearchResults}
          setError={setError}
        />
        <SearchResults
          error={error}
          choices={choices}
          searchResults={searchResults}
          downloadByPath={onDownloadByPath}
        />
        <UploadForm
          fileInputRef={fileInputRef}
          handleUpload={onHandleUpload}
          loading={loading}
          message={message}
          setMessage={setMessage}
        />
        <FileTable
          title="Recently indexed files"
          files={files}
          renderFileRow={renderFileRow}
          onRefresh={onFetchFiles}
        />
        <FileTable
          title="Uploaded files"
          files={uploadedFiles}
          renderFileRow={renderFileRow}
        />
        <Footer apiBase={"http://localhost:8080"} />
      </div>
    </div>
  );
};

export default App;
