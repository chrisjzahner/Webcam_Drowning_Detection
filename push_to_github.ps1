# PowerShell script to push to GitHub
# Run this after Git is installed

Write-Host "Initializing Git repository..." -ForegroundColor Green
git init

Write-Host "Adding remote repository..." -ForegroundColor Green
git remote add origin https://github.com/chrisjzahner/Webcam_Drowning_Detection.git

Write-Host "Adding all files..." -ForegroundColor Green
git add .

Write-Host "Committing changes..." -ForegroundColor Green
git commit -m "Initial commit: Webcam Drowning Detection system"

Write-Host "Pushing to GitHub..." -ForegroundColor Green
git branch -M main
git push -u origin main

Write-Host "Done! Check your repository at https://github.com/chrisjzahner/Webcam_Drowning_Detection" -ForegroundColor Green

