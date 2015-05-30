echo 
echo building distibution
python setup.py py2exe >dist_log.txt
xcopy templates dist\templates /s /y
xcopy static dist\static /y /s
xcopy run-listeningserver.bat dist  /y

pause

