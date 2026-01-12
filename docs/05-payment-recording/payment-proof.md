# Payment Proof

## Overview

Users can attach proof of payment (receipts, screenshots, bank confirmations) to provide evidence of offline payments. This increases trust and makes confirmation easier.

---

## Supported Proof Types

| Type | Description | Use Case |
|------|-------------|----------|
| Bank Screenshot | Screenshot of bank transfer confirmation | Digital transfers |
| UPI Screenshot | Screenshot of UPI payment confirmation | UPI payments |
| Receipt Photo | Photo of physical receipt | Cash payments |
| PDF Statement | Bank statement excerpt | Formal documentation |

---

## Upload Proof with Payment

### User Story
> As a payer, I want to attach proof when recording a payment.

### Technical Requirements

**Request**
```
POST /api/v1/groups/{group_id}/payments
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

payment_data: {
  "receiver_id": "user-uuid",
  "amount": 100.00,
  "description": "Bank transfer settlement",
  "payment_method": "bank_transfer"
}
proof: <file>
```

**File Validation**
| Rule | Value |
|------|-------|
| Max file size | 5 MB |
| Allowed types | image/jpeg, image/png, image/webp, application/pdf |
| Max files | 3 per payment |

**Response**
```json
HTTP 201 Created
{
  "id": "payment-uuid",
  "amount": 100.00,
  "proof_files": [
    {
      "id": "file-uuid",
      "url": "/uploads/payments/uuid/proof_1.jpg",
      "type": "image/jpeg",
      "uploaded_at": "2026-01-11T15:00:00Z"
    }
  ],
  "status": "pending"
}
```

---

## Add Proof to Existing Payment

### User Story
> As a payer, I want to add proof to a payment I already recorded.

### Technical Requirements

**Request**
```
POST /api/v1/groups/{group_id}/payments/{payment_id}/proof
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <image/pdf>
```

**Response**
```json
HTTP 200 OK
{
  "id": "file-uuid",
  "url": "/uploads/payments/uuid/proof_2.jpg",
  "type": "image/jpeg",
  "uploaded_at": "2026-01-11T15:30:00Z",
  "message": "Proof uploaded successfully"
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 403 | Not payer | `{"detail": "Only the payer can add proof"}` |
| 400 | Max files reached | `{"detail": "Maximum 3 proof files allowed"}` |
| 400 | Invalid file | `{"detail": "Only images and PDFs are allowed"}` |
| 400 | Payment not pending | `{"detail": "Cannot add proof to confirmed/rejected payment"}` |

---

## View Payment Proof

### User Story
> As a receiver, I want to view the proof attached to a payment.

### Technical Requirements

**Request**
```
GET /api/v1/groups/{group_id}/payments/{payment_id}/proof
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "payment_id": "payment-uuid",
  "proof_files": [
    {
      "id": "file-uuid-1",
      "url": "/uploads/payments/uuid/proof_1.jpg",
      "type": "image/jpeg",
      "size_bytes": 245000,
      "uploaded_at": "2026-01-11T15:00:00Z"
    },
    {
      "id": "file-uuid-2",
      "url": "/uploads/payments/uuid/proof_2.pdf",
      "type": "application/pdf",
      "size_bytes": 125000,
      "uploaded_at": "2026-01-11T15:30:00Z"
    }
  ]
}
```

### Get Specific File

**Request**
```
GET /api/v1/groups/{group_id}/payments/{payment_id}/proof/{file_id}
Authorization: Bearer <access_token>
```

**Response**
Returns the file with appropriate content-type header.

---

## Delete Proof

### User Story
> As a payer, I want to delete incorrect proof and upload the correct one.

### Technical Requirements

**Request**
```
DELETE /api/v1/groups/{group_id}/payments/{payment_id}/proof/{file_id}
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "message": "Proof file deleted"
}
```

**Error Responses**
| Code | Condition | Response |
|------|-----------|----------|
| 403 | Not payer | `{"detail": "Only the payer can delete proof"}` |
| 400 | Payment not pending | `{"detail": "Cannot modify proof of confirmed payment"}` |
| 404 | File not found | `{"detail": "Proof file not found"}` |

---

## Proof Visibility

### Access Control

| User | Can View | Can Upload | Can Delete |
|------|----------|------------|------------|
| Payer | ✅ | ✅ | ✅ |
| Receiver | ✅ | ❌ | ❌ |
| Group Admin | ✅ | ❌ | ❌ |
| Other Members | ❌ | ❌ | ❌ |

### Privacy Considerations
- Proof may contain sensitive bank info
- Only payer, receiver, and admins can view
- Files stored securely with access control
- URLs are signed and expire after access

---

## File Processing

### Image Processing
- Original file preserved
- Thumbnail generated (200x200) for preview
- Metadata stripped (EXIF) for privacy

### PDF Handling
- Original file preserved
- First page thumbnail generated
- Text not extracted

### Storage Structure
```
/uploads/payments/{payment_id}/
  ├── proof_1.jpg
  ├── proof_1_thumb.jpg
  ├── proof_2.pdf
  └── proof_2_thumb.png
```

---

## Proof in Notifications

### Payment Notification with Proof
When a payment has proof attached, the notification mentions it:

```
Subject: [GroupName] John recorded a $100 payment (with proof attached)

John has recorded a payment with proof attached. Please review and confirm.

[View Payment & Proof] [Confirm Payment]
```

---

## Proof Requirements (Optional Setting)

### Group Setting
Admins can require proof for payments above a certain amount.

**Configuration**
```json
PATCH /api/v1/groups/{group_id}/settings
{
  "require_payment_proof": true,
  "proof_required_amount": 50.00
}
```

When enabled:
- Payments ≥ threshold must include proof
- Payments without proof are rejected at creation time

---

## Acceptance Criteria

### Upload
- [ ] Can upload proof with payment
- [ ] Can add proof to existing payment
- [ ] Multiple files supported (up to 3)
- [ ] Invalid files rejected
- [ ] File size limit enforced

### View
- [ ] Payer can view proof
- [ ] Receiver can view proof
- [ ] Admin can view proof
- [ ] Other members cannot view
- [ ] Thumbnails displayed correctly

### Delete
- [ ] Payer can delete proof
- [ ] Cannot delete from confirmed payments
- [ ] Receiver cannot delete

### Processing
- [ ] Images are processed correctly
- [ ] Thumbnails generated
- [ ] PDFs handled properly
- [ ] Metadata stripped

### Security
- [ ] URLs are access-controlled
- [ ] Signed URLs expire
- [ ] Files stored securely
