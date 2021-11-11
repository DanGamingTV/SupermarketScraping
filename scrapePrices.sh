python3 example.py
echo "Finished scraping prices"
cd ./data
git add -A && git commit -m "Automated commit" --no-gpg-sign && git push origin master