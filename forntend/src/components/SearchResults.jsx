import { cleanPath, formatBytes } from "../utils/common_utils.mjs";

const SearchResults = ({ error, choices, searchResults, downloadByPath }) => (
    <>
        {error && (
            <div className="mb-4 p-4 border border-red-200 bg-red-100 text-red-800 rounded-md shadow flex items-center gap-2">
                <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path d="M10 18a8 8 0 100-16 8 8 0 000 16zm-.25-9.5V6h1.5v2.5h-1.5zM9 8h2v5H9V8zm1 9a1.5 1.5 0 110-3 1.5 1.5 0 010 3z" /></svg>
                <span>{error}</span>
            </div>
        )}
        {choices && (
            <div className="mb-6 p-4 border border-yellow-300 bg-yellow-50 rounded-md shadow">
                <div className="font-semibold text-yellow-800">Multiple files matched — choose one to download</div>
                <ul className="mt-3 list-disc list-inside space-y-1">
                    {choices.map((c, i) => (
                        <li key={i} className="truncate">
                            <button
                                className="text-indigo-600 underline hover:text-indigo-800 transition"
                                onClick={() => downloadByPath(c)}
                            >
                                {c}
                            </button>
                        </li>
                    ))}
                </ul>
            </div>
        )}
        {searchResults.length > 0 && (
            <div className="mb-8 border rounded-md p-6 bg-white shadow-lg">
                <div className="font-semibold mb-4 text-indigo-700">Search results ({searchResults.length})</div>
                <div className="overflow-visible rounded-md border border-gray-200">
                    <table className="w-full text-sm table-auto">
                        <thead className="bg-indigo-100 text-indigo-700 text-left text-xs font-semibold">
                            <tr>
                                <th className="px-4 py-3">Name</th>
                                <th className="px-4 py-3">Size</th>
                                <th className="px-4 py-3">Path</th>
                                <th className="px-4 py-3">Modified</th>
                                <th className="px-4 py-3">Action</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {searchResults.map((r, i) => (
                                <tr key={`${r.name}-${i}`} className="hover:bg-indigo-50 transition">
                                    <td className="px-4 py-3 truncate max-w-xs">{r.name}</td>
                                    <td className="px-4 py-3">{formatBytes(r.size)}</td>
                                    <td className="px-4 py-3 max-w-xs relative group">
                                        <span className="truncate block cursor-pointer">
                                            {cleanPath(r.path)}
                                        </span>

                                        {/* Enhanced Tooltip */}
                                        <div
                                            className="
                                                absolute left-1/2 transform -translate-x-1/2 bottom-full mb-3 w-max max-w-xs rounded-lg bg-gray-900 bg-opacity-90 
                                                px-3 py-2 text-sm text-white font-medium shadow-lg whitespace-normal
                                                opacity-0 translate-y-2 group-hover:opacity-100 group-hover:translate-y-0 
                                                pointer-events-none transition-all duration-300 ease-in-out select-text
                                                backdrop-blur-sm
                                                text-wrap
                                                z-100
                                            "
                                        >
                                            {r.path}
                                            {/* Arrow pointer */}
                                            <div
                                                className="
                                                    absolute top-full left-1/2 transform -translate-x-1/2 w-3 h-3 bg-gray-900 bg-opacity-90 rotate-45
                                                    shadow-lg
                                                "
                                                style={{ filter: "drop-shadow(0 1px 1px rgba(0,0,0,0.15))" }}
                                            />
                                        </div>
                                    </td>
                                    <td className="px-4 py-3">{r.modified || "-"}</td>
                                    <td className="px-4 py-3">
                                        <button
                                            className="px-3 py-1 rounded-md bg-indigo-600 text-white text-sm font-semibold shadow hover:bg-indigo-700 transition"
                                            onClick={() => downloadByPath(r.path)}
                                        >
                                            Download
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        )}
    </>
);

export default SearchResults;
