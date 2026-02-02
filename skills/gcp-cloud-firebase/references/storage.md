# Cloud Storage for Firebase

## Table of Contents
- [Admin SDK Setup](#admin-sdk-setup)
- [Upload Files](#upload-files)
- [Download Files](#download-files)
- [Signed URLs](#signed-urls)
- [File Metadata](#file-metadata)
- [Security Rules](#security-rules)
- [Common Patterns](#common-patterns)

## Admin SDK Setup

```typescript
import { initializeApp, cert } from 'firebase-admin/app';
import { getStorage } from 'firebase-admin/storage';

initializeApp({
  credential: cert(serviceAccount),
  storageBucket: 'your-project.appspot.com',
});

const bucket = getStorage().bucket();
```

## Upload Files

### Upload from Buffer

```typescript
async function uploadBuffer(
  buffer: Buffer,
  destination: string,
  contentType: string
): Promise<string> {
  const file = bucket.file(destination);

  await file.save(buffer, {
    contentType,
    metadata: {
      cacheControl: 'public, max-age=31536000',
    },
  });

  return `gs://${bucket.name}/${destination}`;
}

// Usage
const imageBuffer = Buffer.from(base64Data, 'base64');
await uploadBuffer(imageBuffer, 'images/photo.jpg', 'image/jpeg');
```

### Upload from Stream

```typescript
import { Readable } from 'stream';

async function uploadStream(
  stream: Readable,
  destination: string,
  contentType: string
): Promise<void> {
  const file = bucket.file(destination);
  const writeStream = file.createWriteStream({
    contentType,
    resumable: false,
  });

  return new Promise((resolve, reject) => {
    stream
      .pipe(writeStream)
      .on('error', reject)
      .on('finish', resolve);
  });
}
```

### Upload from Express Request

```typescript
import multer from 'multer';

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB
});

app.post('/upload', upload.single('file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  const { buffer, originalname, mimetype } = req.file;
  const destination = `uploads/${Date.now()}-${originalname}`;

  await bucket.file(destination).save(buffer, {
    contentType: mimetype,
  });

  res.json({ path: destination });
});
```

### Upload with Progress

```typescript
import { createWriteStream } from 'fs';

async function uploadWithProgress(
  localPath: string,
  destination: string,
  onProgress: (progress: number) => void
): Promise<void> {
  const [metadata] = await bucket.upload(localPath, {
    destination,
    onUploadProgress: (event) => {
      const progress = (event.bytesWritten / event.contentLength) * 100;
      onProgress(progress);
    },
  });
}
```

## Download Files

### Download to Buffer

```typescript
async function downloadToBuffer(filePath: string): Promise<Buffer> {
  const [contents] = await bucket.file(filePath).download();
  return contents;
}
```

### Download to Stream

```typescript
function downloadToStream(filePath: string): Readable {
  return bucket.file(filePath).createReadStream();
}

// Express endpoint
app.get('/files/:path', async (req, res) => {
  const file = bucket.file(req.params.path);

  const [exists] = await file.exists();
  if (!exists) {
    return res.status(404).json({ error: 'File not found' });
  }

  const [metadata] = await file.getMetadata();
  res.setHeader('Content-Type', metadata.contentType || 'application/octet-stream');
  res.setHeader('Content-Length', metadata.size);

  file.createReadStream().pipe(res);
});
```

## Signed URLs

### Generate Download URL

```typescript
async function getDownloadUrl(
  filePath: string,
  expiresInMinutes: number = 60
): Promise<string> {
  const [url] = await bucket.file(filePath).getSignedUrl({
    action: 'read',
    expires: Date.now() + expiresInMinutes * 60 * 1000,
  });

  return url;
}
```

### Generate Upload URL

```typescript
async function getUploadUrl(
  filePath: string,
  contentType: string,
  expiresInMinutes: number = 15
): Promise<string> {
  const [url] = await bucket.file(filePath).getSignedUrl({
    action: 'write',
    expires: Date.now() + expiresInMinutes * 60 * 1000,
    contentType,
  });

  return url;
}

// API endpoint for client upload
app.post('/upload-url', requireAuth, async (req, res) => {
  const { filename, contentType } = req.body;
  const path = `users/${req.user.uid}/${Date.now()}-${filename}`;

  const uploadUrl = await getUploadUrl(path, contentType);

  res.json({ uploadUrl, path });
});
```

### Resumable Upload URL

```typescript
async function getResumableUploadUrl(
  filePath: string,
  contentType: string
): Promise<string> {
  const [url] = await bucket.file(filePath).createResumableUpload({
    metadata: { contentType },
  });

  return url;
}
```

## File Metadata

### Get Metadata

```typescript
async function getFileMetadata(filePath: string) {
  const [metadata] = await bucket.file(filePath).getMetadata();
  return {
    name: metadata.name,
    size: metadata.size,
    contentType: metadata.contentType,
    created: metadata.timeCreated,
    updated: metadata.updated,
    md5Hash: metadata.md5Hash,
    customMetadata: metadata.metadata,
  };
}
```

### Set Metadata

```typescript
async function setFileMetadata(filePath: string, metadata: Record<string, string>) {
  await bucket.file(filePath).setMetadata({
    metadata, // Custom metadata
    cacheControl: 'public, max-age=3600',
  });
}
```

### List Files

```typescript
async function listFiles(prefix: string, maxResults: number = 100) {
  const [files] = await bucket.getFiles({
    prefix,
    maxResults,
  });

  return files.map(file => ({
    name: file.name,
    size: file.metadata.size,
  }));
}

// With pagination
async function listFilesWithPagination(prefix: string, pageToken?: string) {
  const [files, , apiResponse] = await bucket.getFiles({
    prefix,
    maxResults: 100,
    pageToken,
  });

  return {
    files: files.map(f => f.name),
    nextPageToken: apiResponse?.nextPageToken,
  };
}
```

## Security Rules

### Basic Rules

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // Helper functions
    function isAuthenticated() {
      return request.auth != null;
    }

    function isOwner(userId) {
      return request.auth.uid == userId;
    }

    function isValidImage() {
      return request.resource.contentType.matches('image/.*');
    }

    function isValidSize(maxMB) {
      return request.resource.size < maxMB * 1024 * 1024;
    }

    // User files
    match /users/{userId}/{allPaths=**} {
      allow read: if isAuthenticated() && isOwner(userId);
      allow write: if isOwner(userId)
        && isValidImage()
        && isValidSize(5);
    }

    // Public files (read-only)
    match /public/{allPaths=**} {
      allow read: if true;
      allow write: if false;
    }
  }
}
```

### Advanced Rules

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    function hasRole(role) {
      return request.auth.token.role == role;
    }

    function isOrganizationMember(orgId) {
      return request.auth.token.organizationId == orgId;
    }

    // Allowed file types
    function isAllowedType() {
      return request.resource.contentType.matches('image/.*')
        || request.resource.contentType.matches('application/pdf')
        || request.resource.contentType.matches('video/.*');
    }

    // Organization files
    match /organizations/{orgId}/{allPaths=**} {
      allow read: if isOrganizationMember(orgId);
      allow write: if isOrganizationMember(orgId)
        && isAllowedType()
        && request.resource.size < 50 * 1024 * 1024;
    }

    // Admin uploads
    match /admin/{allPaths=**} {
      allow read: if true;
      allow write: if hasRole('admin');
    }
  }
}
```

## Common Patterns

### Image Processing Pipeline

```typescript
import sharp from 'sharp';

interface ImageVariant {
  suffix: string;
  width: number;
  height?: number;
}

const variants: ImageVariant[] = [
  { suffix: 'thumb', width: 150, height: 150 },
  { suffix: 'medium', width: 600 },
  { suffix: 'large', width: 1200 },
];

async function processImage(
  sourceBuffer: Buffer,
  basePath: string
): Promise<string[]> {
  const results: string[] = [];

  for (const variant of variants) {
    const processed = await sharp(sourceBuffer)
      .resize(variant.width, variant.height, { fit: 'inside' })
      .jpeg({ quality: 80 })
      .toBuffer();

    const path = `${basePath}_${variant.suffix}.jpg`;
    await bucket.file(path).save(processed, {
      contentType: 'image/jpeg',
    });

    results.push(path);
  }

  return results;
}
```

### Cleanup Old Files

```typescript
async function deleteOldFiles(prefix: string, olderThanDays: number) {
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - olderThanDays);

  const [files] = await bucket.getFiles({ prefix });

  for (const file of files) {
    const [metadata] = await file.getMetadata();
    const created = new Date(metadata.timeCreated);

    if (created < cutoff) {
      await file.delete();
      console.log(`Deleted: ${file.name}`);
    }
  }
}
```

### Copy Between Buckets

```typescript
async function copyFile(
  sourcePath: string,
  destBucket: string,
  destPath: string
) {
  const sourceFile = bucket.file(sourcePath);
  const destinationBucket = getStorage().bucket(destBucket);

  await sourceFile.copy(destinationBucket.file(destPath));
}
```

### File Existence Check

```typescript
async function fileExists(filePath: string): Promise<boolean> {
  const [exists] = await bucket.file(filePath).exists();
  return exists;
}
```
