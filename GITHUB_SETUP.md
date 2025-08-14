# GitHub Repository Setup Guide

This guide will walk you through setting up the GitHub repository for the Akamai Usage Reporter project.

## Prerequisites

- GitHub account
- Git installed locally
- SSH key configured (recommended) or GitHub CLI

## Step 1: Create GitHub Repository

### Option A: Via GitHub Web Interface (Recommended)

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Fill in the repository details:
   - **Repository name**: `akamai-usage-reporter`
   - **Description**: `A CLI tool that analyzes Akamai account usage and generates Cloudflare migration checklists`
   - **Visibility**: Choose Public or Private
   - **Initialize with**: Leave unchecked (we already have files)
5. Click "Create repository"

### Option B: Via GitHub CLI

```bash
gh repo create akamai-usage-reporter \
  --description "A CLI tool that analyzes Akamai account usage and generates Cloudflare migration checklists" \
  --public \
  --source=. \
  --remote=origin \
  --push
```

## Step 2: Configure Git User (if not already done)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Step 3: Add Remote Origin

Replace `yourusername` with your actual GitHub username:

```bash
git remote add origin https://github.com/yourusername/akamai-usage-reporter.git
```

Or if using SSH:

```bash
git remote add origin git@github.com:yourusername/akamai-usage-reporter.git
```

## Step 4: Push to GitHub

```bash
git push -u origin main
```

## Step 5: Verify Repository

1. Visit your repository on GitHub
2. Verify all files are present
3. Check that the README renders correctly
4. Verify the GitHub Actions workflow file is in place

## Step 6: Enable GitHub Features

### GitHub Actions
- Go to Actions tab
- GitHub Actions should be automatically enabled
- The CI workflow will run on the next push

### Issues
- Go to Settings → Features
- Ensure Issues are enabled
- Consider enabling Discussions for community engagement

### Wiki (Optional)
- Go to Settings → Features
- Enable Wiki if you want additional documentation

## Step 7: Update Repository URLs

After creating the repository, update these files with your actual GitHub username:

1. **README.md**: Replace `yourusername` with your actual username
2. **setup.py**: Update the URL in the setup configuration
3. **CONTRIBUTING.md**: Update issue tracker URLs

## Step 8: First Release (Optional)

1. Go to Releases → "Create a new release"
2. Tag version: `v1.0.0`
3. Release title: `Initial Release`
4. Description: Copy from CHANGELOG.md
5. Publish release

## Step 9: Community Setup

### Issue Templates
Create `.github/ISSUE_TEMPLATE/` directory with templates for:
- Bug reports
- Feature requests
- Usage questions

### Pull Request Template
Create `.github/pull_request_template.md` for standardized PR descriptions.

## Step 10: Documentation Updates

After the repository is live:

1. Update the README badges with your actual repository URLs
2. Add any additional documentation
3. Consider adding a Wiki for advanced usage examples

## Troubleshooting

### Permission Denied
- Ensure your SSH key is added to GitHub
- Check repository permissions
- Verify you're the owner or have write access

### Push Fails
- Check remote URL: `git remote -v`
- Verify authentication: `ssh -T git@github.com`
- Check branch protection rules

### Actions Not Running
- Ensure the workflow file is in `.github/workflows/`
- Check Actions tab for any error messages
- Verify the workflow syntax is correct

## Next Steps

Once the repository is set up:

1. **Share**: Share the repository with your team/community
2. **Document**: Add more detailed documentation as needed
3. **Community**: Engage with users through Issues and Discussions
4. **Maintain**: Regular updates and maintenance

## Support

If you encounter issues:
- Check GitHub's [documentation](https://docs.github.com/)
- Review the [GitHub Community](https://github.com/orgs/community/discussions)
- Open an issue in this repository

---

**Note**: Remember to never commit sensitive information like API keys or credentials to the repository. Use environment variables and `.gitignore` to protect sensitive data.
