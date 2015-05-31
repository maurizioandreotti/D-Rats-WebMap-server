echo off
cls
echo 
echo  listeningServer.exe 
echo 
echo  -o : output port, where to connect internet browsers http:\\IP:port
echo  -i : output port, where d-rats will send GPS fixes
echo  -x : longitude
echo  -y : latitude 
echo  -m : name of the html map to load (located in templates folder)
echo
echo  NOTE: there is currently a bug in this application : 
echo        once launched it will remain in background even after the cmd window is closed
echo        TO CLOSE IT, OPEN TASK MANAGER AND KILL "listeningserver.exe".
echo on


rem # sample 

rem python listeningServer.py -o 5010 -i 5011

rem python listeningServer.py -o 5010 -i 5011 -x 9.375 -y 45.835 -m map.html




ListeningServer -o 5010 -i 5011 -m map-31maggio.html x 9.375 -y 45.835
pause