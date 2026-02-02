# Firestore Queries

## Table of Contents
- [Basic Queries](#basic-queries)
- [Compound Queries](#compound-queries)
- [Ordering and Limiting](#ordering-and-limiting)
- [Pagination](#pagination)
- [Real-time Listeners](#real-time-listeners)
- [Indexing](#indexing)
- [Query Patterns](#query-patterns)

## Basic Queries

### Equality

```typescript
// Single field equality
const users = await db.collection('users')
  .where('status', '==', 'active')
  .get();

// Multiple equality conditions
const orders = await db.collection('orders')
  .where('userId', '==', userId)
  .where('status', '==', 'pending')
  .get();
```

### Comparison

```typescript
// Greater than
const expensiveProducts = await db.collection('products')
  .where('price', '>', 100)
  .get();

// Greater than or equal
const recentOrders = await db.collection('orders')
  .where('createdAt', '>=', lastWeek)
  .get();

// Less than
const lowStock = await db.collection('products')
  .where('inventory', '<', 10)
  .get();

// Not equal
const activeUsers = await db.collection('users')
  .where('status', '!=', 'deleted')
  .get();
```

### In Queries

```typescript
// in - matches any value in array (max 30 values)
const selectedUsers = await db.collection('users')
  .where('uid', 'in', ['user1', 'user2', 'user3'])
  .get();

// not-in - excludes values (max 10 values)
const otherUsers = await db.collection('users')
  .where('role', 'not-in', ['admin', 'moderator'])
  .get();
```

### Array Queries

```typescript
// array-contains - document has value in array
const typescriptPosts = await db.collection('posts')
  .where('tags', 'array-contains', 'typescript')
  .get();

// array-contains-any - has any of the values (max 30)
const techPosts = await db.collection('posts')
  .where('tags', 'array-contains-any', ['javascript', 'typescript', 'node'])
  .get();
```

## Compound Queries

### AND Conditions

```typescript
// All conditions must match
const results = await db.collection('products')
  .where('category', '==', 'electronics')
  .where('price', '<=', 500)
  .where('inStock', '==', true)
  .get();
```

### OR Conditions (Firestore v2)

```typescript
import { or, and, where } from 'firebase/firestore';

// OR query
const results = await db.collection('orders')
  .where(
    or(
      where('status', '==', 'pending'),
      where('status', '==', 'processing')
    )
  )
  .get();

// Complex: (A AND B) OR (C AND D)
const complex = await db.collection('products')
  .where(
    or(
      and(
        where('category', '==', 'electronics'),
        where('price', '<', 100)
      ),
      and(
        where('category', '==', 'books'),
        where('price', '<', 20)
      )
    )
  )
  .get();
```

### Query Limitations

```typescript
// ❌ Cannot use inequality on different fields
db.collection('products')
  .where('price', '>', 100)
  .where('rating', '<', 3)  // ERROR

// ✅ Use composite index for range on same field
db.collection('products')
  .where('price', '>=', 50)
  .where('price', '<=', 100)

// ❌ Cannot combine array-contains with array-contains-any
db.collection('posts')
  .where('tags', 'array-contains', 'a')
  .where('categories', 'array-contains-any', ['b', 'c'])  // ERROR

// ❌ Cannot combine not-in with != or not-in
db.collection('users')
  .where('role', 'not-in', ['admin'])
  .where('status', '!=', 'deleted')  // ERROR
```

## Ordering and Limiting

### Order By

```typescript
// Ascending (default)
const oldest = await db.collection('users')
  .orderBy('createdAt')
  .get();

// Descending
const newest = await db.collection('users')
  .orderBy('createdAt', 'desc')
  .get();

// Multiple order fields
const sorted = await db.collection('products')
  .orderBy('category')
  .orderBy('price', 'desc')
  .get();

// Order after filter (requires index if inequality)
const filtered = await db.collection('products')
  .where('category', '==', 'electronics')
  .orderBy('price', 'desc')
  .get();
```

### Limiting

```typescript
// Limit results
const top10 = await db.collection('products')
  .orderBy('sales', 'desc')
  .limit(10)
  .get();

// Limit to last N
const last5 = await db.collection('messages')
  .orderBy('sentAt', 'desc')
  .limitToLast(5)
  .get();
```

## Pagination

### Cursor-Based Pagination

```typescript
// First page
const firstPage = await db.collection('products')
  .orderBy('name')
  .limit(25)
  .get();

const lastDoc = firstPage.docs[firstPage.docs.length - 1];

// Next page
const nextPage = await db.collection('products')
  .orderBy('name')
  .startAfter(lastDoc)
  .limit(25)
  .get();

// Previous page
const prevPage = await db.collection('products')
  .orderBy('name')
  .endBefore(firstPage.docs[0])
  .limitToLast(25)
  .get();
```

### Offset-Based (Not Recommended)

```typescript
// ❌ Expensive - reads all skipped documents
const page3 = await db.collection('products')
  .orderBy('name')
  .offset(50)  // Skips 50 docs but still bills for reads
  .limit(25)
  .get();

// ✅ Better: Use cursor-based pagination
```

### Pagination Helper

```typescript
interface Page<T> {
  items: T[];
  hasNext: boolean;
  hasPrev: boolean;
  cursors: {
    start: string | null;
    end: string | null;
  };
}

async function getPage<T>(
  baseQuery: FirebaseFirestore.Query,
  pageSize: number,
  cursor?: { type: 'after' | 'before'; docPath: string }
): Promise<Page<T>> {
  let query = baseQuery.limit(pageSize + 1);

  if (cursor) {
    const cursorDoc = await db.doc(cursor.docPath).get();
    query = cursor.type === 'after'
      ? query.startAfter(cursorDoc)
      : query.endBefore(cursorDoc).limitToLast(pageSize + 1);
  }

  const snapshot = await query.get();
  const docs = snapshot.docs;
  const hasMore = docs.length > pageSize;

  if (hasMore) {
    cursor?.type === 'before' ? docs.shift() : docs.pop();
  }

  return {
    items: docs.map(d => ({ id: d.id, ...d.data() } as T)),
    hasNext: cursor?.type === 'before' ? true : hasMore,
    hasPrev: cursor?.type === 'after' ? true : (cursor?.type === 'before' && hasMore),
    cursors: {
      start: docs[0]?.ref.path || null,
      end: docs[docs.length - 1]?.ref.path || null,
    },
  };
}
```

## Real-time Listeners

### Document Listener

```typescript
const unsubscribe = db.collection('users').doc(userId)
  .onSnapshot(
    (doc) => {
      if (doc.exists) {
        console.log('User data:', doc.data());
      }
    },
    (error) => {
      console.error('Listen error:', error);
    }
  );

// Cleanup
unsubscribe();
```

### Collection Listener

```typescript
const unsubscribe = db.collection('messages')
  .where('conversationId', '==', conversationId)
  .orderBy('sentAt', 'desc')
  .limit(50)
  .onSnapshot((snapshot) => {
    snapshot.docChanges().forEach((change) => {
      if (change.type === 'added') {
        console.log('New message:', change.doc.data());
      }
      if (change.type === 'modified') {
        console.log('Modified:', change.doc.data());
      }
      if (change.type === 'removed') {
        console.log('Removed:', change.doc.id);
      }
    });
  });
```

### Listener Options

```typescript
// Include metadata changes
db.collection('items').doc(id)
  .onSnapshot(
    { includeMetadataChanges: true },
    (doc) => {
      const source = doc.metadata.hasPendingWrites ? 'Local' : 'Server';
      console.log(`${source} data:`, doc.data());
    }
  );
```

## Indexing

### Single-Field Indexes

Automatically created for all fields. No configuration needed.

### Composite Indexes

```json
// firestore.indexes.json
{
  "indexes": [
    {
      "collectionGroup": "orders",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "userId", "order": "ASCENDING" },
        { "fieldPath": "status", "order": "ASCENDING" },
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
  ],
  "fieldOverrides": [
    {
      "collectionGroup": "posts",
      "fieldPath": "tags",
      "indexes": [
        { "order": "ASCENDING", "queryScope": "COLLECTION" },
        { "arrayConfig": "CONTAINS", "queryScope": "COLLECTION" },
        { "order": "ASCENDING", "queryScope": "COLLECTION_GROUP" }
      ]
    }
  ]
}
```

### Index Exemptions

```json
{
  "fieldOverrides": [
    {
      "collectionGroup": "logs",
      "fieldPath": "message",
      "indexes": []  // Disable indexing for this field
    }
  ]
}
```

## Query Patterns

### Search by Prefix

```typescript
// Firestore doesn't support full-text search
// But prefix search works with range queries
const query = db.collection('users')
  .where('name', '>=', searchTerm)
  .where('name', '<=', searchTerm + '\uf8ff')
  .limit(10);

// For full-text search, use:
// - Algolia
// - Elasticsearch
// - Cloud Functions + search index
```

### Date Range

```typescript
const today = new Date();
const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);

const recentOrders = await db.collection('orders')
  .where('createdAt', '>=', Timestamp.fromDate(weekAgo))
  .where('createdAt', '<=', Timestamp.fromDate(today))
  .orderBy('createdAt', 'desc')
  .get();
```

### Geospatial (Basic)

```typescript
import { GeoPoint } from 'firebase-admin/firestore';

// Store location
await db.collection('stores').doc(storeId).set({
  name: 'Store Name',
  location: new GeoPoint(37.7749, -122.4194),
});

// Firestore doesn't have native geo queries
// Use geohash library for proximity queries
import * as geohash from 'ngeohash';

const hash = geohash.encode(lat, lng, 5); // precision 5

const nearby = await db.collection('stores')
  .where('geohash', '>=', hash)
  .where('geohash', '<=', hash + '\uf8ff')
  .get();
```

### Count Documents

```typescript
// Firestore v2: Native count
const countQuery = db.collection('users')
  .where('status', '==', 'active')
  .count();

const snapshot = await countQuery.get();
console.log('Count:', snapshot.data().count);

// For older versions or complex counts:
// Use counter documents (see data-modeling.md)
```

### Aggregate Queries

```typescript
// Sum (Firestore v2)
const sumQuery = db.collection('orders')
  .where('status', '==', 'completed')
  .aggregate({
    totalRevenue: AggregateField.sum('total'),
    orderCount: AggregateField.count(),
    avgOrder: AggregateField.average('total'),
  });

const result = await sumQuery.get();
console.log(result.data());
// { totalRevenue: 15000, orderCount: 150, avgOrder: 100 }
```
