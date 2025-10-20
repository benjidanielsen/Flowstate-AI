import React from 'react';

interface HighlightTextProps {
  text: string;
  highlight: string;
  className?: string;
}

/**
 * Component that highlights search terms within text
 * @param text - The full text to display
 * @param highlight - The term to highlight
 * @param className - Optional CSS classes for the text
 */
const HighlightText: React.FC<HighlightTextProps> = ({ text, highlight, className = '' }) => {
  if (!highlight.trim()) {
    return <span className={className}>{text}</span>;
  }

  // Escape special regex characters in the highlight term
  const escapedHighlight = highlight.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  
  // Create regex to find all occurrences (case-insensitive)
  const regex = new RegExp(`(${escapedHighlight})`, 'gi');
  
  // Split text by the highlight term
  const parts = text.split(regex);

  return (
    <span className={className}>
      {parts.map((part, index) => {
        // Check if this part matches the highlight term (case-insensitive)
        if (part.toLowerCase() === highlight.toLowerCase()) {
          return (
            <mark
              key={index}
              className="bg-yellow-200 text-gray-900 font-semibold px-0.5 rounded"
            >
              {part}
            </mark>
          );
        }
        return <React.Fragment key={index}>{part}</React.Fragment>;
      })}
    </span>
  );
};

export default HighlightText;
