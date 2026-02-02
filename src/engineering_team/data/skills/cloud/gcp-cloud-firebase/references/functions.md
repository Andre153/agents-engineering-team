# Cloud Functions for Firebase

## Table of Contents
- [Project Setup](#project-setup)
- [HTTP Functions](#http-functions)
- [Firestore Triggers](#firestore-triggers)
- [Auth Triggers](#auth-triggers)
- [Storage Triggers](#storage-triggers)
- [Scheduled Functions](#scheduled-functions)
- [Callable Functions](#callable-functions)
- [Best Practices](#best-practices)

## Project Setup

### Initialize

```bash
firebase init functions
```

### package.json

```json
{
  "name": "functions",
  "scripts": {
    "build": "tsc",
    "serve": "npm run build && firebase emulators:start --only functions",
    "deploy": "firebase deploy --only functions"
  },
  "engines": {
    "node": "20"
  },
  "main": "lib/index.js",
  "dependencies": {
    "firebase-admin": "^12.0.0",
    "firebase-functions": "^5.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0"
  }
}
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "module": "commonjs",
    "noImplicitReturns": true,
    "noUnusedLocals": true,
    "outDir": "lib",
    "sourceMap": true,
    "strict": true,
    "target": "es2022"
  },
  "include": ["src"]
}
```

### Basic Structure

```typescript
// src/index.ts
import { initializeApp } from 'firebase-admin/app';
import { setGlobalOptions } from 'firebase-functions/v2';

initializeApp();

setGlobalOptions({
  region: 'us-central1',
  memory: '256MiB',
  timeoutSeconds: 60,
});

// Export functions
export * from './http';
export * from './triggers';
export * from './scheduled';
```

## HTTP Functions

### Basic HTTP Function

```typescript
import { onRequest } from 'firebase-functions/v2/https';

export const helloWorld = onRequest((req, res) => {
  res.json({ message: 'Hello from Firebase!' });
});
```

### With CORS

```typescript
import { onRequest } from 'firebase-functions/v2/https';

export const api = onRequest({ cors: true }, (req, res) => {
  res.json({ data: 'response' });
});

// Specific origins
export const apiRestricted = onRequest({
  cors: ['https://myapp.com', 'https://staging.myapp.com'],
}, (req, res) => {
  res.json({ data: 'response' });
});
```

### Express App

```typescript
import { onRequest } from 'firebase-functions/v2/https';
import express from 'express';

const app = express();

app.use(express.json());

app.get('/users', (req, res) => {
  res.json({ users: [] });
});

app.post('/users', (req, res) => {
  res.status(201).json({ id: '123' });
});

export const api = onRequest(app);
```

### With Authentication

```typescript
import { onRequest, HttpsError } from 'firebase-functions/v2/https';
import { getAuth } from 'firebase-admin/auth';

export const protectedEndpoint = onRequest(async (req, res) => {
  const authHeader = req.headers.authorization;

  if (!authHeader?.startsWith('Bearer ')) {
    res.status(401).json({ error: 'Unauthorized' });
    return;
  }

  try {
    const token = authHeader.split('Bearer ')[1];
    const decoded = await getAuth().verifyIdToken(token);

    // Access user info
    res.json({ uid: decoded.uid });
  } catch {
    res.status(401).json({ error: 'Invalid token' });
  }
});
```

## Firestore Triggers

### Document Created

```typescript
import { onDocumentCreated } from 'firebase-functions/v2/firestore';
import { getFirestore } from 'firebase-admin/firestore';

export const onUserCreated = onDocumentCreated(
  'users/{userId}',
  async (event) => {
    const snapshot = event.data;
    if (!snapshot) return;

    const userData = snapshot.data();
    const userId = event.params.userId;

    // Create related documents
    await getFirestore().collection('profiles').doc(userId).set({
      displayName: userData.displayName,
      createdAt: new Date(),
    });
  }
);
```

### Document Updated

```typescript
import { onDocumentUpdated } from 'firebase-functions/v2/firestore';

export const onOrderUpdated = onDocumentUpdated(
  'orders/{orderId}',
  async (event) => {
    const before = event.data?.before.data();
    const after = event.data?.after.data();

    if (!before || !after) return;

    // Check if status changed
    if (before.status !== after.status) {
      console.log(`Order ${event.params.orderId} status: ${before.status} -> ${after.status}`);

      // Send notification, update analytics, etc.
    }
  }
);
```

### Document Deleted

```typescript
import { onDocumentDeleted } from 'firebase-functions/v2/firestore';

export const onUserDeleted = onDocumentDeleted(
  'users/{userId}',
  async (event) => {
    const userId = event.params.userId;

    // Cleanup related data
    const batch = getFirestore().batch();

    const profileRef = getFirestore().collection('profiles').doc(userId);
    batch.delete(profileRef);

    // Delete user's posts
    const posts = await getFirestore()
      .collection('posts')
      .where('authorId', '==', userId)
      .get();

    posts.docs.forEach(doc => batch.delete(doc.ref));

    await batch.commit();
  }
);
```

### Document Written (Create/Update/Delete)

```typescript
import { onDocumentWritten } from 'firebase-functions/v2/firestore';

export const onDocumentChange = onDocumentWritten(
  'items/{itemId}',
  async (event) => {
    const before = event.data?.before.exists ? event.data.before.data() : null;
    const after = event.data?.after.exists ? event.data.after.data() : null;

    if (!before && after) {
      console.log('Document created');
    } else if (before && !after) {
      console.log('Document deleted');
    } else if (before && after) {
      console.log('Document updated');
    }
  }
);
```

## Auth Triggers

### User Created

```typescript
import { beforeUserCreated, beforeUserSignedIn } from 'firebase-functions/v2/identity';

export const beforeCreate = beforeUserCreated(async (event) => {
  const user = event.data;

  // Block disposable emails
  if (user.email?.endsWith('@tempmail.com')) {
    throw new Error('Disposable emails not allowed');
  }

  // Set custom claims
  return {
    customClaims: {
      role: 'user',
      createdVia: 'signup',
    },
  };
});

export const beforeSignIn = beforeUserSignedIn(async (event) => {
  const user = event.data;

  // Check if user is banned
  const userDoc = await getFirestore().collection('users').doc(user.uid).get();
  if (userDoc.exists && userDoc.data()?.banned) {
    throw new Error('Account has been suspended');
  }
});
```

## Storage Triggers

### File Uploaded

```typescript
import { onObjectFinalized } from 'firebase-functions/v2/storage';
import { getStorage } from 'firebase-admin/storage';
import sharp from 'sharp';

export const generateThumbnail = onObjectFinalized(async (event) => {
  const filePath = event.data.name;
  const contentType = event.data.contentType;

  // Only process images
  if (!contentType?.startsWith('image/')) return;

  // Skip if already a thumbnail
  if (filePath.includes('_thumb')) return;

  const bucket = getStorage().bucket(event.data.bucket);
  const [buffer] = await bucket.file(filePath).download();

  const thumbnail = await sharp(buffer)
    .resize(200, 200, { fit: 'cover' })
    .toBuffer();

  const thumbPath = filePath.replace(/(\.[^.]+)$/, '_thumb$1');
  await bucket.file(thumbPath).save(thumbnail, {
    contentType,
  });
});
```

### File Deleted

```typescript
import { onObjectDeleted } from 'firebase-functions/v2/storage';

export const cleanupThumbnail = onObjectDeleted(async (event) => {
  const filePath = event.data.name;

  // If original deleted, delete thumbnail too
  if (!filePath.includes('_thumb')) {
    const thumbPath = filePath.replace(/(\.[^.]+)$/, '_thumb$1');
    try {
      await getStorage().bucket(event.data.bucket).file(thumbPath).delete();
    } catch {
      // Thumbnail may not exist
    }
  }
});
```

## Scheduled Functions

### Cron Schedule

```typescript
import { onSchedule } from 'firebase-functions/v2/scheduler';

// Every day at midnight
export const dailyCleanup = onSchedule('0 0 * * *', async () => {
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - 30);

  const oldDocs = await getFirestore()
    .collection('logs')
    .where('createdAt', '<', cutoff)
    .limit(500)
    .get();

  const batch = getFirestore().batch();
  oldDocs.docs.forEach(doc => batch.delete(doc.ref));
  await batch.commit();
});

// Every hour
export const hourlySync = onSchedule('0 * * * *', async () => {
  // Sync data, send reports, etc.
});

// Every 5 minutes
export const frequentCheck = onSchedule('*/5 * * * *', async () => {
  // Health checks, monitoring, etc.
});
```

### With Timezone

```typescript
export const dailyReport = onSchedule({
  schedule: '0 9 * * *', // 9 AM
  timeZone: 'America/New_York',
}, async () => {
  // Generate and send daily report
});
```

## Callable Functions

### Basic Callable

```typescript
import { onCall, HttpsError } from 'firebase-functions/v2/https';

interface CreateOrderRequest {
  items: { productId: string; quantity: number }[];
}

interface CreateOrderResponse {
  orderId: string;
  total: number;
}

export const createOrder = onCall<CreateOrderRequest>(async (request) => {
  // Auth check
  if (!request.auth) {
    throw new HttpsError('unauthenticated', 'Must be logged in');
  }

  const { items } = request.data;

  if (!items?.length) {
    throw new HttpsError('invalid-argument', 'Items required');
  }

  // Create order
  const orderRef = await getFirestore().collection('orders').add({
    userId: request.auth.uid,
    items,
    status: 'pending',
    createdAt: new Date(),
  });

  return {
    orderId: orderRef.id,
    total: 100, // Calculate actual total
  } as CreateOrderResponse;
});
```

### Call from Client

```typescript
// Client-side
import { getFunctions, httpsCallable } from 'firebase/functions';

const functions = getFunctions();
const createOrder = httpsCallable(functions, 'createOrder');

const result = await createOrder({
  items: [{ productId: 'prod-1', quantity: 2 }],
});

console.log(result.data.orderId);
```

## Best Practices

### Cold Start Optimization

```typescript
// Initialize at module level
import { initializeApp } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';

initializeApp();
const db = getFirestore();

// Lazy load heavy dependencies
let sharp: typeof import('sharp') | null = null;

async function getSharp() {
  if (!sharp) {
    sharp = await import('sharp');
  }
  return sharp;
}
```

### Error Handling

```typescript
import { logger } from 'firebase-functions';

export const safeFunction = onRequest(async (req, res) => {
  try {
    // Your logic
    res.json({ success: true });
  } catch (error) {
    logger.error('Function failed', { error, requestId: req.headers['x-request-id'] });

    if (error instanceof HttpsError) {
      res.status(400).json({ error: error.message });
    } else {
      res.status(500).json({ error: 'Internal server error' });
    }
  }
});
```

### Resource Configuration

```typescript
export const heavyFunction = onRequest({
  memory: '1GiB',
  timeoutSeconds: 300,
  minInstances: 1, // Avoid cold starts
  maxInstances: 10,
  concurrency: 80,
}, async (req, res) => {
  // Heavy processing
});
```

### Secrets

```typescript
import { defineSecret } from 'firebase-functions/params';

const apiKey = defineSecret('API_KEY');

export const withSecret = onRequest(
  { secrets: [apiKey] },
  async (req, res) => {
    const key = apiKey.value();
    // Use the secret
  }
);
```
