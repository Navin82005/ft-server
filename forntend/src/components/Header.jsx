const Header = ({ status }) => (
    <header className="flex items-center justify-between mb-8">
        <h1 className="text-4xl font-extrabold text-indigo-600 tracking-tight">File Server Dashboard</h1>
        <div className="text-sm text-gray-600">
            {/* <div>
                Status:{" "}
                <span className={status?.indexing_complete ? "text-green-600 font-semibold" : "text-yellow-600 font-semibold"}>
                    {status ? (status.indexing_complete ? "Ready" : "Indexing...") : "-"}
                </span>
            </div>
            <div>Files indexed: {status ? status.total_files : "-"}</div> */}
        </div>
    </header>
);

export default Header;
