ssh bob@95.179.138.59
enter password

change the entry: * * * * * /home/bob/invoke_api.sh 2>&1 > /dev/null 
to entry: * 9-16 * * 1-5 /home/bob/invoke_api.sh 2>&1 > /dev/null 

save cat pictures:
scp bob@95.179.138.59:/home/bob/cat.jpeg ~/