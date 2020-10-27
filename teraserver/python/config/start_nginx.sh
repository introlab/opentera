echo "stop nginx"
sudo nginx -s stop
echo "reconfigure and start nginx" 
sudo nginx -c nginx.conf -p $PWD
echo "nginx started."
