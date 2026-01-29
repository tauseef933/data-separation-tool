# Deployment Guide - Data Separation Tool

This guide will help you deploy your Data Separation Tool to a FREE cloud platform, making it accessible to your clients 24/7 without your computer running.

---

## RECOMMENDED: Streamlit Community Cloud (100% FREE)

### Why Streamlit Cloud?
- Completely FREE forever
- No credit card required
- Easy deployment (5 minutes)
- Automatic updates from GitHub
- Perfect for 10-20 users
- Professional URL
- 1GB RAM per app (handles 50MB+ files easily)

### Step-by-Step Deployment

#### 1. Prepare Your GitHub Repository

**If you don't have GitHub account:**
1. Go to https://github.com
2. Click "Sign up"
3. Create free account

**Create Repository:**
1. Login to GitHub
2. Click the "+" icon (top right) → "New repository"
3. Fill in:
   - Repository name: `data-separation-tool`
   - Description: "Professional Excel data categorization tool"
   - Make it **Public** (required for free Streamlit)
4. Click "Create repository"

**Upload Your Files:**

Option A - Using GitHub Web Interface:
1. Click "uploading an existing file"
2. Drag and drop these files:
   - `app.py`
   - `requirements.txt`
   - `README.md`
3. Create folder `.streamlit` and upload `config.toml` inside it
4. Click "Commit changes"

Option B - Using Git Command Line:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/data-separation-tool.git
git push -u origin main
```

#### 2. Deploy to Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Click "Sign in" → "Continue with GitHub"
3. Authorize Streamlit to access your GitHub
4. Click "New app" button
5. Fill in deployment form:
   - **Repository**: Select `your-username/data-separation-tool`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: Choose a custom name (e.g., `yourcompany-data-tool`)
6. Click "Deploy!"

#### 3. Wait for Deployment (2-3 minutes)
- Streamlit will install dependencies
- You'll see build logs
- When complete, your app will automatically open

#### 4. Get Your URL
- Your URL will be: `https://yourappname.streamlit.app`
- Share this URL with your clients
- **It works 24/7 without your computer!**

#### 5. Custom Domain (Optional)
If you want to use your own domain:
1. Go to app settings
2. Click "Custom domain"
3. Follow DNS configuration instructions

---

## ALTERNATIVE: Hugging Face Spaces (100% FREE)

### Why Hugging Face?
- Completely FREE
- No credit card required
- Unlimited public apps
- 16GB RAM per app
- Great for larger files

### Step-by-Step Deployment

#### 1. Create Hugging Face Account
1. Go to https://huggingface.co
2. Click "Sign Up"
3. Create free account

#### 2. Create New Space
1. Login to Hugging Face
2. Click your profile icon → "New Space"
3. Fill in:
   - **Space name**: `data-separation-tool`
   - **License**: Apache 2.0
   - **Select the SDK**: Choose **Streamlit**
   - **Space hardware**: CPU basic (free)
   - **Visibility**: Public
4. Click "Create Space"

#### 3. Upload Files
1. In your new Space, click "Files and versions"
2. Click "Add file" → "Upload files"
3. Upload these files:
   - `app.py`
   - `requirements.txt`
   - `README.md`
4. Create `.streamlit` folder:
   - Click "Add file" → "Create a new file"
   - Name: `.streamlit/config.toml`
   - Paste content from your config.toml
   - Click "Commit"

#### 4. Wait for Build
- Hugging Face will automatically build your app
- This takes 2-3 minutes
- When complete, you'll see "Running" status

#### 5. Access Your App
- Your URL: `https://huggingface.co/spaces/YOUR-USERNAME/data-separation-tool`
- Click "App" tab to view
- Share this URL with clients

---

## After Deployment Checklist

### Test Your Deployment
- [ ] Open your app URL in browser
- [ ] Upload a sample Excel file
- [ ] Process the file
- [ ] Download results
- [ ] Test on mobile device
- [ ] Verify speed and performance

### Share with Clients
- [ ] Send URL to all 10-20 users
- [ ] Provide quick usage instructions
- [ ] Share support contact information
- [ ] Set up feedback channel

### Monitor Usage
- [ ] Check Streamlit/Hugging Face analytics dashboard
- [ ] Monitor for errors or issues
- [ ] Review user feedback
- [ ] Update categories as needed

---

## Updating Your App

When you need to make changes:

### For Streamlit Cloud:
1. Edit files in GitHub repository
2. Commit changes
3. Streamlit automatically redeploys (takes 1-2 minutes)

### For Hugging Face:
1. Go to your Space
2. Click "Files and versions"
3. Edit or upload new files
4. App automatically rebuilds

---

## Advanced Configuration

### Increase Upload Limit

**Streamlit Cloud:**
1. Go to app settings
2. Click "Advanced settings"
3. Add to config:
   ```
   [server]
   maxUploadSize = 500
   ```

**Hugging Face:**
1. Edit `.streamlit/config.toml`
2. Change `maxUploadSize=500`
3. Commit changes

### Add Password Protection

Add to your `app.py` (after imports):

```python
import hmac

def check_password():
    def password_entered():
        if hmac.compare_digest(st.session_state["password"], "your_password_here"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.text_input("Password", type="password", on_change=password_entered, key="password")
    
    if "password_correct" in st.session_state:
        st.error("Password incorrect")
    return False

# Add at start of main():
if not check_password():
    st.stop()
```

### Enable Analytics

**Streamlit Cloud:**
- Analytics automatically available in dashboard
- View page views, user sessions, errors

**Hugging Face:**
- View usage in Space settings
- Monitor downloads and interactions

---

## Troubleshooting

### "App Not Loading"
**Solution:** 
- Check build logs for errors
- Verify all files are uploaded
- Check requirements.txt for typos

### "Out of Memory"
**Solution:**
- Reduce `maxUploadSize` limit
- Optimize code for memory usage
- Upgrade to paid plan if needed

### "Too Slow"
**Solution:**
- Check your internet connection
- Try during off-peak hours
- Consider upgrading hardware tier

### "Can't Find My App"
**Solution:**
- Make sure repository is Public (for Streamlit)
- Verify app is "Running" status
- Clear browser cache

---

## Support Resources

### Streamlit Cloud
- Documentation: https://docs.streamlit.io/streamlit-community-cloud
- Community Forum: https://discuss.streamlit.io
- Status Page: https://streamlitstatus.com

### Hugging Face
- Documentation: https://huggingface.co/docs/hub/spaces
- Community Forum: https://discuss.huggingface.co
- Discord: https://discord.gg/hugging-face

---

## Cost Comparison

### Streamlit Community Cloud
- **Cost**: $0 forever
- **Limits**: 1 GB RAM, 1 CPU, Public apps only
- **Users**: Unlimited
- **Uptime**: 99.9%
- **Support**: Community forum

### Hugging Face Spaces
- **Cost**: $0 forever
- **Limits**: 16 GB RAM, 2 CPU cores
- **Users**: Unlimited
- **Uptime**: 99%+
- **Support**: Community forum

### Paid Alternatives (If Needed)
- **Streamlit Cloud Pro**: $20/month (private apps, more resources)
- **Heroku**: $7/month (more control)
- **Google Cloud Run**: Pay per use (~$5/month)
- **AWS Elastic Beanstalk**: Variable pricing

---

## Final Notes

**For your use case (10-20 users, 50MB files):**
- ✅ Streamlit Community Cloud is PERFECT and FREE
- ✅ No server maintenance required
- ✅ Professional URL for clients
- ✅ Easy updates through GitHub
- ✅ Reliable uptime

**Deployment time:** 10-15 minutes total (first time)

**No coding required after initial setup!**

Good luck with your deployment! 🚀
