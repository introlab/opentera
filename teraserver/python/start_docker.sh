echo "Starting postresql"
service postgresql start
echo "Starting redis-server"
service redis-server start
#redis-server &
echo "Sleeping 5 secs."
sleep 5
echo "Starting TeraServer"
$PYTHON3_EXEC ./TeraServer.py

