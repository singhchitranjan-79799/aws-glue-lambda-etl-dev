# AWS CLI Setup Guide (Local Machine)

## Why Setup AWS CLI?
- Run AWS commands locally
- Test deployments before GitHub push
- Manage AWS resources from terminal
- Verify configurations

---

## Step 1: Install AWS CLI

### Windows PowerShell
```powershell
# Download and run installer
Invoke-WebRequest -Uri "https://awscli.amazonaws.com/AWSCLIV2.msi" -OutFile AWSCLIV2.msi
.\AWSCLIV2.msi

# Verify installation
aws --version
```

### macOS
```bash
curl "https://awscli.amazonaws.com/awscli-exe-macos.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify
aws --version
```

### Linux
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify
aws --version
```

---

## Step 2: Configure AWS Credentials

You need AWS Access Key ID and Secret Access Key. Get these from:
1. AWS Console → IAM → Users → your-github-user
2. Security credentials tab → Create Access Key

### Configure AWS CLI
```bash
aws configure
```

You'll be prompted for:
```
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-east-1
Default output format [None]: json
```

---

## Step 3: Verify Setup

```bash
# Check if credentials are configured
aws sts get-caller-identity

# Expected output (confirms setup is working):
{
    "UserId": "AIDAI23HZ27SI6FQMGNQ2",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-user"
}
```

---

## Step 4: Test S3 Bucket Access

```bash
# List S3 buckets
aws s3 ls

# Upload a test file
aws s3 cp glue_etl_code/glue.py s3://your-glue-scripts-bucket/test/

# List files in bucket
aws s3 ls s3://your-glue-scripts-bucket/test/

# Download file
aws s3 cp s3://your-glue-scripts-bucket/test/glue.py ./downloaded-glue.py
```

---

## Step 5: Test Lambda Operations

```bash
# List Lambda functions
aws lambda list-functions --region us-east-1

# Get function details
aws lambda get-function --function-name your-lambda-function-name --region us-east-1

# Update Lambda code (manual - useful for testing)
aws lambda update-function-code \
  --function-name your-lambda-function-name \
  --s3-bucket your-glue-scripts-bucket \
  --s3-key lambda_functions/lambda_function.zip \
  --region us-east-1
```

---

## Step 6: Test Glue Operations

```bash
# List Glue jobs
aws glue list-jobs --region us-east-1

# Get specific job details
aws glue get-job --name your-glue-job-name --region us-east-1

# Describe Glue job run (check execution status)
aws glue get-job-runs --job-name your-glue-job-name --region us-east-1
```

---

## Credentials Location

Your credentials are stored here:
- **Windows**: `C:\Users\YourUsername\.aws\credentials`
- **macOS/Linux**: `~/.aws/credentials`

**⚠️ IMPORTANT**: Never share this file or commit it to git.

---

## Troubleshooting AWS CLI

### Error: "Unable to locate credentials"
```bash
# Check if credentials are configured
aws configure list

# Reconfigure if needed
aws configure
```

### Error: "Access Denied" to S3
- Check bucket name is correct
- Verify IAM user has S3 permissions
- Check region is correct

### Error: "InvalidParameter" for Lambda
- Ensure Lambda function name is correct
- Check function exists in specified region
- Verify S3 bucket contains the zip file

---

## Using AWS CLI with Your Project

### Deploy Glue Script Locally
```bash
aws s3 cp glue_etl_code/glue.py s3://your-glue-scripts-bucket/glue_scripts/glue.py
```

### Deploy Lambda Locally
```bash
cd lambda_file_check
pip install -r requirements.txt -t .
zip -r lambda_function.zip .
aws s3 cp lambda_function.zip s3://your-glue-scripts-bucket/lambda_functions/
aws lambda update-function-code \
  --function-name your-lambda-function-name \
  --s3-bucket your-glue-scripts-bucket \
  --s3-key lambda_functions/lambda_function.zip
```

---

## Next: GitHub Secrets

Once AWS CLI is working locally, use those same credentials for GitHub Secrets:
- Copy Access Key ID → GitHub Secret: AWS_ACCESS_KEY_ID
- Copy Secret Access Key → GitHub Secret: AWS_SECRET_ACCESS_KEY
- Your region → GitHub Secret: AWS_REGION
