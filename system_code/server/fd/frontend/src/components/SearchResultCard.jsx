import React from 'react';

/**
 * Search Result Card Component
 * Used to display structured data in search results
 */
const SearchResultCard = ({ result }) => {
  // Parse content field
  const parseContent = () => {
    // Check if content field exists
    if (!result.content) return null;
    
    // Process content field, check if it starts with text:
    if (typeof result.content === 'string' && result.content.startsWith('text:')) {
      return result.content.substring(5); // Remove 'text:' prefix
    }
    
    return result.content;
  };
  
  // Extract text content from table_chunk_fields
  const getTextFromFields = () => {
    if (!result.table_chunk_fields || !Array.isArray(result.table_chunk_fields)) {
      return null;
    }
    
    // Find text field
    const textField = result.table_chunk_fields.find(field => 
      field.field_name === 'text' || field.field_name === 'review_text'
    );
    
    return textField ? textField.field_value : null;
  };
  
  // Priority for display text:
  // 1. Use result.text directly if available
  // 2. Use text field from table_chunk_fields if available
  // 3. Parse and use content field if available
  const displayText = result.text || getTextFromFields() || parseContent();
  
  // Get review ID
  const getReviewId = () => {
    if (!result.table_chunk_fields || !Array.isArray(result.table_chunk_fields)) {
      return result.id || result.point_id || null;
    }
    
    const idField = result.table_chunk_fields.find(field => 
      field.field_name === 'review_id'
    );
    
    return idField ? idField.field_value : (result.id || result.point_id || null);
  };
  
  const reviewId = getReviewId();
  
  return (
    <div className="card bg-white rounded-xl p-5 shadow-sm hover:shadow-md transition-all duration-300 transform hover:scale-[1.01] border border-gray-100">
      <div className="flex justify-between">
        <div className="flex-grow">
          {displayText ? (
            <p className="text-gray-700 whitespace-pre-line">{displayText}</p>
          ) : (
            <p className="text-gray-500 italic">No content to display</p>
          )}
          
          {reviewId && (
            <div className="mt-2 text-xs text-gray-500">
              ID: {reviewId}
            </div>
          )}
        </div>
        {result.score > 0 && (
          <div className="ml-4 text-sm bg-indigo-50 text-indigo-700 px-2 py-1 rounded-full h-fit">
            Relevance: {result.score.toFixed(2)}
          </div>
        )}
      </div>
      
      {/* If there are other structured fields, display them */}
      {result.table_chunk_fields && result.table_chunk_fields.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <details className="text-sm">
            <summary className="text-indigo-600 cursor-pointer hover:text-indigo-800 font-medium">
              View more field information
            </summary>
            <div className="mt-2 grid grid-cols-1 gap-2">
              {result.table_chunk_fields
                .filter(field => field.field_name !== 'text' && field.field_name !== 'review_text')
                .map((field, index) => (
                  <div key={index} className="flex">
                    <span className="font-medium text-gray-700 mr-2">{field.field_name}:</span>
                    <span className="text-gray-600">{field.field_value}</span>
                  </div>
                ))}
            </div>
          </details>
        </div>
      )}
      
      {/* Display document information */}
      {result.doc_info && (
        <div className="mt-2 text-xs text-gray-500">
        </div>
      )}
    </div>
  );
};

export default SearchResultCard;