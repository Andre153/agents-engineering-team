---
name: gcp-cloud-firebase
description: "Google Cloud Platform and Firebase development including Cloud Run, Firestore, Firebase Authentication, Cloud Storage, Cloud Functions, and Firebase Hosting. Use when building serverless backends, Firebase applications, or deploying to GCP."
---

# GCP & Firebase Development

## Quick Reference

| Service | Use Case | Reference |
|---------|----------|-----------|
| Cloud Run | Container-based APIs, microservices | See [cloud-run.md](references/cloud-run.md) |
| Firebase Auth | User authentication, identity | See [authentication.md](references/authentication.md) |
| Cloud Storage | File uploads, static assets, media | See [storage.md](references/storage.md) |
| Cloud Functions | Event-driven functions, triggers | See [functions.md](references/functions.md) |
| Firebase Hosting | Static sites, CDN, custom domains | See [hosting.md](references/hosting.md) |

For Firestore patterns, see the `database-firestore` skill.

## Project Structure

### Firebase + Cloud Run Project

```
project/
├── firebase.json              # Firebase configuration
├── .firebaserc                # Project aliases
├── firestore.rules            # Security rules
├── firestore.indexes.json     # Composite indexes
├── storage.rules              # Storage security rules
├── functions/                 # Cloud Functions
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── index.ts
│       └── triggers/
├── services/                  # Cloud Run services
│   └── api/
│       ├── Dockerfile
│       ├── package.json
│       └── src/
└── hosting/                   # Static frontend
    └── public/
```

### firebase.json

```json
{
  "firestore": {
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  },
  "hosting": {
    "public": "hosting/public",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [
      {
        "source": "/api/**",
        "run": {
          "serviceId": "api",
          "region": "us-central1"
        }
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  },
  "storage": {
    "rules": "storage.rules"
  },
  "functions": {
    "source": "functions",
    "runtime": "nodejs20"
  }
}
```

## Firebase Admin SDK

### Initialization

```typescript
import { initializeApp, cert, getApps } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';
import { getAuth } from 'firebase-admin/auth';
import { getStorage } from 'firebase-admin/storage';

// Initialize once
if (getApps().length === 0) {
  initializeApp({
    credential: cert({
      projectId: process.env.FIREBASE_PROJECT_ID,
      clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
      privateKey: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
    }),
    storageBucket: `${process.env.FIREBASE_PROJECT_ID}.appspot.com`,
  });
}

export const db = getFirestore();
export const auth = getAuth();
export const storage = getStorage();
```

### Environment Variables

```bash
# Required for Firebase Admin SDK
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@project.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"

# Optional
GOOGLE_CLOUD_PROJECT=your-project-id
GCLOUD_PROJECT=your-project-id
```

## Cloud Run Essentials

### Dockerfile

```dockerfile
FROM node:20-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-slim
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./

ENV NODE_ENV=production
ENV PORT=8080
EXPOSE 8080

CMD ["node", "dist/main.js"]
```

### Deployment

```bash
# Build and deploy
gcloud run deploy api \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "FIREBASE_PROJECT_ID=your-project"

# Deploy with service account
gcloud run deploy api \
  --source . \
  --region us-central1 \
  --service-account api-service@project.iam.gserviceaccount.com
```

### Health Check Endpoint

```typescript
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy', timestamp: new Date().toISOString() });
});
```

## Authentication Pattern

### Verify Firebase Token (Middleware)

```typescript
import { getAuth } from 'firebase-admin/auth';

interface AuthenticatedRequest extends Request {
  user?: {
    uid: string;
    email?: string;
    emailVerified: boolean;
    customClaims?: Record<string, unknown>;
  };
}

async function authMiddleware(
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
) {
  const authHeader = req.headers.authorization;

  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing authorization header' });
  }

  const token = authHeader.split('Bearer ')[1];

  try {
    const decoded = await getAuth().verifyIdToken(token);
    req.user = {
      uid: decoded.uid,
      email: decoded.email,
      emailVerified: decoded.email_verified ?? false,
      customClaims: decoded,
    };
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}
```

### Custom Claims

```typescript
// Set custom claims (admin only operation)
await getAuth().setCustomUserClaims(uid, {
  role: 'admin',
  organizationId: 'org-123',
});

// Access in security rules
// request.auth.token.role == 'admin'
```

## Security Rules Pattern

### Firestore Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Helper functions
    function isAuthenticated() {
      return request.auth != null;
    }

    function isOwner(userId) {
      return request.auth.uid == userId;
    }

    function hasRole(role) {
      return request.auth.token.role == role;
    }

    // Users collection
    match /users/{userId} {
      allow read: if isAuthenticated() && isOwner(userId);
      allow create: if isAuthenticated() && isOwner(userId);
      allow update: if isAuthenticated() && isOwner(userId);
      allow delete: if false; // Soft delete only
    }

    // Organization-scoped data
    match /organizations/{orgId}/{document=**} {
      allow read, write: if isAuthenticated()
        && request.auth.token.organizationId == orgId;
    }
  }
}
```

### Storage Rules

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    function isAuthenticated() {
      return request.auth != null;
    }

    function isOwner(userId) {
      return request.auth.uid == userId;
    }

    function isValidImage() {
      return request.resource.contentType.matches('image/.*')
        && request.resource.size < 5 * 1024 * 1024; // 5MB
    }

    // User uploads
    match /users/{userId}/{allPaths=**} {
      allow read: if isAuthenticated();
      allow write: if isOwner(userId) && isValidImage();
    }

    // Public assets
    match /public/{allPaths=**} {
      allow read: if true;
      allow write: if false;
    }
  }
}
```

## Common Patterns

### Pagination

```typescript
import { getFirestore, Query, DocumentSnapshot } from 'firebase-admin/firestore';

interface PaginatedResult<T> {
  items: T[];
  nextCursor?: string;
  hasMore: boolean;
}

async function paginate<T>(
  query: Query,
  limit: number,
  cursor?: string
): Promise<PaginatedResult<T>> {
  let q = query.limit(limit + 1);

  if (cursor) {
    const cursorDoc = await getFirestore().doc(cursor).get();
    q = q.startAfter(cursorDoc);
  }

  const snapshot = await q.get();
  const docs = snapshot.docs;
  const hasMore = docs.length > limit;

  if (hasMore) docs.pop();

  return {
    items: docs.map(doc => ({ id: doc.id, ...doc.data() } as T)),
    nextCursor: hasMore ? docs[docs.length - 1].ref.path : undefined,
    hasMore,
  };
}
```

### Batch Operations

```typescript
const db = getFirestore();
const batch = db.batch();

// Add multiple operations
items.forEach(item => {
  const ref = db.collection('items').doc();
  batch.set(ref, { ...item, createdAt: new Date() });
});

// Commit (max 500 operations per batch)
await batch.commit();
```

### Transaction

```typescript
const db = getFirestore();

await db.runTransaction(async (transaction) => {
  const docRef = db.collection('counters').doc('visits');
  const doc = await transaction.get(docRef);

  if (!doc.exists) {
    transaction.set(docRef, { count: 1 });
  } else {
    transaction.update(docRef, { count: doc.data()!.count + 1 });
  }
});
```

## Deployment Checklist

### Pre-deployment
- [ ] Security rules reviewed and tested
- [ ] Indexes created for all queries
- [ ] Environment variables configured
- [ ] Service account permissions set
- [ ] Error monitoring configured (Cloud Error Reporting)

### Cloud Run
- [ ] Health check endpoint works
- [ ] Container starts in < 10 seconds
- [ ] Memory and CPU limits appropriate
- [ ] Min/max instances configured
- [ ] Request timeout set

### Firebase
- [ ] `firebase deploy --only firestore:rules`
- [ ] `firebase deploy --only storage`
- [ ] `firebase deploy --only hosting`
- [ ] `firebase deploy --only functions`

See reference files for detailed patterns and examples.
