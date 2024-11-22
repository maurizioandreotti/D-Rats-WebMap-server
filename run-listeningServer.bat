echo .
echo  listeningServer.exe 
echo .
echo  -o : output port, where to connect internet browsers http:\\IP:port
echo  -i : output port, where d-rats will send GPS fixes
echo  -x : longitude
echo  -y : latitude 
echo  -m : name of the html map to load (located in templates folder)
echo
echo
echo 


rem # sample to execute python interpreted

 rem python listeningServer.py -o 8010 -i 8011
 rem python listeningServer.py -o 8010 -i 8011 -x 9.375 -y 45.835 -m map.html
 rem python listeningServer.py -o 8010 -i 8011 -m map-resegup.html
 rem python listeningServer.py -o 8010 -i 8011 -m map.html
 rem python listeningServer.py -o 8010 -i 8011 -x 9.375 -y 45.835 -m map-31maggio.html

 python listeningServer.py -o 8010 -i 8011 -x 9.375 -y 45.835 -m map-resegup.html

rem # sample to execute if compiled on windows

rem  listeningServer.exe -o 8010 -i 8011 -x 9.375 -y 45.835 -m map-osm.html
pause