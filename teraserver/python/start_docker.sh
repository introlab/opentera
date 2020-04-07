echo "Starting postresql"
service postgresql start
echo "Starting redis-server"
redis-server &
echo "Sleeping 5 secs."
sleep 5
echo "Starting TeraServer"
$PYTHON3_EXEC ./TeraServer.py &
sleep 5
echo "Starting VideoDispatchServer"
$PYTHON3_EXEC ./services/VideoDispatch/VideoDispatchService.py &
echo "Starting bash"
bash