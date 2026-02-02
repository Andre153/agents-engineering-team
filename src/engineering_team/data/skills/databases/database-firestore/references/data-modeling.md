# Firestore Data Modeling

## Table of Contents
- [Document Design](#document-design)
- [Collection Strategies](#collection-strategies)
- [Relationships](#relationships)
- [Denormalization Patterns](#denormalization-patterns)
- [Multi-Tenancy](#multi-tenancy)
- [Common Schemas](#common-schemas)

## Document Design

### Document Size Considerations

- Max document size: 1 MiB
- Keep documents small for faster reads
- Split large data into subcollections

### Field Types

```typescript
interface FirestoreDocument {
  // Primitives
  stringField: string;
  numberField: number;
  booleanField: boolean;

  // Null
  nullableField: string | null;

  // Timestamp (use for dates)
  createdAt: Timestamp;
  updatedAt: Timestamp;

  // GeoPoint
  location: GeoPoint;

  // Reference
  authorRef: DocumentReference;

  // Arrays (max 20,000 elements recommended)
  tags: string[];

  // Maps (nested objects)
  metadata: {
    source: string;
    version: number;
  };
}
```

### ID Strategies

```typescript
// Auto-generated (recommended for most cases)
const docRef = await db.collection('items').add(data);

// Meaningful IDs (when you need predictable paths)
await db.collection('users').doc(userId).set(data);
await db.collection('user_settings').doc(userId).set(settings);

// Composite IDs (for uniqueness constraints)
const id = `${userId}_${productId}`;
await db.collection('cart_items').doc(id).set(item);

// Slug-based (for URL-friendly paths)
await db.collection('posts').doc(slugify(title)).set(post);
```

## Collection Strategies

### Root Collections vs Subcollections

```typescript
// Root collections - for independent entities
db.collection('users')
db.collection('products')
db.collection('orders')

// Subcollections - for owned/scoped data
db.collection('users').doc(userId).collection('notifications')
db.collection('organizations').doc(orgId).collection('members')

// When to use subcollections:
// - Data is always accessed in context of parent
// - Need to scope security rules to parent
// - Data lifecycle tied to parent
```

### Collection Group Queries

```typescript
// Query across all subcollections with same name
const allNotifications = await db.collectionGroup('notifications')
  .where('read', '==', false)
  .get();

// Requires index in firestore.indexes.json
{
  "indexes": [],
  "fieldOverrides": [
    {
      "collectionGroup": "notifications",
      "fieldPath": "read",
      "indexes": [
        { "order": "ASCENDING", "queryScope": "COLLECTION_GROUP" }
      ]
    }
  ]
}
```

## Relationships

### One-to-One

```typescript
// Option 1: Same document ID
// users/{userId}
// profiles/{userId}  <- Same ID as user

// Option 2: Subcollection with single doc
// users/{userId}/profile/main

// Option 3: Embedded (if small and always needed)
interface User {
  name: string;
  profile: {
    bio: string;
    avatar: string;
  };
}
```

### One-to-Many

```typescript
// Option 1: Subcollection (preferred for large sets)
// users/{userId}/orders/{orderId}

// Option 2: Root collection with reference
interface Order {
  userId: string;  // or DocumentReference
  items: OrderItem[];
  total: number;
}

// Option 3: Array field (for small, bounded sets)
interface User {
  name: string;
  roles: string[];  // Max ~20 items
}
```

### Many-to-Many

```typescript
// Option 1: Junction collection
// users/{userId}
// groups/{groupId}
// memberships/{membershipId}
interface Membership {
  userId: string;
  groupId: string;
  role: 'admin' | 'member';
  joinedAt: Timestamp;
}

// Query: Get user's groups
db.collection('memberships').where('userId', '==', userId)

// Query: Get group's members
db.collection('memberships').where('groupId', '==', groupId)

// Option 2: Arrays on both sides (for small sets)
interface User {
  groupIds: string[];
}
interface Group {
  memberIds: string[];
}
```

## Denormalization Patterns

### Embedded Snapshot

```typescript
// Store snapshot of related data at write time
interface Order {
  id: string;
  userId: string;
  // Snapshot of user at order time
  user: {
    name: string;
    email: string;
  };
  // Snapshot of products at order time
  items: Array<{
    productId: string;
    name: string;
    price: number;
    quantity: number;
  }>;
  total: number;
  createdAt: Timestamp;
}

// Benefits: Fast reads, historical accuracy
// Tradeoff: Data can become stale
```

### Aggregation Documents

```typescript
// Pre-computed aggregations
interface CategoryStats {
  productCount: number;
  averagePrice: number;
  totalInventory: number;
  updatedAt: Timestamp;
}

// Update on write
async function addProduct(product: Product) {
  const batch = db.batch();

  batch.set(db.collection('products').doc(), product);

  batch.update(db.collection('category_stats').doc(product.categoryId), {
    productCount: FieldValue.increment(1),
    totalInventory: FieldValue.increment(product.inventory),
    updatedAt: FieldValue.serverTimestamp(),
  });

  await batch.commit();
}
```

### Fan-Out Pattern

```typescript
// Denormalize to multiple locations for fast reads
async function updateUserName(userId: string, newName: string) {
  const batch = db.batch();

  // Update main document
  batch.update(db.collection('users').doc(userId), { name: newName });

  // Update denormalized copies
  const posts = await db.collection('posts')
    .where('authorId', '==', userId)
    .get();

  posts.docs.forEach(doc => {
    batch.update(doc.ref, { 'author.name': newName });
  });

  await batch.commit();
}
```

## Multi-Tenancy

### Organization-Scoped Data

```typescript
// Structure
// organizations/{orgId}
// organizations/{orgId}/projects/{projectId}
// organizations/{orgId}/members/{userId}

// Security rules enforce tenant isolation
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    function isOrgMember(orgId) {
      return request.auth.token.organizationId == orgId;
    }

    match /organizations/{orgId}/{document=**} {
      allow read, write: if isOrgMember(orgId);
    }
  }
}
```

### Tenant ID as Prefix

```typescript
// Alternative: Prefix document IDs
// users/{tenantId}_{userId}
// Useful when you need collection group queries across tenants (admin)

interface TenantDocument {
  tenantId: string;
  // ... other fields
}

// Query within tenant
db.collection('documents')
  .where('tenantId', '==', tenantId)
  .orderBy('createdAt', 'desc')
```

## Common Schemas

### User Profile

```typescript
interface User {
  // Identity
  uid: string;
  email: string;
  emailVerified: boolean;

  // Profile
  displayName: string;
  photoURL: string | null;
  bio: string;

  // Settings
  preferences: {
    theme: 'light' | 'dark';
    notifications: boolean;
    language: string;
  };

  // Metadata
  createdAt: Timestamp;
  updatedAt: Timestamp;
  lastLoginAt: Timestamp;

  // Soft delete
  isDeleted: boolean;
  deletedAt: Timestamp | null;
}
```

### E-Commerce Order

```typescript
interface Order {
  id: string;
  orderNumber: string; // Human-readable

  // Customer snapshot
  customerId: string;
  customer: {
    name: string;
    email: string;
  };

  // Shipping
  shippingAddress: {
    street: string;
    city: string;
    state: string;
    postalCode: string;
    country: string;
  };

  // Items snapshot
  items: Array<{
    productId: string;
    sku: string;
    name: string;
    price: number;
    quantity: number;
    subtotal: number;
  }>;

  // Totals
  subtotal: number;
  tax: number;
  shipping: number;
  discount: number;
  total: number;

  // Status
  status: 'pending' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  statusHistory: Array<{
    status: string;
    timestamp: Timestamp;
    note?: string;
  }>;

  // Payment
  paymentMethod: string;
  paymentStatus: 'pending' | 'paid' | 'refunded';

  // Timestamps
  createdAt: Timestamp;
  updatedAt: Timestamp;
}
```

### Content Management

```typescript
interface Post {
  id: string;
  slug: string;

  // Content
  title: string;
  excerpt: string;
  content: string; // Or reference to storage
  featuredImage: string | null;

  // Author snapshot
  authorId: string;
  author: {
    name: string;
    avatar: string;
  };

  // Taxonomy
  categoryId: string;
  categoryName: string; // Denormalized
  tags: string[];

  // Status
  status: 'draft' | 'published' | 'archived';
  publishedAt: Timestamp | null;

  // SEO
  metaTitle: string;
  metaDescription: string;

  // Engagement (updated async)
  viewCount: number;
  likeCount: number;
  commentCount: number;

  // Timestamps
  createdAt: Timestamp;
  updatedAt: Timestamp;
}
```

### Chat/Messaging

```typescript
// Conversations
interface Conversation {
  id: string;
  type: 'direct' | 'group';
  name: string | null; // For groups

  // Participants
  participantIds: string[];
  participants: Record<string, {
    name: string;
    avatar: string;
    joinedAt: Timestamp;
  }>;

  // Last message preview
  lastMessage: {
    text: string;
    senderId: string;
    senderName: string;
    sentAt: Timestamp;
  } | null;

  // Unread counts per user
  unreadCounts: Record<string, number>;

  createdAt: Timestamp;
  updatedAt: Timestamp;
}

// Messages (subcollection)
// conversations/{conversationId}/messages/{messageId}
interface Message {
  id: string;
  senderId: string;
  senderName: string;

  type: 'text' | 'image' | 'file';
  text: string;
  attachments: Array<{
    type: string;
    url: string;
    name: string;
    size: number;
  }>;

  // Read receipts
  readBy: Record<string, Timestamp>;

  sentAt: Timestamp;
  editedAt: Timestamp | null;
  deletedAt: Timestamp | null;
}
```
