import React, { useState } from 'react';
import axios from 'axios';
import SearchResultCard from '../components/SearchResultCard';

const Search = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [useDeepSearch, setUseDeepSearch] = useState(false);
  const [resultLimit, setResultLimit] = useState(10);

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Determine whether to use regular search or deep search based on user selection
      const endpoint = useDeepSearch ? '/api/deep_search' : '/api/search';
      const response = await axios.post(endpoint, { 
        query,
        limit: resultLimit 
      });
      setResults(response.data.data);
    } catch (err) {
      console.error('Search error:', err);
      setError(err.response?.data?.error || 'An error occurred during search');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <h1 className="page-title">Review Search</h1>
      
      <div className="card bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow duration-300">
        <form onSubmit={handleSearch} className="space-y-4">
          <div>
            <label htmlFor="search-query" className="block text-sm font-medium text-gray-700 mb-2 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              Search Keywords
            </label>
            <div className="flex">
              <input
                id="search-query"
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter search keywords..."
                className="input flex-grow focus:ring-indigo-500 focus:border-indigo-500"
              />
              <button 
                type="submit" 
                className="btn btn-primary ml-2 px-4 py-2 rounded-lg transition-all duration-300 transform hover:scale-105"
                disabled={loading}
                style={{ position: 'relative', zIndex: 10 }}
              >
                {loading ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Searching...
                  </span>
                ) : 'Search'}
              </button>
            </div>
          </div>
          
          <div className="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-6">
            {/* Deep Search Toggle Switch */}
            <div className="flex items-center">
              <label htmlFor="deep-search" className="mr-2 text-sm font-medium text-gray-700 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                Deep Search
              </label>
              <div className="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in">
                <input 
                  type="checkbox" 
                  name="deep-search" 
                  id="deep-search" 
                  checked={useDeepSearch}
                  onChange={() => setUseDeepSearch(!useDeepSearch)}
                  className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"
                />
                <label 
                  htmlFor="deep-search" 
                  className={`toggle-label block overflow-hidden h-6 rounded-full cursor-pointer ${useDeepSearch ? 'bg-indigo-500' : 'bg-gray-300'}`}
                ></label>
              </div>
              <span className="text-xs text-gray-500">{useDeepSearch ? 'Enabled' : 'Disabled'}</span>
            </div>
            
            {/* Result Count Limit Slider */}
            <div className="flex-grow">
              <label htmlFor="result-limit" className="block text-sm font-medium text-gray-700 flex items-center mb-1">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                </svg>
                Result Count: {resultLimit}
              </label>
              <input
                type="range"
                id="result-limit"
                min="1"
                max="30"
                value={resultLimit}
                onChange={(e) => setResultLimit(parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>1</span>
                <span>15</span>
                <span>30</span>
              </div>
            </div>
          </div>
          {error && (
            <div className="text-red-500 text-sm">{error}</div>
          )}
        </form>
      </div>
      
      {loading ? (
        <div className="flex justify-center items-center h-32 bg-gray-50 rounded-lg animate-pulse">
          <div className="text-xl text-gray-400 flex items-center">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Searching...
          </div>
        </div>
      ) : results.length > 0 ? (
        <div className="space-y-4 fade-in">
          <h2 className="text-xl font-semibold text-gray-800 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Search Results
          </h2>
          <div className="space-y-4">
            {results.map((result, index) => (
              <div key={index} style={{animationDelay: `${index * 0.05}s`}}>
                <SearchResultCard result={result} />
              </div>
            ))}
          </div>
        </div>
      ) : query && !loading ? (
        <div className="text-center py-12 text-gray-500 bg-gray-50 rounded-xl border border-gray-200 fade-in">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          No matching results found. Please try different keywords.
        </div>
      ) : null}
    </div>
  );
};

export default Search;