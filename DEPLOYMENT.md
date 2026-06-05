# Deployment Guide

This guide covers deploying the World Cup Rosters Dashboard to various hosting platforms.

## Table of Contents
- [GitHub Pages](#github-pages)
- [Vercel](#vercel)
- [Netlify](#netlify)
- [Pre-Deployment Checklist](#pre-deployment-checklist)

---

## Pre-Deployment Checklist

Before deploying, ensure:

1. ✅ All data files are up to date in `dashboard/data/`
2. ✅ Dashboard works locally (`python dashboard/serve.py`)
3. ✅ All assets (logos, flags) are present in `dashboard/assets/`
4. ✅ No hardcoded localhost URLs in JavaScript files
5. ✅ CORS headers configured if needed
6. ✅ README.md updated with live demo link

---

## GitHub Pages

GitHub Pages is the simplest option for static sites and integrates directly with your repository.

### Setup Steps

1. **Prepare the dashboard directory**

The dashboard is already structured correctly with `index.html` at the root of the `dashboard/` directory.

2. **Create GitHub Pages configuration**

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Pages
        uses: actions/configure-pages@v4
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: './dashboard'
      
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

3. **Enable GitHub Pages**

- Go to your repository on GitHub
- Navigate to Settings → Pages
- Under "Build and deployment":
  - Source: GitHub Actions
- Save changes

4. **Push and deploy**

```bash
git add .github/workflows/deploy.yml
git commit -m "Add GitHub Pages deployment workflow"
git push origin main
```

5. **Access your site**

Your dashboard will be available at:
```
https://yourusername.github.io/world-cup-rosters-charts/
```

### Updating the Dashboard

Simply push changes to the main branch:
```bash
git add dashboard/
git commit -m "Update dashboard data"
git push origin main
```

The workflow will automatically redeploy.

---

## Vercel

Vercel offers excellent performance with automatic deployments and preview URLs for pull requests.

### Setup Steps

1. **Install Vercel CLI** (optional)

```bash
npm install -g vercel
```

2. **Create `vercel.json` configuration**

Create `vercel.json` in the project root:

```json
{
  "version": 2,
  "name": "world-cup-rosters-dashboard",
  "builds": [
    {
      "src": "dashboard/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/dashboard/$1"
    }
  ],
  "headers": [
    {
      "source": "/data/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=3600, must-revalidate"
        }
      ]
    }
  ]
}
```

3. **Deploy via Vercel Dashboard**

- Go to [vercel.com](https://vercel.com)
- Click "Add New Project"
- Import your GitHub repository
- Configure:
  - Framework Preset: Other
  - Root Directory: `dashboard`
  - Build Command: (leave empty)
  - Output Directory: (leave empty)
- Click "Deploy"

4. **Deploy via CLI** (alternative)

```bash
cd dashboard
vercel
```

Follow the prompts to link your project.

5. **Access your site**

Vercel will provide a URL like:
```
https://world-cup-rosters-charts.vercel.app
```

### Custom Domain

1. Go to your project settings on Vercel
2. Navigate to "Domains"
3. Add your custom domain
4. Update DNS records as instructed

---

## Netlify

Netlify is another excellent option with drag-and-drop deployment.

### Setup Steps

1. **Create `netlify.toml` configuration**

Create `netlify.toml` in the project root:

```toml
[build]
  publish = "dashboard"
  command = "echo 'No build required'"

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"

[[headers]]
  for = "/data/*"
  [headers.values]
    Cache-Control = "public, max-age=3600, must-revalidate"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

2. **Deploy via Netlify Dashboard**

- Go to [netlify.com](https://netlify.com)
- Click "Add new site" → "Import an existing project"
- Connect to GitHub and select your repository
- Configure:
  - Base directory: (leave empty)
  - Build command: (leave empty)
  - Publish directory: `dashboard`
- Click "Deploy site"

3. **Deploy via Netlify CLI** (alternative)

```bash
npm install -g netlify-cli
netlify login
netlify init
netlify deploy --prod --dir=dashboard
```

4. **Access your site**

Netlify will provide a URL like:
```
https://world-cup-rosters-charts.netlify.app
```

### Custom Domain

1. Go to "Domain settings" in your Netlify dashboard
2. Click "Add custom domain"
3. Follow DNS configuration instructions

---

## Post-Deployment

### Update README.md

Add the live demo link to your README:

```markdown
## Live Demo

🌐 **[View Live Dashboard](https://yourusername.github.io/world-cup-rosters-charts/)**
```

### Monitor Performance

- Check browser console for errors
- Test on different devices and browsers
- Monitor loading times for data files
- Verify all assets load correctly

### Analytics (Optional)

Add Google Analytics or similar:

1. Get tracking ID from analytics provider
2. Add tracking script to `dashboard/index.html` before `</head>`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

---

## Troubleshooting

### Issue: 404 errors for data files

**Solution**: Ensure data files are in `dashboard/data/` and paths in JavaScript are relative:
```javascript
// Correct
d3.csv('data/rosters_with_market_values.csv')

// Incorrect
d3.csv('/data/rosters_with_market_values.csv')
```

### Issue: CORS errors

**Solution**: Ensure proper headers are set in deployment configuration (see platform-specific configs above).

### Issue: Large file sizes

**Solution**: 
- Compress CSV files if needed
- Consider using JSON instead of CSV for better compression
- Enable gzip compression on hosting platform

### Issue: Slow loading

**Solution**:
- Implement lazy loading for visualizations
- Add loading indicators
- Consider pagination for large datasets
- Use CDN for D3.js library

---

## Continuous Deployment

All three platforms support automatic deployments:

1. **Push to main branch** → Automatic deployment
2. **Pull request** → Preview deployment (Vercel/Netlify)
3. **Merge PR** → Production deployment

### Recommended Workflow

```bash
# Create feature branch
git checkout -b update-2026-rosters

# Make changes
python -m src.scrapers.wikipedia_scraper --year 2026
cp data/processed/rosters_with_market_values.csv dashboard/data/

# Commit and push
git add .
git commit -m "Update 2026 rosters"
git push origin update-2026-rosters

# Create PR on GitHub
# Review preview deployment
# Merge to main → automatic production deployment
```

---

## Security Considerations

1. **No sensitive data**: Ensure no API keys or credentials in repository
2. **HTTPS only**: All platforms provide free SSL certificates
3. **Content Security Policy**: Consider adding CSP headers
4. **Rate limiting**: Monitor for unusual traffic patterns

---

## Cost

All three platforms offer generous free tiers:

- **GitHub Pages**: Free for public repositories
- **Vercel**: Free tier includes 100GB bandwidth/month
- **Netlify**: Free tier includes 100GB bandwidth/month

For this project, the free tier should be more than sufficient.

---

## Recommendation

**For this project, GitHub Pages is recommended** because:
- ✅ Simplest setup
- ✅ Direct integration with repository
- ✅ No additional account needed
- ✅ Sufficient for static dashboard
- ✅ Free for public repositories

Use Vercel or Netlify if you need:
- Preview deployments for PRs
- Custom headers/redirects
- Better performance/CDN
- Form handling or serverless functions

---

## Next Steps

1. Choose your deployment platform
2. Follow the setup steps above
3. Test the deployed dashboard thoroughly
4. Update README.md with live demo link
5. Share your dashboard! 🎉