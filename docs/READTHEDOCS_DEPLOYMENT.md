# ReadTheDocs Deployment Guide

This guide walks you through deploying the MongoDB Query Builder documentation to ReadTheDocs.io.

## Prerequisites

- GitHub repository with the documentation
- ReadTheDocs account (free at readthedocs.org)
- MkDocs documentation set up (already done!)

## Local Testing

First, test the documentation locally:

```bash
# Install MkDocs dependencies
pip install -r docs/requirements.txt

# Serve documentation locally
mkdocs serve

# Visit http://localhost:8000 to preview
```

## ReadTheDocs Setup

### 1. Import Project

1. Log in to [ReadTheDocs.org](https://readthedocs.org)
2. Click "Import a Project"
3. Select "Import from GitHub"
4. Choose your `mongodb-builder` repository
5. Click "Next"

### 2. Project Configuration

ReadTheDocs will automatically detect the `.readthedocs.yaml` file. Verify these settings:

- **Name**: MongoDB Query Builder
- **Repository URL**: Your GitHub repo URL
- **Default branch**: main (or master)
- **Documentation type**: MkDocs (auto-detected)

### 3. Advanced Settings

In the project admin panel:

1. **Domains**: 
   - Default: `mongodb-query-builder.readthedocs.io`
   - Can add custom domain later

2. **Versions**:
   - Enable version tags for releases
   - Set "latest" as default version

3. **Build Settings**:
   - Build on push: ✓
   - Build pull requests: ✓ (optional)

### 4. Environment Variables (if needed)

If you need any environment variables, add them in:
Admin → Environment Variables

## GitHub Integration

### Webhook Setup

ReadTheDocs automatically sets up a webhook. Verify in your GitHub repo:

1. Go to Settings → Webhooks
2. You should see a ReadTheDocs webhook
3. It triggers on push events

### Build Status Badge

Add to your README.md:

```markdown
[![Documentation Status](https://readthedocs.org/projects/mongodb-query-builder/badge/?version=latest)](https://mongodb-query-builder.readthedocs.io/en/latest/?badge=latest)
```

## Version Management

For version management with `mike`:

```bash
# Install mike
pip install mike

# Deploy initial version
mike deploy --push --update-aliases 0.1.0 latest

# Deploy new version
mike deploy --push --update-aliases 0.2.0 latest

# List versions
mike list

# Set default version
mike set-default --push latest
```

## Troubleshooting

### Build Failures

1. Check build logs in ReadTheDocs dashboard
2. Common issues:
   - Missing dependencies in `docs/requirements.txt`
   - Incorrect `mkdocs.yml` syntax
   - Python version mismatch

### Custom Domain

To use a custom domain:

1. Add CNAME record pointing to `readthedocs.io`
2. Add domain in ReadTheDocs admin panel
3. Enable HTTPS

### Search Not Working

Ensure in `mkdocs.yml`:
- Search plugin is enabled
- Language is set correctly

## Maintenance

### Updating Documentation

1. Make changes to documentation files
2. Commit and push to GitHub
3. ReadTheDocs automatically rebuilds

### Monitoring

- Check build status in ReadTheDocs dashboard
- Monitor 404 errors in analytics
- Review search queries for missing content

## Next Steps

1. Complete placeholder documentation files
2. Add more examples and tutorials
3. Set up documentation versioning
4. Consider adding:
   - API changelog
   - Contributing guide
   - Architecture diagrams
   - Video tutorials

## Resources

- [ReadTheDocs Documentation](https://docs.readthedocs.io/)
- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [Mike Documentation](https://github.com/jimporter/mike)
