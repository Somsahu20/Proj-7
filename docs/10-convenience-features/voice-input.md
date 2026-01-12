# Voice Input

## Overview

Users can add expenses using voice commands, powered by the Web Speech API.

---

## Voice Commands

### Add Expense

**Example utterances**:
- "Add $50 for dinner"
- "Spent $25 on groceries"
- "Coffee for $5"
- "Add 100 dollars for hotel, split with John and Jane"

### Parsing

```javascript
// Input: "Add $50 for dinner split with John"
// Parsed:
{
  "amount": 50.00,
  "description": "dinner",
  "split_with": ["John"],
  "confidence": 0.85
}
```

---

## Implementation

### Web Speech API

```javascript
const recognition = new webkitSpeechRecognition();
recognition.continuous = false;
recognition.interimResults = true;

recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  const parsed = parseExpenseFromVoice(transcript);
  showConfirmationDialog(parsed);
};
```

### Flow

```
1. User taps microphone icon
2. "Listening..." indicator
3. User speaks
4. Transcript displayed
5. Parsed expense shown
6. User confirms or edits
7. Expense created
```

---

## Parsing Logic

### Amount Detection
- "$50", "50 dollars", "fifty bucks"
- Currency symbols and words

### Description Detection
- "for dinner", "on groceries"
- Everything after amount

### Split Detection
- "split with John"
- "between me, John, and Jane"

---

## Confirmation UI

```
┌─────────────────────────────────────┐
│ 🎤 You said: "50 dollars for dinner │
│              split with John"       │
├─────────────────────────────────────┤
│ Amount: $50.00            [Edit]    │
│ Description: Dinner       [Edit]    │
│ Split with: John          [Edit]    │
│ Category: Food & Drinks   [Change]  │
├─────────────────────────────────────┤
│     [Cancel]    [Add Expense]       │
└─────────────────────────────────────┘
```

---

## Acceptance Criteria

- [ ] Voice input activates
- [ ] Speech recognized accurately
- [ ] Amount parsed correctly
- [ ] Description extracted
- [ ] Confirmation before saving
- [ ] Edit option before submit
