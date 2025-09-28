const FileTable = ({ title, files, renderFileRow, onRefresh, onGetStatus }) => (
    <section className="mb-12">
        <div className="mb-4 font-semibold text-lg text-indigo-600">{title}</div>
        <div className="overflow-auto rounded-md border border-gray-200 shadow-sm">
            <table className="w-full text-sm table-auto bg-white">
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
                    {files.map((f, i) => renderFileRow(f, i))}
                </tbody>
            </table>
        </div>
        {(onRefresh || onGetStatus) && (
            <div className="mt-4 flex gap-3">
                {onRefresh && (
                    <button
                        className="px-5 py-3 bg-white border border-indigo-600 rounded-lg text-indigo-600 font-semibold shadow hover:bg-indigo-50 transition"
                        onClick={onRefresh}
                    >
                        Refresh
                    </button>
                )}
                {onGetStatus && (
                    <button
                        className="px-5 py-3 bg-white border border-indigo-600 rounded-lg text-indigo-600 font-semibold shadow hover:bg-indigo-50 transition"
                        onClick={onGetStatus}
                    >
                        Get Status
                    </button>
                )}
            </div>
        )}
    </section>
);

export default FileTable;
