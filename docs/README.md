# SWT-Bench Documentation Site

This directory contains the source files for the SWT-Bench leaderboard website that is automatically deployed to GitHub Pages.

## Files

- `generate_index.py` - Python script that generates the final `index.html` from the template and CSV data
- `index.template.html` - HTML template for the leaderboard page
- `runs.csv` - Model performance data
- `orgs.csv` - Organization/provider information
- `approaches.csv` - Approach/paper mapping data
- `static/` - Static assets (CSS, JS, images)

## Serving Locally

To generate the site locally:

```bash
cd docs
python generate_index.py
```

This will create/update the `index.html` file based on the current CSV data and template.

You can serve this using the Python built-in HTTP library:
```bash
python -m http.server 8080
```

## Automatic Deployment

The site is automatically built and deployed to GitHub Pages via the `.github/workflows/deploy-pages.yml` workflow:

1. **Triggers**: Runs on pushes to the `main` branch, pull requests, or manual dispatch
2. **Build Process**: 
   - Checks out the repository
   - Sets up Python 3.11
   - Runs `generate_index.py` to create the final HTML
   - Uploads the entire `docs/` directory as a Pages artifact
3. **Deployment**: Deploys to GitHub Pages (only on pushes to `main`)

## GitHub Pages Configuration

Make sure GitHub Pages is configured in your repository settings:
1. Go to Settings → Pages
2. Set Source to "GitHub Actions"
3. The workflow will handle the rest automatically

