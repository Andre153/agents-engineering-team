# Firestore Security Rules

## Table of Contents
- [Rule Structure](#rule-structure)
- [Authentication](#authentication)
- [Data Validation](#data-validation)
- [Role-Based Access](#role-based-access)
- [Common Patterns](#common-patterns)
- [Testing Rules](#testing-rules)

## Rule Structure

### Basic Structure

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Rules go here
  }
}
```

### Match Patterns

```javascript
// Single document
match /users/{userId} {
  allow read, write: if true;
}

// Subcollection
match /users/{userId}/posts/{postId} {
  allow read: if true;
}

// Recursive wildcard (all nested documents)
match /users/{userId}/{document=**} {
  allow read: if true;
}

// Collection group
match /{path=**}/comments/{commentId} {
  allow read: if true;
}
```

### Operations

```javascript
match /users/{userId} {
  // Granular operations
  allow get: if true;      // Single document read
  allow list: if true;     // Collection query
  allow create: if true;   // New document
  allow update: if true;   // Existing document
  allow delete: if true;   // Remove document

  // Combined operations
  allow read: if true;     // get + list
  allow write: if true;    // create + update + delete
}
```

## Authentication

### Basic Auth Check

```javascript
function isAuthenticated() {
  return request.auth != null;
}

function isOwner(userId) {
  return request.auth.uid == userId;
}

match /users/{userId} {
  allow read: if isAuthenticated();
  allow write: if isOwner(userId);
}
```

### Email Verification

```javascript
function isEmailVerified() {
  return request.auth.token.email_verified == true;
}

match /verified-only/{docId} {
  allow read, write: if isAuthenticated() && isEmailVerified();
}
```

### Auth Provider

```javascript
function signedInWith(provider) {
  return request.auth.token.firebase.sign_in_provider == provider;
}

match /social-users/{userId} {
  allow create: if signedInWith('google.com') || signedInWith('github.com');
}
```

## Data Validation

### Field Validation

```javascript
function isValidUser() {
  let data = request.resource.data;
  return data.keys().hasAll(['name', 'email', 'createdAt'])
    && data.name is string
    && data.name.size() >= 2
    && data.name.size() <= 100
    && data.email is string
    && data.email.matches('.*@.*\\..*')
    && data.createdAt is timestamp;
}

match /users/{userId} {
  allow create: if isOwner(userId) && isValidUser();
}
```

### Update Validation

```javascript
function isValidUpdate() {
  let data = request.resource.data;
  let prev = resource.data;

  // Cannot change these fields
  return data.id == prev.id
    && data.createdAt == prev.createdAt
    && data.authorId == prev.authorId
    // Must update timestamp
    && data.updatedAt > prev.updatedAt;
}

match /posts/{postId} {
  allow update: if isOwner(resource.data.authorId) && isValidUpdate();
}
```

### Field Type Validation

```javascript
function validateTypes(data) {
  return data.title is string
    && data.price is number
    && data.price > 0
    && data.tags is list
    && data.tags.size() <= 10
    && data.metadata is map
    && data.active is bool;
}

match /products/{productId} {
  allow create: if validateTypes(request.resource.data);
}
```

### Immutable Fields

```javascript
function fieldNotChanged(field) {
  return !request.resource.data.diff(resource.data).affectedKeys().hasAny([field]);
}

function immutableFields() {
  return fieldNotChanged('id')
    && fieldNotChanged('createdAt')
    && fieldNotChanged('authorId');
}

match /documents/{docId} {
  allow update: if immutableFields();
}
```

## Role-Based Access

### Custom Claims

```javascript
function hasRole(role) {
  return request.auth.token.role == role;
}

function hasAnyRole(roles) {
  return request.auth.token.role in roles;
}

function isAdmin() {
  return hasRole('admin');
}

match /admin-only/{docId} {
  allow read, write: if isAdmin();
}

match /content/{docId} {
  allow read: if true;
  allow write: if hasAnyRole(['admin', 'editor']);
}
```

### Organization-Based Access

```javascript
function isOrgMember(orgId) {
  return request.auth.token.organizationId == orgId;
}

function isOrgAdmin(orgId) {
  return isOrgMember(orgId) && request.auth.token.organizationRole == 'admin';
}

match /organizations/{orgId} {
  allow read: if isOrgMember(orgId);
  allow write: if isOrgAdmin(orgId);

  match /projects/{projectId} {
    allow read, write: if isOrgMember(orgId);
  }

  match /settings/{settingId} {
    allow read: if isOrgMember(orgId);
    allow write: if isOrgAdmin(orgId);
  }
}
```

### Document-Based Roles

```javascript
// Check roles stored in document
match /teams/{teamId} {
  function getTeamData() {
    return get(/databases/$(database)/documents/teams/$(teamId)).data;
  }

  function isTeamMember() {
    return request.auth.uid in getTeamData().memberIds;
  }

  function isTeamAdmin() {
    return request.auth.uid in getTeamData().adminIds;
  }

  allow read: if isTeamMember();
  allow write: if isTeamAdmin();
}
```

## Common Patterns

### User Profile

```javascript
match /users/{userId} {
  allow read: if isAuthenticated();
  allow create: if isOwner(userId)
    && request.resource.data.keys().hasAll(['name', 'email', 'createdAt'])
    && request.resource.data.name is string
    && request.resource.data.name.size() <= 100;
  allow update: if isOwner(userId)
    && !request.resource.data.diff(resource.data).affectedKeys().hasAny(['uid', 'createdAt']);
  allow delete: if false; // Soft delete only
}
```

### Posts with Comments

```javascript
match /posts/{postId} {
  allow read: if resource.data.status == 'published' || isOwner(resource.data.authorId);
  allow create: if isAuthenticated()
    && request.resource.data.authorId == request.auth.uid;
  allow update: if isOwner(resource.data.authorId) || isAdmin();
  allow delete: if isOwner(resource.data.authorId) || isAdmin();

  match /comments/{commentId} {
    allow read: if true;
    allow create: if isAuthenticated()
      && request.resource.data.authorId == request.auth.uid;
    allow update: if isOwner(resource.data.authorId);
    allow delete: if isOwner(resource.data.authorId)
      || isOwner(get(/databases/$(database)/documents/posts/$(postId)).data.authorId);
  }
}
```

### Rate Limiting (Basic)

```javascript
// Check timestamp of last action
function rateLimit(seconds) {
  let lastAction = get(/databases/$(database)/documents/rate_limits/$(request.auth.uid)).data.lastAction;
  return lastAction == null || request.time > lastAction + duration.value(seconds, 's');
}

match /messages/{messageId} {
  allow create: if isAuthenticated() && rateLimit(5); // 5 seconds between messages
}
```

### Soft Delete

```javascript
match /items/{itemId} {
  // Only show non-deleted items
  allow read: if resource.data.isDeleted != true;

  // Soft delete only
  allow delete: if false;

  // Allow setting isDeleted flag
  allow update: if isOwner(resource.data.ownerId)
    && request.resource.data.diff(resource.data).affectedKeys().hasOnly(['isDeleted', 'deletedAt'])
    && request.resource.data.isDeleted == true
    && request.resource.data.deletedAt is timestamp;
}
```

### Read-Only for Non-Owners

```javascript
match /public-data/{docId} {
  allow read: if true;
  allow write: if isAdmin();
}

match /user-data/{userId}/{document=**} {
  allow read: if isAuthenticated();
  allow write: if isOwner(userId);
}
```

## Testing Rules

### Emulator Testing

```typescript
import { assertFails, assertSucceeds, initializeTestEnvironment } from '@firebase/rules-unit-testing';

let testEnv: RulesTestEnvironment;

beforeAll(async () => {
  testEnv = await initializeTestEnvironment({
    projectId: 'test-project',
    firestore: {
      rules: fs.readFileSync('firestore.rules', 'utf8'),
    },
  });
});

afterAll(async () => {
  await testEnv.cleanup();
});

beforeEach(async () => {
  await testEnv.clearFirestore();
});

test('allows user to read own document', async () => {
  const userId = 'user-123';
  const db = testEnv.authenticatedContext(userId).firestore();

  await assertSucceeds(db.collection('users').doc(userId).get());
});

test('denies user from reading other user document', async () => {
  const db = testEnv.authenticatedContext('user-1').firestore();

  await assertFails(db.collection('users').doc('user-2').get());
});

test('denies unauthenticated access', async () => {
  const db = testEnv.unauthenticatedContext().firestore();

  await assertFails(db.collection('users').doc('any').get());
});

test('validates data on create', async () => {
  const db = testEnv.authenticatedContext('user-1').firestore();

  // Valid data
  await assertSucceeds(
    db.collection('posts').add({
      title: 'Test',
      authorId: 'user-1',
      createdAt: new Date(),
    })
  );

  // Invalid data (missing title)
  await assertFails(
    db.collection('posts').add({
      authorId: 'user-1',
      createdAt: new Date(),
    })
  );
});

test('allows admin access with custom claims', async () => {
  const db = testEnv.authenticatedContext('admin-1', { role: 'admin' }).firestore();

  await assertSucceeds(db.collection('admin-only').doc('test').get());
});
```

### Run Tests

```bash
# Start emulator
firebase emulators:start --only firestore

# Run tests
npm test
```

### Deploy Rules

```bash
# Deploy rules only
firebase deploy --only firestore:rules

# Preview changes
firebase firestore:rules:get
```
