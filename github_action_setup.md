# Setting Up GitHub Actions for Weather Scraper

This guide will help you set up a GitHub Action to run your weather scraper script daily at 12:30 AM Pacific Time.

## 1. Create a Personal Access Token (PAT)

1. Go to your GitHub account settings (click your profile picture → Settings)
2. Scroll down to "Developer settings" (bottom of left sidebar)
3. Click on "Personal access tokens" → "Tokens (classic)"
4. Click "Generate new token" → "Generate new token (classic)"
5. Give it a descriptive name (e.g., "Weather Scraper Workflow")
6. Set expiration as needed (you can set it to "No expiration" for long-term use)
7. Select these permissions:
   - `repo` (Full control of private repositories)
8. Click "Generate token"
9. **IMPORTANT**: Copy the token immediately - you won't be able to see it again!

## 2. Set Up GitHub Secrets

1. Go to your GitHub repository
2. Click on "Settings" tab
3. In the left sidebar, click on "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Add each of these secrets:
   - Name: `PAT_TOKEN`
     Value: (The Personal Access Token you just created)
   - Name: `API_KEY`
     Value: (Your Ambient Weather API Key)
   - Name: `APPLICATION_KEY`
     Value: (Your Ambient Weather Application Key)
   - Name: `ELLWOOD_MAIN_MAC`
     Value: (Your Ellwood Main MAC address)
   - Name: `ELLWOOD_MESA_MAC`
     Value: (Your Ellwood Mesa MAC address)

## 3. GitHub Actions Workflow

The workflow file (.github/workflows/weather_scraper.yml) is already configured to:
- Run daily at 12:30 AM Pacific Time
- Use your environment variables securely via GitHub Secrets
- Automatically commit and push new weather data

## 4. Testing the Setup

1. After setting up all secrets:
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
3. Ensure the PAT_TOKEN has the correct repository permissions
4. Check that the token hasn't expired
5. Verify the repository name and branch in the push command
6. Make sure the data directory exists and is writable

For permission errors:
- Double-check that your PAT has the `repo` scope
- Verify the token is correctly saved in repository secrets
- Ensure the token hasn't been revoked or expired

For script execution errors:
- Check the Python dependencies are correctly listed in requirements.txt
- Verify all environment variables are properly set
- Review the script's output in the workflow logs