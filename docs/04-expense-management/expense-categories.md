# Expense Categories

## Overview

Expenses can be categorized to help with organization, filtering, and analysis. Categories can be predefined per group type or custom.

---

## Predefined Categories

### Trip Category

| Category | Icon | Description |
|----------|------|-------------|
| Transport | 🚗 | Flights, trains, taxis, car rentals |
| Accommodation | 🏨 | Hotels, Airbnb, hostels |
| Food & Drinks | 🍕 | Restaurants, groceries, snacks |
| Activities | 🎢 | Tours, attractions, experiences |
| Shopping | 🛍️ | Souvenirs, clothing, gifts |
| Other | 📦 | Miscellaneous expenses |

### Apartment Category

| Category | Icon | Description |
|----------|------|-------------|
| Rent | 🏠 | Monthly rent payments |
| Utilities | 💡 | Electricity, water, gas |
| Internet | 📶 | Internet and cable |
| Groceries | 🛒 | Food and household items |
| Cleaning | 🧹 | Cleaning supplies, services |
| Maintenance | 🔧 | Repairs and maintenance |
| Other | 📦 | Miscellaneous expenses |

### Couple Category

| Category | Icon | Description |
|----------|------|-------------|
| Dining | 🍽️ | Restaurants and takeout |
| Groceries | 🛒 | Food and household |
| Entertainment | 🎬 | Movies, concerts, events |
| Transportation | 🚌 | Commute, gas, parking |
| Gifts | 🎁 | Presents for each other |
| Subscriptions | 📺 | Streaming, apps, memberships |
| Other | 📦 | Miscellaneous expenses |

### Friends/Outings Category

| Category | Icon | Description |
|----------|------|-------------|
| Food & Drinks | 🍻 | Restaurants, bars, cafes |
| Entertainment | 🎮 | Movies, games, events |
| Transport | 🚕 | Shared rides, parking |
| Tickets | 🎟️ | Event tickets, entry fees |
| Other | 📦 | Miscellaneous expenses |

### Default (Other) Category

| Category | Icon | Description |
|----------|------|-------------|
| Food | 🍔 | Food expenses |
| Transport | 🚗 | Transportation |
| Utilities | 💡 | Bills and utilities |
| Entertainment | 🎭 | Fun and leisure |
| Shopping | 🛒 | Purchases |
| Health | 💊 | Medical expenses |
| Other | 📦 | Miscellaneous |

---

## Get Categories for Group

### Technical Requirements

**Request**
```
GET /api/v1/groups/{group_id}/categories
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "group_type": "trip",
  "categories": [
    {
      "name": "Transport",
      "icon": "🚗",
      "is_custom": false,
      "expense_count": 5,
      "total_amount": 350.00
    },
    {
      "name": "Accommodation",
      "icon": "🏨",
      "is_custom": false,
      "expense_count": 2,
      "total_amount": 400.00
    },
    {
      "name": "Souvenirs",
      "icon": "🎁",
      "is_custom": true,
      "expense_count": 3,
      "total_amount": 75.00
    }
  ]
}
```

---

## Custom Categories

### User Story
> As a group admin, I want to create custom categories that fit our specific needs.

### Create Custom Category

**Request**
```json
POST /api/v1/groups/{group_id}/categories
Authorization: Bearer <access_token>
{
  "name": "Pet Expenses",
  "icon": "🐕"
}
```

**Validation**
| Rule | Value |
|------|-------|
| Name | 2-50 chars, unique in group |
| Icon | Optional, single emoji |

**Response**
```json
HTTP 201 Created
{
  "name": "Pet Expenses",
  "icon": "🐕",
  "is_custom": true
}
```

### Edit Custom Category

**Request**
```json
PATCH /api/v1/groups/{group_id}/categories/{category_name}
Authorization: Bearer <access_token>
{
  "name": "Pet Care",
  "icon": "🐾"
}
```

**Response**
```json
HTTP 200 OK
{
  "name": "Pet Care",
  "icon": "🐾",
  "is_custom": true
}
```

Note: Updating category name updates all expenses using it.

### Delete Custom Category

**Request**
```
DELETE /api/v1/groups/{group_id}/categories/{category_name}
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "message": "Category deleted",
  "affected_expenses": 3,
  "new_category": "Other"
}
```

Note: Expenses with deleted category are moved to "Other".

---

## Category Statistics

### User Story
> As a group member, I want to see spending breakdown by category.

### Technical Requirements

**Request**
```
GET /api/v1/groups/{group_id}/categories/statistics
Authorization: Bearer <access_token>
Query Parameters:
  - period: string (this_month | last_month | all_time | custom)
  - start_date: date (for custom)
  - end_date: date (for custom)
```

**Response**
```json
HTTP 200 OK
{
  "period": {
    "start": "2026-01-01",
    "end": "2026-01-31"
  },
  "total_expenses": 1500.00,
  "categories": [
    {
      "name": "Food & Drinks",
      "icon": "🍕",
      "amount": 600.00,
      "percentage": 40.0,
      "count": 15,
      "trend": "up",
      "trend_percentage": 15.0
    },
    {
      "name": "Transport",
      "icon": "🚗",
      "amount": 400.00,
      "percentage": 26.7,
      "count": 8,
      "trend": "stable",
      "trend_percentage": 0.0
    },
    {
      "name": "Accommodation",
      "icon": "🏨",
      "amount": 350.00,
      "percentage": 23.3,
      "count": 2,
      "trend": "down",
      "trend_percentage": -10.0
    },
    {
      "name": "Other",
      "icon": "📦",
      "amount": 150.00,
      "percentage": 10.0,
      "count": 5,
      "trend": "stable",
      "trend_percentage": 0.0
    }
  ]
}
```

---

## Category Icons

### Available Icons (Emoji Support)

```
🍕🍔🍽️🍻🥤☕ - Food & Drinks
🚗🚕🚌✈️🚂🛵 - Transport
🏨🏠🛏️🏡🏢 - Accommodation
🎬🎮🎢🎭🎤🎪 - Entertainment
🛒🛍️👕👗💄 - Shopping
💡💧🔌📶📺 - Utilities
🔧🧹🧺💊🏥 - Services
🎁🎂🎉💐❤️ - Gifts/Special
📦❓🔖💰💳 - Other/Finance
```

### Icon Selection UI
- Grid of common icons
- Category-relevant suggestions
- Custom emoji input
- No icon option (show first letter)

---

## Uncategorized Expenses

### Behavior
- Expenses without category are valid
- Displayed as "Uncategorized" in lists
- Counted separately in statistics

### Suggest Category
Based on description keywords:

| Keywords | Suggested Category |
|----------|-------------------|
| uber, lyft, taxi, cab | Transport |
| hotel, airbnb, booking | Accommodation |
| dinner, lunch, restaurant | Food & Drinks |
| movie, cinema, concert | Entertainment |
| grocery, supermarket | Groceries |

---

## Category Filtering

### Filter Expenses by Category

**Request**
```
GET /api/v1/groups/{group_id}/expenses?category=Transport
```

### Filter Multiple Categories

**Request**
```
GET /api/v1/groups/{group_id}/expenses?categories=Transport,Food
```

### Filter Uncategorized

**Request**
```
GET /api/v1/groups/{group_id}/expenses?category=uncategorized
```

---

## Acceptance Criteria

### Predefined Categories
- [ ] Categories loaded based on group type
- [ ] All predefined categories are available
- [ ] Icons display correctly

### Custom Categories
- [ ] Admin can create custom categories
- [ ] Admin can edit custom categories
- [ ] Admin can delete custom categories
- [ ] Deleted category expenses moved to "Other"

### Statistics
- [ ] Category breakdown is accurate
- [ ] Percentages total 100%
- [ ] Trends are calculated correctly

### Filtering
- [ ] Filter by single category works
- [ ] Filter by multiple categories works
- [ ] Uncategorized filter works

### UI
- [ ] Category dropdown in expense form
- [ ] Icon picker for custom categories
- [ ] Category badges on expense list
