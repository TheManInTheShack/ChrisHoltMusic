@ECHO OFF

REM git remote add origin http://github.com/TheManInTheShack/ChrisHoltMusic.git

git add -A

git commit -m %1

git push origin main
