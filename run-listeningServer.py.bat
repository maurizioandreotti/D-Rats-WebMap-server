echo .
echo  listeningServer.exe 
echo .
echo  -o : output port, where to connect internet browsers http:\\IP:port
echo  -i : output port, where d-rats will send GPS fixes
echo  -x : longitude
echo  -y : latitude 
echo  -m : name of the html map to load (located in templates folder)
echo  -k : set to 1 to generate CSV file
echo
echo 


rem # sample 

 rem python listeningServer.py -o 5010 -i 5011
 rem python listeningServer.py -o 5010 -i 5011 -x 9.375 -y 45.835 -m map.html
 rem python listeningServer.py -o 5010 -i 5011 -m map-resegup.html
 rem python listeningServer.py -o 5010 -i 5011 -m map.html
 rem python listeningServer.py -o 5010 -i 5011 -x 9.375 -y 45.835 -m map-31maggio.html

c:\python27\python.exe listeningServer-KML.py -o 5010 -i 5011 -x 9.375 -y 45.835 -m map.html -k 1


pause
