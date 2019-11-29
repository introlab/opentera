echo "Starting postresql"
service postgresql start
echo "Starting redis-server"
redis-server &
echo "Sleeping 5 secs."
sleep 5
echo "Starting TeraServer"
python3.6 ./TeraServer.py
