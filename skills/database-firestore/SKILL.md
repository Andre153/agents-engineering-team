---
name: database-firestore
description: "Firestore database design, data modeling, querying, and best practices. Use when designing Firestore schemas, writing queries, implementing security rules, or optimizing Firestore performance."
---

# Firestore Database

## Quick Reference

| Topic | Reference |
|-------|-----------|
| Data modeling patterns | See [data-modeling.md](references/data-modeling.md) |
| Querying and indexing | See [queries.md](references/queries.md) |
| Security rules | See [security-rules.md](references/security-rules.md) |

## Core Concepts

### Document Database Structure

```
Firestore
├── Collection: users
│   ├── Document: user-1
│   │   ├── Field: name = "Alice"
│   │   ├── Field: email = "alice@example.com"
│   │   └── Subcollection: orders
│   │       └── Document: order-1
│   └── Document: user-2
└── Collection: products
    └── Document: product-1
```

### Admin SDK Setup

```typescript
import { initializeApp, cert } from 'firebase-admin/app';
import { getFirestore, FieldValue, Timestamp } from 'firebase-admin/firestore';

initializeApp({
  credential: cert(serviceAccount),
});

const db = getFirestore();
```

## CRUD Operations

### Create

```typescript
// Auto-generated ID
const docRef = await db.collection('users').add({
  name: 'Alice',
  email: 'alice@example.com',
  createdAt: FieldValue.serverTimestamp(),
});
console.log('Created with ID:', docRef.id);

// Specific ID
await db.collection('users').doc('user-alice').set({
  name: 'Alice',
  email: 'alice@example.com',
});

// Set with merge (upsert)
await db.collection('users').doc('user-alice').set({
  lastLogin: FieldValue.serverTimestamp(),
}, { merge: true });
```

### Read

```typescript
// Single document
const doc = await db.collection('users').doc('user-1').get();
if (doc.exists) {
  console.log(doc.id, doc.data());
}

// Collection
const snapshot = await db.collection('users').get();
snapshot.forEach(doc => {
  console.log(doc.id, doc.data());
});

// With query
const activeUsers = await db.collection('users')
  .where('status', '==', 'active')
  .orderBy('createdAt', 'desc')
  .limit(10)
  .get();
```

### Update

```typescript
// Update fields
await db.collection('users').doc('user-1').update({
  name: 'Alice Smith',
  updatedAt: FieldValue.serverTimestamp(),
});

// Nested field update
await db.collection('users').doc('user-1').update({
  'address.city': 'New York',
  'preferences.theme': 'dark',
});

// Array operations
await db.collection('users').doc('user-1').update({
  tags: FieldValue.arrayUnion('premium'),
  // tags: FieldValue.arrayRemove('basic'),
});

// Increment
await db.collection('posts').doc('post-1').update({
  viewCount: FieldValue.increment(1),
});
```

### Delete

```typescript
// Delete document
await db.collection('users').doc('user-1').delete();

// Delete field
await db.collection('users').doc('user-1').update({
  temporaryField: FieldValue.delete(),
});
```

## Batch and Transactions

### Batch Writes

```typescript
const batch = db.batch();

// Add operations (max 500 per batch)
const userRef = db.collection('users').doc('user-1');
batch.set(userRef, { name: 'Alice' });

const profileRef = db.collection('profiles').doc('user-1');
batch.set(profileRef, { bio: 'Hello' });

const counterRef = db.collection('counters').doc('users');
batch.update(counterRef, { count: FieldValue.increment(1) });

// Commit atomically
await batch.commit();
```

### Transactions

```typescript
await db.runTransaction(async (transaction) => {
  // Reads must come before writes
  const accountRef = db.collection('accounts').doc('account-1');
  const account = await transaction.get(accountRef);

  if (!account.exists) {
    throw new Error('Account not found');
  }

  const currentBalance = account.data()!.balance;
  if (currentBalance < 100) {
    throw new Error('Insufficient balance');
  }

  // Now write
  transaction.update(accountRef, {
    balance: currentBalance - 100,
  });

  transaction.set(db.collection('transactions').doc(), {
    accountId: 'account-1',
    amount: -100,
    timestamp: FieldValue.serverTimestamp(),
  });
});
```

## Common Patterns

### Typed Collections

```typescript
interface User {
  id: string;
  name: string;
  email: string;
  createdAt: Timestamp;
}

// Generic converter
function createConverter<T extends { id: string }>() {
  return {
    toFirestore: (data: Omit<T, 'id'>) => data,
    fromFirestore: (snap: FirebaseFirestore.QueryDocumentSnapshot): T => ({
      id: snap.id,
      ...snap.data(),
    } as T),
  };
}

const usersRef = db.collection('users').withConverter(createConverter<User>());

// Now fully typed
const user = await usersRef.doc('user-1').get();
const userData: User | undefined = user.data();
```

### Pagination

```typescript
interface PaginatedResult<T> {
  items: T[];
  lastDoc: FirebaseFirestore.DocumentSnapshot | null;
  hasMore: boolean;
}

async function paginate<T>(
  query: FirebaseFirestore.Query,
  limit: number,
  startAfterDoc?: FirebaseFirestore.DocumentSnapshot
): Promise<PaginatedResult<T>> {
  let q = query.limit(limit + 1);

  if (startAfterDoc) {
    q = q.startAfter(startAfterDoc);
  }

  const snapshot = await q.get();
  const docs = snapshot.docs;
  const hasMore = docs.length > limit;

  if (hasMore) docs.pop();

  return {
    items: docs.map(doc => ({ id: doc.id, ...doc.data() } as T)),
    lastDoc: docs.length > 0 ? docs[docs.length - 1] : null,
    hasMore,
  };
}

// Usage
const page1 = await paginate<User>(
  db.collection('users').orderBy('createdAt', 'desc'),
  20
);

const page2 = await paginate<User>(
  db.collection('users').orderBy('createdAt', 'desc'),
  20,
  page1.lastDoc!
);
```

### Cursor-based Pagination (for APIs)

```typescript
async function paginateWithCursor<T>(
  query: FirebaseFirestore.Query,
  limit: number,
  cursor?: string
): Promise<{ items: T[]; nextCursor?: string }> {
  let q = query.limit(limit + 1);

  if (cursor) {
    const cursorDoc = await db.doc(cursor).get();
    q = q.startAfter(cursorDoc);
  }

  const snapshot = await q.get();
  const docs = snapshot.docs;
  const hasMore = docs.length > limit;

  if (hasMore) docs.pop();

  return {
    items: docs.map(doc => ({ id: doc.id, ...doc.data() } as T)),
    nextCursor: hasMore ? docs[docs.length - 1].ref.path : undefined,
  };
}
```

### Soft Delete

```typescript
interface SoftDeletable {
  deletedAt: Timestamp | null;
  isDeleted: boolean;
}

async function softDelete(ref: FirebaseFirestore.DocumentReference) {
  await ref.update({
    isDeleted: true,
    deletedAt: FieldValue.serverTimestamp(),
  });
}

// Query active records only
const activeUsers = await db.collection('users')
  .where('isDeleted', '==', false)
  .get();
```

### Audit Trail

```typescript
interface AuditLog {
  entityType: string;
  entityId: string;
  action: 'create' | 'update' | 'delete';
  userId: string;
  changes: Record<string, { old: unknown; new: unknown }>;
  timestamp: Timestamp;
}

async function updateWithAudit(
  ref: FirebaseFirestore.DocumentReference,
  updates: Record<string, unknown>,
  userId: string
) {
  const doc = await ref.get();
  const oldData = doc.data() || {};

  const changes: Record<string, { old: unknown; new: unknown }> = {};
  for (const [key, value] of Object.entries(updates)) {
    if (oldData[key] !== value) {
      changes[key] = { old: oldData[key], new: value };
    }
  }

  const batch = db.batch();

  batch.update(ref, {
    ...updates,
    updatedAt: FieldValue.serverTimestamp(),
  });

  batch.set(db.collection('audit_logs').doc(), {
    entityType: ref.parent.id,
    entityId: ref.id,
    action: 'update',
    userId,
    changes,
    timestamp: FieldValue.serverTimestamp(),
  } as AuditLog);

  await batch.commit();
}
```

## Performance Tips

### Index Strategy

```javascript
// firestore.indexes.json
{
  "indexes": [
    {
      "collectionGroup": "orders",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "userId", "order": "ASCENDING" },
        { "fieldPath": "createdAt", "order": "DESCENDING" }
      ]
    },
    {
      "collectionGroup": "products",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "category", "order": "ASCENDING" },
        { "fieldPath": "price", "order": "ASCENDING" }
      ]
    }
  ]
}
```

### Denormalization

```typescript
// Store frequently accessed data together
interface Order {
  id: string;
  userId: string;
  // Denormalized user data
  userName: string;
  userEmail: string;
  // Denormalized product data
  items: Array<{
    productId: string;
    productName: string;
    productPrice: number;
    quantity: number;
  }>;
  total: number;
  createdAt: Timestamp;
}
```

### Aggregation with Counter Documents

```typescript
// Maintain counters for expensive counts
async function incrementCounter(counterId: string, field: string) {
  const counterRef = db.collection('counters').doc(counterId);
  await counterRef.set({
    [field]: FieldValue.increment(1),
  }, { merge: true });
}

// Usage
await incrementCounter('global', 'totalUsers');
await incrementCounter('org-123', 'memberCount');
```

## Query Limitations

### Firestore Constraints

| Constraint | Limit |
|------------|-------|
| Max document size | 1 MiB |
| Max field depth | 20 levels |
| Max write operations per second per document | 1 |
| Max `in` / `array-contains-any` values | 30 |
| Max inequality filters per query | 1 field (but multiple on same field OK) |
| Max `OR` groups in a query | 30 |

### Query Patterns

```typescript
// ✅ Valid: Multiple equality + one inequality
db.collection('orders')
  .where('status', '==', 'pending')
  .where('userId', '==', 'user-1')
  .where('total', '>', 100)

// ❌ Invalid: Inequality on different fields
db.collection('orders')
  .where('createdAt', '>', yesterday)
  .where('total', '<', 100)

// ✅ Valid: Range on same field
db.collection('products')
  .where('price', '>=', 10)
  .where('price', '<=', 100)

// ✅ Valid: in query (max 30 values)
db.collection('users')
  .where('status', 'in', ['active', 'pending'])

// ✅ Valid: array-contains
db.collection('posts')
  .where('tags', 'array-contains', 'typescript')
```

For detailed patterns, see the reference files.
