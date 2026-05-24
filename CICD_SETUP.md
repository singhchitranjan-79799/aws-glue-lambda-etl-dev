# CI/CD Setup Guide for AWS Glue & Lambda

## Overview
This document covers the complete setup for CI/CD pipeline using GitHub Actions to deploy:
- AWS Glue Scripts
- AWS Lambda Functions
- Code to S3

---

## Phase 1: AWS Setup

### 1.1 Create S3 Bucket for Scripts
```bash
# Create S3 bucket (replace with your bucket name)
aws s3 mb s3://your-glue-scripts-bucket --region us-east-1

# Create folder structure
aws s3api put-object --bucket your-glue-scripts-bucket --key glue_scripts/
aws s3api put-object --bucket your-glue-scripts-bucket --key lambda_functions/
```

### 1.2 Create IAM User for GitHub Actions
```bash
# Create new IAM user
aws iam create-user --user-name github-actions-user

# Create access key
aws iam create-access-key --user-name github-actions-user
```

**IMPORTANT:** Save the Access Key ID and Secret Access Key - you'll need these for GitHub Secrets.

### 1.3 Create IAM Policy
Create a file `glue-lambda-deployment-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-glue-scripts-bucket",
        "arn:aws:s3:::your-glue-scripts-bucket/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration"
      ],
      "Resource": "arn:aws:lambda:*:ACCOUNT_ID:function:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "glue:UpdateJob",
        "glue:GetJob"
      ],
      "Resource": "*"
    }
  ]
}
```

### 1.4 Attach Policy to GitHub Actions User
```bash
# First, create the policy
aws iam create-policy \
  --policy-name GitHubActionsGluePolicy \
  --policy-document file://glue-lambda-deployment-policy.json

# Then attach to user
aws iam attach-user-policy \
  --user-name github-actions-user \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/GitHubActionsGluePolicy
```

Replace `ACCOUNT_ID` with your AWS Account ID.

---

## Phase 2: GitHub Secrets Configuration

Add the following secrets to your GitHub repository:
- Go to: **Settings → Secrets and variables → Actions → New repository secret**

### Required Secrets:
1. **AWS_ACCESS_KEY_ID** → Access Key from Step 1.2
2. **AWS_SECRET_ACCESS_KEY** → Secret Access Key from Step 1.2  
3. **AWS_REGION** → Your AWS region (e.g., `us-east-1`)
4. **AWS_ACCOUNT_ID** → Your AWS Account ID
5. **AWS_GLUE_SCRIPTS_BUCKET** → Your S3 bucket name (e.g., `your-glue-scripts-bucket`)

---

## Phase 3: Configure Lambda Function

In your GitHub Actions workflow (`.github/workflows/deploy.yml`), update:
- Replace `your-lambda-function-name` with actual Lambda function name
- Ensure your Lambda function exists in AWS

---

## Phase 4: Configure Glue Job (Optional)

If you have a Glue Job defined:
1. Create the Glue Job in AWS Console first
2. Update `.github/workflows/deploy.yml` with correct job name
3. Ensure the IAM role exists

---

## Phase 5: Git Workflow

### Initialize/Push to GitHub
```bash
# If not already initialized
git init
git add .
git commit -m "Initial commit: Add CI/CD pipeline"
git branch -M main
git remote add origin https://github.com/your-username/repo-name.git
git push -u origin main
```

### Trigger CI/CD
Every push to `main` branch will automatically:
1. ✅ Upload Glue scripts to S3
2. ✅ Package and upload Lambda function to S3
3. ✅ Update Lambda function code in AWS
4. ✅ Update Glue Job configuration (if exists)

---

## Phase 6: Verify Deployment

### Check GitHub Actions:
1. Go to your GitHub repo → **Actions** tab
2. View the latest workflow run
3. Check logs for any errors

### Verify in AWS:
```bash
# Check S3 upload
aws s3 ls s3://your-glue-scripts-bucket/glue_scripts/

# Check Lambda update
aws lambda get-function --function-name your-lambda-function-name

# Check Glue Job
aws glue get-job --name your-glue-job-name
```

---

## File Structure (Expected)
```
.
├── .github/
│   └── workflows/
│       └── deploy.yml              # GitHub Actions workflow
├── glue_etl_code/
│   └── glue.py                      # Your Glue script
├── lambda_file_check/
│   ├── lambda.py                    # Your Lambda handler
│   └── requirements.txt             # Lambda dependencies
└── README.md
```

---

## Troubleshooting

### Issue: "Access Denied" errors
- Verify IAM policy is attached to github-actions-user
- Check AWS credentials in GitHub Secrets
- Verify S3 bucket exists and region is correct

### Issue: Lambda update fails
- Ensure Lambda function exists in AWS
- Check function name is correct in workflow
- Verify IAM policy includes lambda:UpdateFunctionCode

### Issue: Workflow not triggering
- Check branch protection rules
- Ensure you're pushing to `main` branch
- Verify `.github/workflows/deploy.yml` syntax

---

## Advanced: Multi-Environment Setup (Future)

To add staging/production environments:
1. Create separate S3 buckets per environment
2. Add environment-based GitHub secrets
3. Use GitHub environments with approval gates
4. Modify workflow to support manual triggers

