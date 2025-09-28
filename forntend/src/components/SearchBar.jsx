const SearchBar = ({ query, setQuery, doSearch, loading, setSearchResults, setError }) => (
    <form onSubmit={doSearch} className="flex gap-4 mb-8">
        <input
            className="flex-1 border border-gray-300 rounded-lg p-3 shadow-sm
                 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
            value={query}
            placeholder="Search filenames (min 2 chars)"
            onChange={(e) => setQuery(e.target.value)}
        />
        <button
            className="px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 transition disabled:opacity-50"
            disabled={loading}
        >
            Search
        </button>
        <button
            type="button"
            className="px-6 py-3 border border-indigo-600 rounded-lg font-semibold text-indigo-600 hover:bg-indigo-50 transition"
            onClick={() => {
                setQuery("");
                setSearchResults([]);
                setError(null);
            }}
        >
            Clear
        </button>
    </form>
);

export default SearchBar;
