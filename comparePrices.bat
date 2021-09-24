node comparer.js
echo "Finished comparing prices"
cd ./data_changes
git add -A && git commit -m "Automated Commit" --no-gpg-sign && git push origin master