# Setting Up GitHub Actions for Weather Scraper

This guide will help you set up a GitHub Action to run your weather scraper script daily at 12:30 AM Pacific Time.

## 1. Set Up GitHub Secrets

First, you'll need to securely store your environment variables as GitHub Secrets:

1. Go to your GitHub repository
2. Click on "Settings" tab
3. In the left sidebar, click on "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Add each of these secrets:
   - Name: `API_KEY`
     Value: (Your Ambient Weather API Key)
   - Name: `APPLICATION_KEY`
     Value: (Your Ambient Weather Application Key)
   - Name: `ELLWOOD_MAIN_MAC`
     Value: (Your Ellwood Main MAC address)
   - Name: `ELLWOOD_MESA_MAC`
     Value: (Your Ellwood Mesa MAC address)

## 2. Create GitHub Actions Workflow

1. In your repository, create a new directory:
   ```bash
   mkdir -p .github/workflows
   ```

2. Create a new file `.github/workflows/weather_scraper.yml` with the following content:
   ```yaml
   name: Daily Weather Scraper

   on:
     schedule:
       # Runs at 12:30 AM Pacific Time (8:30 UTC)
       - cron: '30 8 * * *'
     workflow_dispatch:  # Allows manual triggering

   jobs:
     scrape:
       runs-on: ubuntu-latest
       
       steps:
       - uses: actions/checkout@v4
       
       - name: Set up Python
         uses: actions/setup-python@v5
         with:
           python-version: '3.x'
           
       - name: Install dependencies
         run: |
           python -m pip install --upgrade pip
           pip install -r requirements.txt
           
       - name: Run weather scraper
         env:
           API_KEY: ${{ secrets.API_KEY }}
           APPLICATION_KEY: ${{ secrets.APPLICATION_KEY }}
           ELLWOOD_MAIN_MAC: ${{ secrets.ELLWOOD_MAIN_MAC }}
           ELLWOOD_MESA_MAC: ${{ secrets.ELLWOOD_MESA_MAC }}
         run: python src/weather_scraper.py

       - name: Commit and push if there are changes
         run: |
           git config --local user.email "github-actions[bot]@users.noreply.github.com"
           git config --local user.name "github-actions[bot]"
           git add data/
           git diff --quiet && git diff --staged --quiet || (git commit -m "Update weather data" && git push)
   ```

## 3. Important Notes

1. The schedule is set to run at 12:30 AM Pacific Time (8:30 UTC). GitHub Actions uses UTC time, so we've converted the time accordingly.

2. The workflow includes `workflow_dispatch` which allows you to manually trigger the action from the GitHub Actions tab for testing.

3. The action will:
   - Set up Python
   - Install required dependencies
   - Run your weather scraper with the environment variables
   - Automatically commit and push any new data files to the repository

4. Make sure your repository has these files:
   - `requirements.txt` (already exists)
   - `.gitignore` (already exists and includes .env)
   - The workflow file created above

## 4. Testing the Setup

1. After setting up:
   - Push all changes to GitHub
   - Go to the "Actions" tab in your repository
   - Click on "Daily Weather Scraper" workflow
   - Click "Run workflow" to test it manually

2. Monitor the first run to ensure:
   - All environment variables are properly accessed
   - The script runs successfully
   - Data is properly saved and committed

## Troubleshooting

If you encounter any issues:
1. Check the Actions tab for detailed logs
2. Verify that all secrets are properly set
3. Ensure the repository has proper permissions to create commits
4. Confirm that the dependencies are properly listed in requirements.txt