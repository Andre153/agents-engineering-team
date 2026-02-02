# Cloud Run

## Table of Contents
- [Container Configuration](#container-configuration)
- [Deployment](#deployment)
- [Service Configuration](#service-configuration)
- [Scaling](#scaling)
- [Secrets and Environment](#secrets-and-environment)
- [Networking](#networking)
- [Best Practices](#best-practices)

## Container Configuration

### Production Dockerfile

```dockerfile
# Multi-stage build for smaller images
FROM node:20-slim AS builder

WORKDIR /app

# Install dependencies first (better caching)
COPY package*.json ./
RUN npm ci --only=production

# Copy source and build
COPY . .
RUN npm run build

# Production image
FROM node:20-slim AS production

WORKDIR /app

# Copy only what's needed
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./

# Non-root user for security
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nodeuser
USER nodeuser

# Cloud Run uses PORT env variable
ENV NODE_ENV=production
ENV PORT=8080
EXPOSE 8080

# Start the application
CMD ["node", "dist/main.js"]
```

### Dockerfile with Build Args

```dockerfile
FROM node:20-slim AS builder

ARG NODE_ENV=production
ARG BUILD_VERSION=unknown

WORKDIR /app
COPY . .
RUN npm ci && npm run build

FROM node:20-slim
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules

ENV NODE_ENV=${NODE_ENV}
ENV BUILD_VERSION=${BUILD_VERSION}
ENV PORT=8080

CMD ["node", "dist/main.js"]
```

### .dockerignore

```
node_modules
npm-debug.log
.git
.gitignore
.env*
*.md
tests/
coverage/
.nyc_output/
dist/
Dockerfile
docker-compose*.yml
```

## Deployment

### Basic Deployment

```bash
# Deploy from source (Cloud Build)
gcloud run deploy SERVICE_NAME \
  --source . \
  --region us-central1 \
  --platform managed

# Deploy from container image
gcloud run deploy SERVICE_NAME \
  --image gcr.io/PROJECT_ID/IMAGE_NAME:TAG \
  --region us-central1 \
  --platform managed
```

### Deployment with Options

```bash
gcloud run deploy api \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --service-account api@project.iam.gserviceaccount.com \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 60s \
  --concurrency 80 \
  --set-env-vars "NODE_ENV=production,LOG_LEVEL=info" \
  --set-secrets "DB_PASSWORD=db-password:latest"
```

### Cloud Build Configuration

```yaml
# cloudbuild.yaml
steps:
  # Build the container
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'gcr.io/$PROJECT_ID/api:$COMMIT_SHA'
      - '-t'
      - 'gcr.io/$PROJECT_ID/api:latest'
      - '.'

  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/api:$COMMIT_SHA']

  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'api'
      - '--image'
      - 'gcr.io/$PROJECT_ID/api:$COMMIT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'

images:
  - 'gcr.io/$PROJECT_ID/api:$COMMIT_SHA'
  - 'gcr.io/$PROJECT_ID/api:latest'
```

## Service Configuration

### service.yaml (Declarative)

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: api
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: '0'
        autoscaling.knative.dev/maxScale: '10'
        run.googleapis.com/cpu-throttling: 'false'
    spec:
      containerConcurrency: 80
      timeoutSeconds: 60
      serviceAccountName: api@project.iam.gserviceaccount.com
      containers:
        - image: gcr.io/project/api:latest
          ports:
            - containerPort: 8080
          resources:
            limits:
              memory: 512Mi
              cpu: '1'
          env:
            - name: NODE_ENV
              value: production
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-password
                  key: latest
          startupProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 0
            periodSeconds: 1
            timeoutSeconds: 1
            failureThreshold: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            periodSeconds: 10
```

Deploy with:
```bash
gcloud run services replace service.yaml --region us-central1
```

## Scaling

### Concurrency Settings

```bash
# Requests per container instance
gcloud run services update api \
  --concurrency 80

# CPU always allocated (not throttled between requests)
gcloud run services update api \
  --no-cpu-throttling

# Min instances (avoid cold starts)
gcloud run services update api \
  --min-instances 1

# Max instances (cost control)
gcloud run services update api \
  --max-instances 100
```

### Cold Start Optimization

```typescript
// Pre-initialize connections at module level
import { getFirestore } from 'firebase-admin/firestore';

// Initialize immediately, not on first request
const db = getFirestore();

// Warm connection pools
const warmConnections = async () => {
  await db.collection('_health').limit(1).get();
};

// Call during startup
warmConnections().catch(console.error);
```

## Secrets and Environment

### Using Secret Manager

```bash
# Create secret
echo -n "my-secret-value" | gcloud secrets create db-password --data-file=-

# Grant access to service account
gcloud secrets add-iam-policy-binding db-password \
  --member="serviceAccount:api@project.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Mount as environment variable
gcloud run services update api \
  --set-secrets "DB_PASSWORD=db-password:latest"

# Mount as file
gcloud run services update api \
  --set-secrets "/secrets/db-password=db-password:latest"
```

### Access in Code

```typescript
// As environment variable
const dbPassword = process.env.DB_PASSWORD;

// As file
import { readFileSync } from 'fs';
const dbPassword = readFileSync('/secrets/db-password', 'utf8');
```

## Networking

### VPC Connector (Private Network)

```bash
# Create connector
gcloud compute networks vpc-access connectors create my-connector \
  --region us-central1 \
  --network default \
  --range 10.8.0.0/28

# Attach to Cloud Run
gcloud run services update api \
  --vpc-connector my-connector \
  --vpc-egress all-traffic
```

### Internal Services

```bash
# Internal only (no public access)
gcloud run services update api \
  --ingress internal

# Internal and Cloud Load Balancing
gcloud run services update api \
  --ingress internal-and-cloud-load-balancing
```

### Service-to-Service Auth

```typescript
import { GoogleAuth } from 'google-auth-library';

const auth = new GoogleAuth();

async function callInternalService(url: string) {
  const client = await auth.getIdTokenClient(url);
  const response = await client.request({ url });
  return response.data;
}

// Usage
const result = await callInternalService('https://internal-api-xxxxx-uc.a.run.app/endpoint');
```

## Best Practices

### Startup Time
- Use slim base images (`node:20-slim`)
- Multi-stage builds to reduce image size
- Lazy-load non-critical modules
- Pre-warm database connections

### Resource Limits
```bash
# Right-size for your workload
--memory 256Mi   # Lightweight APIs
--memory 512Mi   # Standard APIs
--memory 1Gi     # Memory-intensive processing
--memory 2Gi     # Heavy processing

--cpu 1          # Standard
--cpu 2          # CPU-intensive
```

### Request Timeout
```bash
# Match to your longest expected request
--timeout 60s    # Standard
--timeout 300s   # File processing
--timeout 900s   # Max (15 minutes)
```

### Health Checks

```typescript
// Comprehensive health check
app.get('/health', async (req, res) => {
  const checks = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.BUILD_VERSION,
    checks: {} as Record<string, boolean>,
  };

  try {
    // Check Firestore
    await db.collection('_health').limit(1).get();
    checks.checks.firestore = true;
  } catch {
    checks.checks.firestore = false;
    checks.status = 'degraded';
  }

  const statusCode = checks.status === 'healthy' ? 200 : 503;
  res.status(statusCode).json(checks);
});
```

### Graceful Shutdown

```typescript
import { getFirestore } from 'firebase-admin/firestore';

const db = getFirestore();

process.on('SIGTERM', async () => {
  console.log('SIGTERM received, shutting down gracefully');

  // Stop accepting new requests
  server.close();

  // Terminate Firestore client
  await db.terminate();

  process.exit(0);
});
```
