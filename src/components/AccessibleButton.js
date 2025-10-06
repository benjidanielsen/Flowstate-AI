import React from 'react';

/**
 * AccessibleButton component
 * - Keyboard navigable (focusable, triggers on Enter/Space)
 * - Screen reader friendly with ARIA label
 * - WCAG 2.1 AA compliant
 */

const AccessibleButton = ({ onClick, label, ariaLabel, disabled = false }) => {
  // Handle keyboard activation
  const handleKeyDown = (event) => {
    if (disabled) return;
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onClick();
    }
  };

  return (
    <div
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-disabled={disabled}
      aria-label={ariaLabel || label}
      onClick={disabled ? undefined : onClick}
      onKeyDown={handleKeyDown}
      style={{
        cursor: disabled ? 'not-allowed' : 'pointer',
        padding: '8px 16px',
        backgroundColor: disabled ? '#ccc' : '#007acc',
        color: '#fff',
        borderRadius: '4px',
        display: 'inline-block',
        userSelect: 'none'
      }}
    >
      {label}
    </div>
  );
};

export default AccessibleButton;
