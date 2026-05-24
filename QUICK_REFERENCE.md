# Quick CI/CD Reference - What Happens on Each Push to Main

## Automatic Actions (GitHub Actions Workflow)

### When you push code to `main` branch:
1. **GitHub Actions Triggered** ✅
2. **Code Checked Out** - Your latest code from main branch
3. **Python Environment Setup** - Python 3.9 installed
4. **Dependencies Installed** - boto3, awsglue libraries
5. **AWS Credentials Configured** - Using GitHub Secrets
6. **Glue Script Uploaded** → S3 bucket
7. **Lambda Code Packaged** → Requirements included
8. **Lambda Function Updated** → In AWS Lambda service
9. **Glue Job Updated** → Configuration synced (if exists)
10. **Summary Printed** → Deployment complete message

---

## Step-by-Step Setup Checklist

### ✅ Phase 1: AWS Account Setup (One-time)
- [ ] Create S3 bucket for scripts: `your-glue-scripts-bucket`
- [ ] Create IAM user: `github-actions-user`
- [ ] Generate Access Keys for the user
- [ ] Create IAM Policy with S3, Lambda, Glue permissions
- [ ] Attach policy to github-actions-user

### ✅ Phase 2: GitHub Secrets (One-time)
Add 5 secrets to GitHub repo settings:
- [ ] AWS_ACCESS_KEY_ID
- [ ] AWS_SECRET_ACCESS_KEY
- [ ] AWS_REGION (e.g., us-east-1)
- [ ] AWS_ACCOUNT_ID
- [ ] AWS_GLUE_SCRIPTS_BUCKET

### ✅ Phase 3: Project Configuration
- [ ] Verify `.github/workflows/deploy.yml` exists
- [ ] Update Lambda function name in workflow
- [ ] Update Glue job name in workflow (if you have one)
- [ ] Check `lambda_file_check/requirements.txt` has dependencies

### ✅ Phase 4: First Deployment
```bash
# Push your code
git add .
git commit -m "Setup CI/CD pipeline"
git push origin main
```
- Go to GitHub Actions tab
- Monitor your first deployment
- Check CloudWatch logs if issues occur

---

## Track Changes in GitHub

### Every change tracked:
- Who made changes (git user)
- When changes were made (commit timestamp)
- What changed (git diff)
- Deployment status (success/failure in Actions)
- AWS resources updated (logs in Actions)

### View Change History:
1. GitHub → **Commits** tab - See all changes
2. GitHub → **Actions** tab - See all deployments
3. GitHub → **Settings** → Activity log - Account changes

---

## Common Updates

### Update Glue Script
```bash
# Edit glue_etl_code/glue.py
git add glue_etl_code/glue.py
git commit -m "Update Glue job logic"
git push origin main  # → Automatically deployed to S3 & Glue
```

### Update Lambda Code
```bash
# Edit lambda_file_check/lambda.py
git add lambda_file_check/lambda.py
git commit -m "Update Lambda handler"
git push origin main  # → Automatically deployed to Lambda
```

### Add Lambda Dependencies
```bash
# Edit lambda_file_check/requirements.txt
# Add: requests==2.28.0
git add lambda_file_check/requirements.txt
git commit -m "Add requests library to Lambda"
git push origin main  # → requirements automatically included in Lambda zip
```

---

## Security Notes
❌ NEVER commit:
- AWS credentials
- API keys
- Database passwords

✅ Always use:
- GitHub Secrets for credentials
- IAM roles and policies
- Principle of least privilege
