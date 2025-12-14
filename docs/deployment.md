# Publishing Documentation

This guide explains how to publish Yarasp documentation to ReadTheDocs and GitHub Pages.

## Prerequisites

1. MkDocs installed:
   ```bash
   pip install mkdocs mkdocs-material mkdocstrings[python]
   ```

   Or using uv:
   ```bash
   uv add --dev mkdocs mkdocs-material mkdocstrings[python]
   ```

2. Git repository with documentation files committed

3. Account on ReadTheDocs (optional, for ReadTheDocs publishing)

## Local Development

Before publishing, test the documentation locally:

```bash
# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

The documentation will be available at `http://127.0.0.1:8000`

## Publishing to ReadTheDocs

ReadTheDocs is a free documentation hosting service that automatically builds and publishes documentation from your Git repository.

### Step 1: Sign Up

1. Go to [ReadTheDocs](https://readthedocs.org/)
2. Sign up or log in with your GitHub account
3. Click "Import a Project"

### Step 2: Connect Repository

1. Select "Import Manually" or connect your GitHub account
2. Fill in the project details:
   - **Name**: `yarasp` (or your preferred name)
   - **Repository URL**: `https://github.com/pavelsr/yarasp`
   - **Repository Type**: Git
   - **Default Branch**: `main` (or `master`)
3. Click "Create"

### Step 3: Configure Build Settings

1. Go to **Admin** → **Advanced Settings**
2. Configure the following:

   - **Python configuration file**: Leave empty or set to `requirements-docs.txt` (if you create one)
   - **Requirements file**: `requirements-docs.txt` (optional, see below)
   - **Documentation type**: Select "MkDocs (Markdown)"
   - **Default branch**: `main` (or your default branch)
   - **Default version**: `latest`
   - **Install Project**: No (we're just building docs, not installing the package)
   - **Use system packages**: No

### Step 4: Create Requirements File (Optional)

Create a `requirements-docs.txt` file in the repository root:

```txt
mkdocs>=1.5.0
mkdocs-material>=9.0.0
mkdocstrings[python]>=0.23.0
```

Add it to your repository:

```bash
git add requirements-docs.txt
git commit -m "Add documentation requirements"
git push
```

**Note**: ReadTheDocs will automatically install dependencies listed in this file.

### Step 5: Configure mkdocs.yml

Ensure your `mkdocs.yml` is properly configured (already done in this project):

```yaml
site_name: Yarasp Documentation
site_description: Yandex Schedule API Client with async support, HTTP caching, and API key usage tracking

repo_name: pavelsr/yarasp
repo_url: https://github.com/pavelsr/yarasp
```

### Step 6: Build

1. Go to **Admin** → **Versions**
2. Ensure your default branch is activated
3. ReadTheDocs will automatically trigger a build
4. Check the build status in the **Builds** section

### Step 7: Access Your Documentation

Once the build succeeds, your documentation will be available at:
- `https://yarasp.readthedocs.io/` (replace `yarasp` with your project name)

### Updating Documentation

ReadTheDocs automatically rebuilds documentation when you push changes to your repository. No manual action required!

## Publishing to GitHub Pages

GitHub Pages allows you to host static documentation directly from your GitHub repository.

### Method 1: Using GitHub Actions (Recommended)

This method automatically builds and publishes documentation when you push changes.

#### Step 1: Create GitHub Actions Workflow

Create `.github/workflows/docs.yml`:

```yaml
name: Deploy Documentation

on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'
      - 'mkdocs.yml'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install mkdocs mkdocs-material mkdocstrings[python]
      
      - name: Build documentation
        run: mkdocs build
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        if: github.ref == 'refs/heads/main'
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./site
```

#### Step 2: Enable GitHub Pages

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Pages**
3. Under **Source**, select:
   - **Deploy from a branch**
   - **Branch**: `gh-pages`
   - **Folder**: `/ (root)`
4. Click **Save**

#### Step 3: Push Changes

```bash
git add .github/workflows/docs.yml
git commit -m "Add GitHub Actions workflow for documentation"
git push
```

GitHub Actions will automatically build and deploy your documentation.

### Method 2: Manual Deployment

You can manually build and push documentation to the `gh-pages` branch.

#### Step 1: Install Dependencies

```bash
pip install mkdocs mkdocs-material mkdocstrings[python]
```

Or using uv:

```bash
uv add --dev mkdocs mkdocs-material mkdocstrings[python]
```

#### Step 2: Build Documentation

```bash
mkdocs build
```

This creates a `site/` directory with static HTML files.

#### Step 3: Deploy to gh-pages Branch

```bash
# Install mkdocs gh-deploy plugin
pip install mkdocs-git-revision-date-plugin

# Deploy to gh-pages branch
mkdocs gh-deploy
```

Or manually:

```bash
# Create orphan branch for gh-pages
git checkout --orphan gh-pages
git rm -rf .

# Copy built site
cp -r site/* .

# Commit and push
git add .
git commit -m "Deploy documentation"
git push origin gh-pages --force

# Return to main branch
git checkout main
```

#### Step 4: Enable GitHub Pages

1. Go to **Settings** → **Pages**
2. Select **Deploy from a branch**
3. Choose `gh-pages` branch and `/ (root)` folder
4. Click **Save**

### Accessing GitHub Pages Documentation

Your documentation will be available at:
- `https://pavelsr.github.io/yarasp/` (replace `pavelsr` and `yarasp` with your username and repository name)

## Custom Domain (Optional)

### For ReadTheDocs

1. Go to **Admin** → **Domains**
2. Add your custom domain
3. Follow DNS configuration instructions

### For GitHub Pages

1. Create a `CNAME` file in the `docs/` directory with your domain:
   ```
   docs.yourdomain.com
   ```
2. Configure DNS records:
   - Type: `CNAME`
   - Name: `docs` (or `@`)
   - Value: `pavelsr.github.io`
3. Go to **Settings** → **Pages** and enter your custom domain

## Troubleshooting

### Build Failures on ReadTheDocs

- Check the build logs in ReadTheDocs dashboard
- Ensure `requirements-docs.txt` includes all dependencies
- Verify `mkdocs.yml` syntax is correct
- Make sure Python version is compatible (ReadTheDocs uses Python 3.x)

### GitHub Pages Not Updating

- Verify GitHub Actions workflow is enabled
- Check Actions tab for failed workflows
- Ensure `gh-pages` branch exists and has content
- Clear browser cache

### Missing Dependencies

If documentation fails to build, ensure all required packages are listed:

```txt
mkdocs>=1.5.0
mkdocs-material>=9.0.0
mkdocstrings[python]>=0.23.0
```

## Best Practices

1. **Version Control**: Keep documentation in the same repository as code
2. **Automatic Builds**: Use GitHub Actions or ReadTheDocs auto-build
3. **Preview Changes**: Test locally with `mkdocs serve` before pushing
4. **Keep Updated**: Update documentation when code changes
5. **Link Checking**: Periodically check for broken links

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [MkDocs Material Theme](https://squidfunk.github.io/mkdocs-material/)
- [ReadTheDocs Documentation](https://docs.readthedocs.io/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)

