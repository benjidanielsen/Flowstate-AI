# Accessibility Guide - FlowState-AI CRM

## Overview

FlowState-AI CRM is committed to providing an accessible experience for all users, including those with disabilities. This document outlines our accessibility standards, implementation guidelines, and testing procedures to ensure WCAG 2.1 Level AA compliance.

## Accessibility Standards

We adhere to the **Web Content Accessibility Guidelines (WCAG) 2.1 Level AA** standards, which ensure our application is:

- **Perceivable:** Information and user interface components must be presentable to users in ways they can perceive
- **Operable:** User interface components and navigation must be operable
- **Understandable:** Information and the operation of the user interface must be understandable
- **Robust:** Content must be robust enough to be interpreted by a wide variety of user agents, including assistive technologies

## Implementation Guidelines

### 1. Semantic HTML

Use semantic HTML elements to provide meaning and structure to content.

**Good:**
```tsx
<nav aria-label="Main navigation">
  <ul>
    <li><a href="/customers">Customers</a></li>
  </ul>
</nav>

<main>
  <h1>Customer Details</h1>
  <section aria-labelledby="profile-heading">
    <h2 id="profile-heading">Profile</h2>
    {/* Content */}
  </section>
</main>
```

**Bad:**
```tsx
<div className="nav">
  <div className="link">Customers</div>
</div>

<div>
  <div className="title">Customer Details</div>
  <div className="section">
    <div className="heading">Profile</div>
    {/* Content */}
  </div>
</div>
```

### 2. Keyboard Navigation

All interactive elements must be keyboard accessible using standard keys:
- **Tab:** Move focus forward
- **Shift + Tab:** Move focus backward
- **Enter/Space:** Activate buttons and links
- **Escape:** Close modals and dialogs
- **Arrow keys:** Navigate within components (e.g., dropdown menus)

**Implementation:**
```tsx
// Ensure all interactive elements are focusable
<button
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  }}
>
  Action
</button>

// Add keyboard support for custom components
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick();
    }
  }}
>
  Custom Button
</div>
```

### 3. ARIA Attributes

Use ARIA (Accessible Rich Internet Applications) attributes to enhance accessibility when semantic HTML is insufficient.

**Common ARIA Attributes:**
- `aria-label`: Provides an accessible name for an element
- `aria-labelledby`: References another element that labels this element
- `aria-describedby`: References an element that describes this element
- `aria-live`: Indicates that an element will be updated dynamically
- `aria-expanded`: Indicates whether a collapsible element is expanded
- `aria-hidden`: Hides an element from assistive technologies
- `role`: Defines the role of an element

**Examples:**
```tsx
// Loading spinner
<div
  role="status"
  aria-live="polite"
  aria-label="Loading customer data"
>
  <div className="spinner" aria-hidden="true"></div>
</div>

// Modal dialog
<div
  role="dialog"
  aria-labelledby="modal-title"
  aria-describedby="modal-description"
  aria-modal="true"
>
  <h2 id="modal-title">Qualification Questionnaire</h2>
  <p id="modal-description">Please answer the following questions...</p>
</div>

// Icon buttons
<button aria-label="Edit customer">
  <Edit aria-hidden="true" />
</button>
```

### 4. Form Accessibility

Forms must be fully accessible with proper labels, error messages, and validation feedback.

**Implementation:**
```tsx
// Always use labels with form inputs
<label htmlFor="customer-name">
  Customer Name
  <span aria-label="required">*</span>
</label>
<input
  id="customer-name"
  type="text"
  required
  aria-required="true"
  aria-invalid={hasError}
  aria-describedby={hasError ? "name-error" : undefined}
/>
{hasError && (
  <div id="name-error" role="alert" className="error">
    Please enter a valid name
  </div>
)}

// Group related inputs
<fieldset>
  <legend>Contact Information</legend>
  <label htmlFor="email">Email</label>
  <input id="email" type="email" />
  
  <label htmlFor="phone">Phone</label>
  <input id="phone" type="tel" />
</fieldset>
```

### 5. Color Contrast

Ensure sufficient color contrast ratios:
- **Normal text:** Minimum 4.5:1 contrast ratio
- **Large text (18pt+ or 14pt+ bold):** Minimum 3:1 contrast ratio
- **UI components and graphics:** Minimum 3:1 contrast ratio

**Tools for Testing:**
- Chrome DevTools Lighthouse
- WebAIM Contrast Checker
- axe DevTools browser extension

**Current Color Palette (WCAG AA Compliant):**
```css
/* Primary colors */
--primary-600: #2563eb; /* Blue - 4.5:1 on white */
--primary-700: #1d4ed8; /* Darker blue - 7:1 on white */

/* Status colors */
--success-600: #16a34a; /* Green - 4.5:1 on white */
--warning-600: #ca8a04; /* Yellow - 4.5:1 on white */
--error-600: #dc2626; /* Red - 4.5:1 on white */

/* Text colors */
--gray-900: #111827; /* Primary text - 16:1 on white */
--gray-600: #4b5563; /* Secondary text - 7:1 on white */
```

### 6. Focus Management

Provide clear visual focus indicators and manage focus appropriately.

**Implementation:**
```tsx
// Custom focus styles
<button className="focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2">
  Action
</button>

// Focus management in modals
useEffect(() => {
  if (isOpen) {
    // Store the element that opened the modal
    const previouslyFocusedElement = document.activeElement;
    
    // Focus the first focusable element in the modal
    modalRef.current?.focus();
    
    return () => {
      // Return focus when modal closes
      (previouslyFocusedElement as HTMLElement)?.focus();
    };
  }
}, [isOpen]);

// Focus trap for modals
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Tab') {
    const focusableElements = modalRef.current?.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements?.[0];
    const lastElement = focusableElements?.[focusableElements.length - 1];
    
    if (e.shiftKey && document.activeElement === firstElement) {
      e.preventDefault();
      (lastElement as HTMLElement)?.focus();
    } else if (!e.shiftKey && document.activeElement === lastElement) {
      e.preventDefault();
      (firstElement as HTMLElement)?.focus();
    }
  }
};
```

### 7. Alternative Text

Provide meaningful alternative text for images and icons.

**Implementation:**
```tsx
// Decorative images (hidden from screen readers)
<img src="logo.png" alt="" aria-hidden="true" />

// Informative images
<img src="chart.png" alt="Sales pipeline showing 45% conversion rate" />

// Icon buttons (use aria-label)
<button aria-label="Delete customer">
  <Trash2 aria-hidden="true" />
</button>

// Icons with adjacent text (hide icon from screen readers)
<button>
  <Plus aria-hidden="true" />
  Add Customer
</button>
```

### 8. Responsive and Zoom-Friendly

Ensure the application works at 200% zoom and on various screen sizes.

**Guidelines:**
- Use relative units (rem, em, %) instead of fixed pixels
- Test at 200% browser zoom
- Ensure text reflows without horizontal scrolling
- Avoid fixed-width containers that break at zoom

```css
/* Good */
.container {
  max-width: 80rem; /* 1280px at default font size */
  padding: 1rem;
  font-size: 1rem;
}

/* Bad */
.container {
  width: 1280px;
  padding: 16px;
  font-size: 16px;
}
```

## Testing Procedures

### Automated Testing

We use **axe-core** and **jest-axe** for automated accessibility testing.

```bash
# Run accessibility tests
npm test -- accessibility.test

# Run all tests including accessibility
npm test
```

**Example Test:**
```tsx
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

it('should not have accessibility violations', async () => {
  const { container } = render(<MyComponent />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

### Manual Testing

#### Keyboard Navigation Test
1. Use only the keyboard (no mouse)
2. Tab through all interactive elements
3. Verify focus is visible
4. Test all keyboard shortcuts
5. Ensure no keyboard traps

#### Screen Reader Test
- **Windows:** NVDA (free) or JAWS
- **macOS:** VoiceOver (built-in)
- **Linux:** Orca

**Test Checklist:**
- [ ] All content is announced
- [ ] Interactive elements have clear labels
- [ ] Form errors are announced
- [ ] Dynamic content updates are announced
- [ ] Navigation is logical

#### Browser DevTools
1. Open Chrome DevTools
2. Run Lighthouse audit
3. Check "Accessibility" category
4. Fix any issues with score < 90

### Testing Tools

- **axe DevTools** - Browser extension for accessibility testing
- **WAVE** - Web accessibility evaluation tool
- **Lighthouse** - Built into Chrome DevTools
- **Color Contrast Analyzer** - Desktop app for contrast checking
- **Screen Readers** - NVDA, JAWS, VoiceOver, Orca

## Common Accessibility Issues and Fixes

### Issue: Missing Form Labels
**Problem:** Input fields without associated labels  
**Fix:** Add `<label>` elements with `htmlFor` attribute

```tsx
// Before
<input type="text" placeholder="Name" />

// After
<label htmlFor="name">Name</label>
<input id="name" type="text" />
```

### Issue: Low Color Contrast
**Problem:** Text is difficult to read due to insufficient contrast  
**Fix:** Use colors with at least 4.5:1 contrast ratio

```tsx
// Before
<div className="text-gray-400">Secondary text</div> // 2.5:1 contrast

// After
<div className="text-gray-600">Secondary text</div> // 7:1 contrast
```

### Issue: Missing Alt Text
**Problem:** Images without alternative text  
**Fix:** Add descriptive `alt` attribute or `aria-label`

```tsx
// Before
<img src="user-avatar.jpg" />

// After
<img src="user-avatar.jpg" alt="John Doe's profile picture" />
```

### Issue: Non-Keyboard Accessible
**Problem:** Interactive elements only work with mouse  
**Fix:** Add keyboard event handlers and proper `tabIndex`

```tsx
// Before
<div onClick={handleClick}>Click me</div>

// After
<button onClick={handleClick}>Click me</button>
// or
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => e.key === 'Enter' && handleClick()}
>
  Click me
</div>
```

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN Accessibility Guide](https://developer.mozilla.org/en-US/docs/Web/Accessibility)
- [React Accessibility Documentation](https://react.dev/learn/accessibility)
- [axe-core Documentation](https://github.com/dequelabs/axe-core)
- [WebAIM Resources](https://webaim.org/resources/)
- [A11y Project Checklist](https://www.a11yproject.com/checklist/)

## Accessibility Statement

FlowState-AI CRM is committed to ensuring digital accessibility for people with disabilities. We are continually improving the user experience for everyone and applying the relevant accessibility standards.

If you encounter any accessibility barriers, please contact our support team at [support email].

---

**Last Updated:** October 2, 2025  
**Maintained By:** Manus 7 (Quality-focused AI Agent)
