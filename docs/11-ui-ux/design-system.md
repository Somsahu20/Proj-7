# Design System

## Overview

The app uses Tailwind CSS for styling and shadcn/ui for components, with support for dark mode.

---

## Colors

### Light Mode

| Token | Value | Usage |
|-------|-------|-------|
| `background` | #FFFFFF | Page background |
| `foreground` | #0F172A | Primary text |
| `primary` | #3B82F6 | Buttons, links |
| `secondary` | #64748B | Secondary text |
| `accent` | #F1F5F9 | Hover states |
| `success` | #10B981 | Positive balance |
| `danger` | #EF4444 | Negative balance |
| `warning` | #F59E0B | Warnings |

### Dark Mode

| Token | Value | Usage |
|-------|-------|-------|
| `background` | #0F172A | Page background |
| `foreground` | #F8FAFC | Primary text |
| `primary` | #60A5FA | Buttons, links |
| `secondary` | #94A3B8 | Secondary text |
| `accent` | #1E293B | Hover states |

---

## Typography

### Font Stack

```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

### Scale

| Name | Size | Line Height | Usage |
|------|------|-------------|-------|
| `text-xs` | 12px | 16px | Labels, captions |
| `text-sm` | 14px | 20px | Secondary text |
| `text-base` | 16px | 24px | Body text |
| `text-lg` | 18px | 28px | Subheadings |
| `text-xl` | 20px | 28px | Card titles |
| `text-2xl` | 24px | 32px | Page titles |
| `text-3xl` | 30px | 36px | Hero text |

---

## Spacing

Using Tailwind's spacing scale (4px base):

| Class | Value | Usage |
|-------|-------|-------|
| `p-2` | 8px | Tight spacing |
| `p-4` | 16px | Standard spacing |
| `p-6` | 24px | Card padding |
| `p-8` | 32px | Section spacing |
| `gap-4` | 16px | Grid/flex gap |

---

## Components (shadcn/ui)

### Buttons

```jsx
<Button>Primary</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="destructive">Danger</Button>
```

### Forms

```jsx
<Input placeholder="Enter amount" />
<Select>...</Select>
<Checkbox />
<RadioGroup />
<Textarea />
```

### Feedback

```jsx
<Toast />
<Alert />
<Badge />
<Skeleton />
```

### Layout

```jsx
<Card />
<Dialog />
<Sheet />
<Tabs />
<Accordion />
```

---

## Breakpoints

| Name | Min Width | Usage |
|------|-----------|-------|
| `sm` | 640px | Large phones |
| `md` | 768px | Tablets |
| `lg` | 1024px | Laptops |
| `xl` | 1280px | Desktops |

---

## Dark Mode

### Implementation

```jsx
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  // ...
}

// Usage
<html className={theme === 'dark' ? 'dark' : ''}>
```

### Toggle

Stored in localStorage, synced with system preference.

---

## Icons

Using Lucide React icons:

```jsx
import { Plus, Settings, Bell, User } from 'lucide-react';

<Plus className="h-4 w-4" />
```

---

## Animations

### Transitions

```css
transition: all 0.15s ease;
```

### Loading States

- Skeleton loaders for content
- Spinner for actions
- Progress bar for uploads

---

## Accessibility

### Requirements

- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader support
- Focus indicators
- Color contrast ratios

### Implementation

- Semantic HTML
- ARIA labels
- Focus trapping in modals
- Skip links
