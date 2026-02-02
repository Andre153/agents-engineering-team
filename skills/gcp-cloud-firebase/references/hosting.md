# Firebase Hosting

## Table of Contents
- [Configuration](#configuration)
- [Rewrites and Redirects](#rewrites-and-redirects)
- [Headers](#headers)
- [Multiple Sites](#multiple-sites)
- [Preview Channels](#preview-channels)
- [Deployment](#deployment)

## Configuration

### Basic firebase.json

```json
{
  "hosting": {
    "public": "public",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ]
  }
}
```

### Single Page App (SPA)

```json
{
  "hosting": {
    "public": "dist",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
```

## Rewrites and Redirects

### Cloud Run Integration

```json
{
  "hosting": {
    "public": "public",
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
  }
}
```

### Cloud Functions Integration

```json
{
  "hosting": {
    "rewrites": [
      {
        "source": "/api/**",
        "function": "api"
      }
    ]
  }
}
```

### Redirects

```json
{
  "hosting": {
    "redirects": [
      {
        "source": "/old-page",
        "destination": "/new-page",
        "type": 301
      },
      {
        "source": "/blog/:post",
        "destination": "https://blog.example.com/:post",
        "type": 302
      },
      {
        "source": "/removed/**",
        "destination": "/",
        "type": 301
      }
    ]
  }
}
```

### Glob Patterns

```json
{
  "hosting": {
    "rewrites": [
      {
        "source": "/users/:id",
        "destination": "/user.html"
      },
      {
        "source": "/posts/:category/:slug",
        "function": "renderPost"
      }
    ]
  }
}
```

## Headers

### Security Headers

```json
{
  "hosting": {
    "headers": [
      {
        "source": "**",
        "headers": [
          {
            "key": "X-Content-Type-Options",
            "value": "nosniff"
          },
          {
            "key": "X-Frame-Options",
            "value": "DENY"
          },
          {
            "key": "X-XSS-Protection",
            "value": "1; mode=block"
          },
          {
            "key": "Referrer-Policy",
            "value": "strict-origin-when-cross-origin"
          }
        ]
      }
    ]
  }
}
```

### Cache Control

```json
{
  "hosting": {
    "headers": [
      {
        "source": "**/*.@(js|css)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "public, max-age=31536000, immutable"
          }
        ]
      },
      {
        "source": "**/*.@(jpg|jpeg|png|gif|webp|svg|ico)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "public, max-age=31536000"
          }
        ]
      },
      {
        "source": "index.html",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "no-cache, no-store, must-revalidate"
          }
        ]
      }
    ]
  }
}
```

### CORS Headers

```json
{
  "hosting": {
    "headers": [
      {
        "source": "/api/**",
        "headers": [
          {
            "key": "Access-Control-Allow-Origin",
            "value": "*"
          },
          {
            "key": "Access-Control-Allow-Methods",
            "value": "GET, POST, PUT, DELETE, OPTIONS"
          },
          {
            "key": "Access-Control-Allow-Headers",
            "value": "Content-Type, Authorization"
          }
        ]
      }
    ]
  }
}
```

## Multiple Sites

### Configure Multiple Sites

```json
{
  "hosting": [
    {
      "target": "app",
      "public": "apps/web/dist",
      "rewrites": [
        { "source": "**", "destination": "/index.html" }
      ]
    },
    {
      "target": "admin",
      "public": "apps/admin/dist",
      "rewrites": [
        { "source": "**", "destination": "/index.html" }
      ]
    },
    {
      "target": "docs",
      "public": "docs/build"
    }
  ]
}
```

### .firebaserc

```json
{
  "projects": {
    "default": "my-project"
  },
  "targets": {
    "my-project": {
      "hosting": {
        "app": ["my-project"],
        "admin": ["my-project-admin"],
        "docs": ["my-project-docs"]
      }
    }
  }
}
```

### Deploy Specific Site

```bash
firebase deploy --only hosting:app
firebase deploy --only hosting:admin
firebase deploy --only hosting
```

## Preview Channels

### Create Preview Channel

```bash
# Create a preview with auto-generated ID
firebase hosting:channel:deploy preview

# Create named preview
firebase hosting:channel:deploy feature-login

# With expiration
firebase hosting:channel:deploy feature-login --expires 7d
```

### In CI/CD

```yaml
# GitHub Actions
- name: Deploy to preview channel
  uses: FirebaseExtended/action-hosting-deploy@v0
  with:
    repoToken: '${{ secrets.GITHUB_TOKEN }}'
    firebaseServiceAccount: '${{ secrets.FIREBASE_SERVICE_ACCOUNT }}'
    channelId: 'pr-${{ github.event.pull_request.number }}'
```

### List and Delete Channels

```bash
# List channels
firebase hosting:channel:list

# Delete channel
firebase hosting:channel:delete feature-login
```

## Deployment

### Deploy Commands

```bash
# Deploy everything
firebase deploy

# Deploy only hosting
firebase deploy --only hosting

# Deploy specific site
firebase deploy --only hosting:app

# Deploy with message
firebase deploy --only hosting -m "v1.2.0 release"
```

### Rollback

```bash
# List recent deploys
firebase hosting:releases:list

# Clone a previous release
firebase hosting:clone SOURCE_SITE:SOURCE_VERSION TARGET_SITE:live
```

### Pre-deploy Script

```json
{
  "hosting": {
    "public": "dist",
    "predeploy": [
      "npm run build",
      "npm run test"
    ]
  }
}
```

### CI/CD Pipeline

```yaml
# GitHub Actions
name: Deploy to Firebase Hosting

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Deploy to Firebase
        uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: '${{ secrets.GITHUB_TOKEN }}'
          firebaseServiceAccount: '${{ secrets.FIREBASE_SERVICE_ACCOUNT }}'
          channelId: live
```

### Custom Domain

```bash
# Add custom domain
firebase hosting:sites:update SITE_ID --site CUSTOM_DOMAIN

# Or via console: Firebase Console > Hosting > Add custom domain
```

DNS Configuration:
1. Add A records pointing to Firebase IPs
2. Add TXT record for verification
3. Wait for SSL certificate provisioning
