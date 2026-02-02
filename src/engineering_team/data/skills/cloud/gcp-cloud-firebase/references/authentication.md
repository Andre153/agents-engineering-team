# Firebase Authentication

## Table of Contents
- [Admin SDK Operations](#admin-sdk-operations)
- [Token Verification](#token-verification)
- [Custom Claims](#custom-claims)
- [User Management](#user-management)
- [Multi-tenancy](#multi-tenancy)
- [Security Patterns](#security-patterns)

## Admin SDK Operations

### Initialize Auth

```typescript
import { initializeApp, cert } from 'firebase-admin/app';
import { getAuth } from 'firebase-admin/auth';

initializeApp({
  credential: cert({
    projectId: process.env.FIREBASE_PROJECT_ID,
    clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
    privateKey: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
  }),
});

export const auth = getAuth();
```

## Token Verification

### Basic Verification

```typescript
import { getAuth, DecodedIdToken } from 'firebase-admin/auth';

async function verifyToken(idToken: string): Promise<DecodedIdToken> {
  return getAuth().verifyIdToken(idToken);
}

// Usage
const decoded = await verifyToken(token);
console.log(decoded.uid, decoded.email);
```

### Express Middleware

```typescript
import { Request, Response, NextFunction } from 'express';
import { getAuth, DecodedIdToken } from 'firebase-admin/auth';

interface AuthRequest extends Request {
  user?: DecodedIdToken;
}

export async function requireAuth(
  req: AuthRequest,
  res: Response,
  next: NextFunction
): Promise<void> {
  const authHeader = req.headers.authorization;

  if (!authHeader?.startsWith('Bearer ')) {
    res.status(401).json({ error: 'Missing authorization header' });
    return;
  }

  const token = authHeader.substring(7);

  try {
    req.user = await getAuth().verifyIdToken(token);
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid or expired token' });
  }
}

// Optional auth (sets user if present, continues if not)
export async function optionalAuth(
  req: AuthRequest,
  res: Response,
  next: NextFunction
): Promise<void> {
  const authHeader = req.headers.authorization;

  if (authHeader?.startsWith('Bearer ')) {
    try {
      req.user = await getAuth().verifyIdToken(authHeader.substring(7));
    } catch {
      // Ignore invalid tokens for optional auth
    }
  }

  next();
}
```

### Check Token Revocation

```typescript
async function verifyTokenStrict(idToken: string): Promise<DecodedIdToken> {
  // checkRevoked: true adds latency but ensures token hasn't been revoked
  return getAuth().verifyIdToken(idToken, true);
}
```

### Session Cookie

```typescript
// Create session cookie (for server-side sessions)
async function createSessionCookie(idToken: string, expiresIn: number = 60 * 60 * 24 * 5 * 1000) {
  return getAuth().createSessionCookie(idToken, { expiresIn });
}

// Verify session cookie
async function verifySessionCookie(sessionCookie: string) {
  return getAuth().verifySessionCookie(sessionCookie, true);
}

// Express middleware for session cookies
async function requireSessionAuth(req: Request, res: Response, next: NextFunction) {
  const sessionCookie = req.cookies.session;

  if (!sessionCookie) {
    return res.status(401).json({ error: 'No session' });
  }

  try {
    req.user = await getAuth().verifySessionCookie(sessionCookie, true);
    next();
  } catch {
    res.status(401).json({ error: 'Invalid session' });
  }
}
```

## Custom Claims

### Set Custom Claims

```typescript
import { getAuth } from 'firebase-admin/auth';

// Set role-based claims
async function setUserRole(uid: string, role: 'admin' | 'editor' | 'viewer') {
  await getAuth().setCustomUserClaims(uid, { role });
}

// Set organization access
async function setOrganizationAccess(uid: string, orgId: string, role: string) {
  const user = await getAuth().getUser(uid);
  const existingClaims = user.customClaims || {};

  await getAuth().setCustomUserClaims(uid, {
    ...existingClaims,
    organizationId: orgId,
    organizationRole: role,
  });
}

// Clear claims
async function clearCustomClaims(uid: string) {
  await getAuth().setCustomUserClaims(uid, null);
}
```

### Access Claims in Security Rules

```javascript
// Firestore rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    function hasRole(role) {
      return request.auth.token.role == role;
    }

    function isOrgMember(orgId) {
      return request.auth.token.organizationId == orgId;
    }

    match /admin/{document=**} {
      allow read, write: if hasRole('admin');
    }

    match /organizations/{orgId}/{document=**} {
      allow read: if isOrgMember(orgId);
      allow write: if isOrgMember(orgId) && request.auth.token.organizationRole == 'admin';
    }
  }
}
```

### Role-Based Middleware

```typescript
type Role = 'admin' | 'editor' | 'viewer';

function requireRole(...roles: Role[]) {
  return async (req: AuthRequest, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    const userRole = req.user.role as Role | undefined;

    if (!userRole || !roles.includes(userRole)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    next();
  };
}

// Usage
app.delete('/users/:id', requireAuth, requireRole('admin'), deleteUser);
app.put('/posts/:id', requireAuth, requireRole('admin', 'editor'), updatePost);
```

## User Management

### Create User

```typescript
async function createUser(email: string, password: string, displayName?: string) {
  return getAuth().createUser({
    email,
    password,
    displayName,
    emailVerified: false,
  });
}

// With custom UID
async function createUserWithUid(uid: string, email: string) {
  return getAuth().createUser({ uid, email });
}
```

### Get User

```typescript
// By UID
const user = await getAuth().getUser(uid);

// By email
const user = await getAuth().getUserByEmail(email);

// By phone
const user = await getAuth().getUserByPhoneNumber(phoneNumber);

// Multiple users
const result = await getAuth().getUsers([
  { uid: 'uid1' },
  { email: 'user@example.com' },
]);
```

### Update User

```typescript
async function updateUser(uid: string, updates: {
  email?: string;
  displayName?: string;
  photoURL?: string;
  disabled?: boolean;
  emailVerified?: boolean;
}) {
  return getAuth().updateUser(uid, updates);
}

// Disable user
await getAuth().updateUser(uid, { disabled: true });

// Change email
await getAuth().updateUser(uid, { email: 'new@email.com' });
```

### Delete User

```typescript
// Single user
await getAuth().deleteUser(uid);

// Multiple users
await getAuth().deleteUsers([uid1, uid2, uid3]);
```

### List Users

```typescript
async function listAllUsers(pageToken?: string): Promise<void> {
  const listResult = await getAuth().listUsers(1000, pageToken);

  listResult.users.forEach(user => {
    console.log(user.uid, user.email);
  });

  if (listResult.pageToken) {
    await listAllUsers(listResult.pageToken);
  }
}
```

### Revoke Tokens

```typescript
// Revoke all refresh tokens for a user
await getAuth().revokeRefreshTokens(uid);

// After revoking, existing ID tokens remain valid until expiration
// Use checkRevoked: true in verifyIdToken to enforce immediately
```

## Multi-tenancy

### Tenant-Aware Auth

```typescript
import { getAuth } from 'firebase-admin/auth';

// Get tenant-specific auth
const tenantAuth = getAuth().tenantManager().authForTenant('tenant-id');

// Verify token for specific tenant
const decoded = await tenantAuth.verifyIdToken(idToken);

// Create user in tenant
const user = await tenantAuth.createUser({ email, password });
```

### Tenant Middleware

```typescript
function requireTenantAuth(tenantId: string) {
  return async (req: AuthRequest, res: Response, next: NextFunction) => {
    const token = req.headers.authorization?.substring(7);

    if (!token) {
      return res.status(401).json({ error: 'No token' });
    }

    try {
      const tenantAuth = getAuth().tenantManager().authForTenant(tenantId);
      req.user = await tenantAuth.verifyIdToken(token);
      next();
    } catch {
      res.status(401).json({ error: 'Invalid token' });
    }
  };
}
```

## Security Patterns

### Rate Limiting Failed Auth

```typescript
import { RateLimiterMemory } from 'rate-limiter-flexible';

const authLimiter = new RateLimiterMemory({
  points: 5, // 5 attempts
  duration: 60 * 15, // per 15 minutes
});

async function loginWithRateLimit(email: string, password: string, ip: string) {
  const key = `${email}_${ip}`;

  try {
    await authLimiter.consume(key);
  } catch {
    throw new Error('Too many login attempts');
  }

  // Proceed with authentication...
}
```

### Secure Token Handling

```typescript
// Always use HTTPS in production

// Short-lived tokens
const TOKEN_EXPIRY = 60 * 60; // 1 hour

// Refresh before expiry
function shouldRefreshToken(decoded: DecodedIdToken): boolean {
  const expiresAt = decoded.exp * 1000;
  const refreshThreshold = 5 * 60 * 1000; // 5 minutes before expiry
  return Date.now() > expiresAt - refreshThreshold;
}
```

### Audit Logging

```typescript
async function logAuthEvent(event: {
  type: 'login' | 'logout' | 'token_refresh' | 'password_change';
  uid: string;
  ip: string;
  userAgent: string;
  success: boolean;
  error?: string;
}) {
  await db.collection('auth_logs').add({
    ...event,
    timestamp: new Date(),
  });
}
```
