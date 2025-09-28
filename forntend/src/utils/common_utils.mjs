/**
 * Remove leading '../' segments from a file path string.
 * @param {string} path - The original file path
 * @returns {string} Cleaned path without leading '../'
 */
export const cleanPath = (path) => path.replace(/^(\.\.\/)+/, "");

/**
 * Convert bytes to a human-readable string with appropriate units.
 * 
 * @param {number|string} bytes - The size in bytes
 * @param {number} decimals - Number of decimal places to show (default 2)
 * @returns {string} Formatted size with unit (e.g., '1.23 MB')
 */
export const formatBytes = (bytes, decimals = 2) => {
    if (bytes === 0 || bytes === "0") return "0 Bytes";
    if (typeof bytes === "string") bytes = parseInt(bytes, 10);
    if (isNaN(bytes) || bytes < 0) return "Invalid size";

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
};
