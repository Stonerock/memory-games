# Deploy to GitHub - Step by Step

Follow these steps to publish this repository to GitHub for internal sharing.

## Prerequisites

- [x] Git initialized (done ✓)
- [x] GitHub account
- [ ] GitHub CLI installed (optional, makes it easier)

---

## Step 1: Review What Will Be Committed

```bash
cd "/Users/markus.karikivi/Local Sites/memory-games"

# See all files that will be added
git status

# Review .gitignore (sensitive files are excluded)
cat .gitignore
```

**Important files that are EXCLUDED (won't be pushed)**:
- `.env` and `.env.local` (API keys)
- `memory/` (your local memories)
- `.venv/` (Python virtual environment)
- `.cursor/` (your local Cursor config)

---

## Step 2: Create Initial Commit

```bash
# Add all files
git add .

# Create first commit
git commit -m "Initial commit: ReasoningBank for Code with Graphiti integration"
```

---

## Step 3: Create GitHub Repository

### Option A: Using GitHub CLI (Recommended)

```bash
# Install gh if needed
# macOS: brew install gh
# Ubuntu: sudo apt install gh

# Login to GitHub
gh auth login

# Create private repo (for internal sharing)
gh repo create reasoning-bank-cursor --private --source=. --remote=origin

# Push code
git push -u origin main
```

### Option B: Using GitHub Website

1. **Go to GitHub**: https://github.com/new

2. **Create Repository**:
   - Repository name: `reasoning-bank-cursor`
   - Description: "AI coding agent with persistent memory (JSONL + Graphiti)"
   - Visibility: **Private** (for internal sharing)
   - **Do NOT** initialize with README, .gitignore, or license (we have them)

3. **Connect and Push**:
   ```bash
   # Replace YOUR_USERNAME and YOUR_ORG
   git remote add origin https://github.com/YOUR_ORG/reasoning-bank-cursor.git
   git branch -M main
   git push -u origin main
   ```

---

## Step 4: Configure Repository Settings

### On GitHub Website:

1. **Go to Settings** → **General**:
   - [ ] Enable Issues
   - [ ] Enable Discussions
   - [ ] Disable Wikis (optional)
   - [ ] Disable Projects (optional)

2. **Go to Settings** → **Actions** → **General**:
   - [ ] Allow all actions and reusable workflows
   - [ ] Enable read/write permissions for workflows

3. **Go to Settings** → **Collaborators and teams**:
   - Add your internal team members
   - Set appropriate permissions (Write or Admin)

---

## Step 5: Add Description and Topics

On the main repo page:

1. **Click "Edit" next to About**

2. **Description**:
   ```
   AI coding agent with persistent memory. Learn from successes and failures. JSONL or Graphiti backends. Cursor IDE integration.
   ```

3. **Topics** (add these tags):
   - `ai-coding-assistant`
   - `cursor-ide`
   - `knowledge-graph`
   - `reasoning-bank`
   - `graphiti`
   - `memory-system`
   - `code-generation`

4. **Website**: (if you have docs hosted)

---

## Step 6: Test the Repository

Clone it fresh to verify:

```bash
# Go to a different directory
cd /tmp

# Clone the repo
git clone https://github.com/YOUR_ORG/reasoning-bank-cursor.git
cd reasoning-bank-cursor

# Follow setup instructions from README
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Test it works
python test_integration.py
```

---

## Step 7: Share with Your Team

### Internal Team Announcement

Send this message to your team:

```
Hi team! 👋

I've set up a new tool called ReasoningBank for Code. It's an AI coding
assistant that learns from our bug fixes and remembers solutions across
projects.

Key Features:
✅ Persistent memory (stores what works/doesn't work)
✅ Integrates with Cursor IDE
✅ Two backends: simple JSONL or semantic Graphiti
✅ Learn from failures (not just successes!)

Repository: https://github.com/YOUR_ORG/reasoning-bank-cursor

Quick Start:
1. Clone the repo
2. Follow README.md
3. For Cursor integration, see CURSOR_INTEGRATION_GUIDE.md

Questions? Check the docs or open an issue!
```

### Share Documentation Links

- **Quick Start**: `https://github.com/YOUR_ORG/reasoning-bank-cursor/blob/main/QUICKSTART.md`
- **Cursor Guide**: `https://github.com/YOUR_ORG/reasoning-bank-cursor/blob/main/CURSOR_INTEGRATION_GUIDE.md`
- **Contributing**: `https://github.com/YOUR_ORG/reasoning-bank-cursor/blob/main/CONTRIBUTING.md`

---

## Step 8: Create First Release (Optional)

```bash
# Tag the first release
git tag -a v0.1.0 -m "Initial release with Graphiti integration"
git push origin v0.1.0
```

Or use GitHub CLI:
```bash
gh release create v0.1.0 \
  --title "v0.1.0 - Initial Release" \
  --notes "First stable release with JSONL and Graphiti backends"
```

---

## Step 9: Ongoing Maintenance

### When Team Members Report Issues

1. **Issues Page**: https://github.com/YOUR_ORG/reasoning-bank-cursor/issues
2. Use issue templates (already set up)
3. Label issues: `bug`, `enhancement`, `cursor`, etc.

### When Team Members Contribute

1. **Pull Requests**: Follow CONTRIBUTING.md
2. CI will run automatically (tests both JSONL and Graphiti)
3. Review and merge PRs

### Regular Updates

```bash
# After making changes
git add .
git commit -m "feat: description of changes"
git push origin main
```

---

## Security Checklist

Before pushing, verify:

- [ ] No API keys in code
- [ ] `.env` and `.env.local` in .gitignore
- [ ] No sensitive data in test files
- [ ] `memory/` folder excluded (contains project-specific data)
- [ ] `.env.local.example` has placeholder values only

---

## Troubleshooting

### "remote: Repository not found"

→ Check repository exists and you have access
→ Use `gh repo view` to verify

### "Permission denied (publickey)"

→ Set up SSH key: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

Or use HTTPS with personal access token:
```bash
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_ORG/reasoning-bank-cursor.git
```

### CI Tests Failing

→ Check `.github/workflows/ci.yml`
→ May need to adjust Python versions or dependencies

---

## What's Next?

After deployment:

1. **Monitor usage**: Check GitHub Insights → Traffic
2. **Collect feedback**: Watch Issues and Discussions
3. **Iterate**: Update based on team feedback
4. **Document learnings**: Add to project memory! 😄

---

## Quick Reference: Git Commands

```bash
# Check status
git status

# Add changes
git add .

# Commit
git commit -m "description"

# Push
git push origin main

# Pull latest
git pull origin main

# Create branch
git checkout -b feature/new-feature

# Push branch
git push -u origin feature/new-feature
```

---

## Support

If you run into issues:
1. Check existing issues: https://github.com/YOUR_ORG/reasoning-bank-cursor/issues
2. Create new issue with bug report template
3. Reach out to project maintainer

---

**You're ready to share this with your team! 🚀**
