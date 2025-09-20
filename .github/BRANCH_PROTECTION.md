# 🌿 Branch Protection Rules

## Branch Strategy

### **main** (Production)
- **Purpose**: Production-ready code
- **Protection**: 
  - Require pull request reviews (2 reviewers)
  - Require status checks to pass before merging
  - Require branches to be up to date before merging
  - Restrict pushes to main branch
  - Require linear history

### **staging** (Staging Environment)
- **Purpose**: Pre-production testing
- **Protection**:
  - Require pull request reviews (1 reviewer)
  - Require status checks to pass
  - Allow force pushes (for hotfixes)

### **develop** (Development Integration)
- **Purpose**: Integration branch for features
- **Protection**:
  - Require pull request reviews (1 reviewer)
  - Allow force pushes

### **feature/*** (Feature Branches)
- **Purpose**: Individual feature development
- **Protection**: None (developer branches)

## Required Status Checks

### For `main` branch:
- ✅ Backend Tests (CI Pipeline)
- ✅ Frontend Tests (CI Pipeline)
- ✅ Security Scan
- ✅ Code Quality (Linting)
- ✅ Build Success

### For `staging` branch:
- ✅ Backend Tests
- ✅ Frontend Tests
- ✅ Code Quality (Linting)
- ✅ Build Success

## Review Requirements

- **main**: 2 approvals required
- **staging**: 1 approval required
- **develop**: 1 approval required
- **feature/***: No approval required

## Deployment Triggers

- **main** → Production deployment
- **staging** → Staging deployment
- **develop** → No automatic deployment
- **feature/*** → No deployment

## Hotfix Process

For critical production fixes:
1. Create `hotfix/issue-description` branch from `main`
2. Make minimal changes
3. Create PR to `main` with expedited review
4. After merge to `main`, cherry-pick to `staging`
5. Delete hotfix branch after deployment
