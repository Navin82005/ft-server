import React, { useState } from "react";

/**
 * UploadForm component for multiple file uploads via drag & drop or file picker.
 *
 * @param {object} props
 * @param {React.RefObject} props.fileInputRef - ref to the hidden file input element
 * @param {function} props.handleUpload - upload submit handler
 * @param {boolean} props.loading - disables inputs during upload
 * @param {string|null} props.message - success message display
 * @param {function} props.setMessage - setter for success messages
 */
const UploadForm = ({ fileInputRef, handleUpload, loading, message, setMessage }) => {
    const [dragActive, setDragActive] = useState(false);
    const [selectedFiles, setSelectedFiles] = useState([]);

    const onDragEnter = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(true);
    };
    const onDragLeave = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.target === e.currentTarget) setDragActive(false);
    };
    const onDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };
    const onDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            fileInputRef.current.files = e.dataTransfer.files;
            setSelectedFiles(Array.from(e.dataTransfer.files));
            e.dataTransfer.clearData();
        }
    };

    const onFileChange = (e) => {
        if (e.target.files && e.target.files.length > 0) {
            setSelectedFiles(Array.from(e.target.files));
            setMessage(null);
        }
    };

    const fileNamesDisplay = () => {
        if (selectedFiles.length === 0) return "Drag & drop files here or click to select";
        if (selectedFiles.length === 1) return selectedFiles[0].name;
        return `${selectedFiles.length} files selected: ${selectedFiles.map(f => f.name).join(", ")}`;
    };

    return (
        <section className="mb-12">
            <div className="mb-4 font-semibold text-lg text-indigo-600">Upload files</div>
            <form
                onSubmit={handleUpload}
                className="flex flex-wrap gap-4 items-center"
                onDragEnter={onDragEnter}
                onDragOver={onDragOver}
                onDragLeave={onDragLeave}
                onDrop={onDrop}
            >
                <label
                    htmlFor="file-upload"
                    className={`flex-1 flex flex-col items-center justify-center rounded border-2 border-dashed p-6 cursor-pointer 
                        transition ${dragActive ? "border-indigo-600 bg-indigo-50" : "border-gray-300 bg-white"}`}
                >
                    <input
                        id="file-upload"
                        ref={fileInputRef}
                        type="file"
                        multiple
                        className="hidden"
                        onChange={onFileChange}
                    />
                    <span className="text-center text-gray-700 select-text break-words" title={selectedFiles.length ? fileNamesDisplay() : undefined}>
                        {fileNamesDisplay()}
                    </span>
                </label>

                <button
                    className="px-6 py-3 bg-green-600 text-white font-semibold rounded-lg shadow-md hover:bg-green-700 transition disabled:opacity-50"
                    disabled={loading}
                    type="submit"
                >
                    Upload
                </button>
                <button
                    type="button"
                    className="px-6 py-3 border border-green-600 rounded-lg font-semibold text-green-600 hover:bg-green-50 transition"
                    onClick={() => {
                        fileInputRef.current.value = null;
                        setSelectedFiles([]);
                        setMessage(null);
                    }}
                >
                    Reset
                </button>
            </form>
            {message && (
                <div className="mt-4 p-4 border border-green-300 bg-green-100 rounded-md shadow flex items-center gap-2 text-green-800">
                    <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M16.707 6.707a1 1 0 00-1.414-1.414L9 11.586 6.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l7-7z" />
                    </svg>
                    <span>{message}</span>
                </div>
            )}
        </section>
    );
};

export default UploadForm;
