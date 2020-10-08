// Load required modules
var https   = require("https");     // https server core module
var http = require("http");         // http server core module
var fs      = require("fs");        // file system core module
var express = require("express");   // web framework external module
var io      = require("socket.io"); // web socket external module
var easyrtc = require("open-easyrtc");   // EasyRTC external module
var ejs = require("ejs");
var redis = require('redis')

var myport = 8080;
var mykey = "";

if (process.argv[2])
    myport = process.argv[2];

if (process.argv[3])
    mykey = process.argv[3];

// Setup and configure Express http server. Expect a subfolder called "static" to be the web root.
var httpApp = express();
httpApp.engine('html', require('ejs').renderFile)
httpApp.use(express.static(__dirname + "/static/"));
httpApp.set('view engine', 'html');
httpApp.set('views', __dirname + '/protected');

httpApp.use('/teraplus', function(req, res){
        //res.send('key: ' + req.query.key);
        if (req.query.key == mykey || mykey == ""){
                // Authorized
                res.render('index.html', {teraplus_port: myport})
                //res.render('/index.html',{ root: __dirname + "/protected/"});
        }else{
                // Not authorized
                res.sendFile('/denied.html',{ root: __dirname + "/static/"});
        }
        //res.sendFile('/index.html',{ root: __dirname + "/protected/"});
});

httpApp.use('/status', function(req,res) {
  //Query server status
  if (req.query.key == mykey || mykey == "") {
    //Send the status of the server
    //TODO: add connected user information?
    //TODO: add active sessions informations?
    res.send({status: 'OK'})
  } else {
    // Not authorized
    res.sendFile('/denied.html',{ root: __dirname + "/static/"});
  }

});

// Start Express https server

var webServer = https.createServer(
{
    key:  fs.readFileSync("../python/certificates/site_key.pem"),
    cert: fs.readFileSync("../python/certificates/site_cert.pem")
},
httpApp).listen(myport);


//var webServer = http.createServer(httpApp).listen(myport);


// Start Socket.io so it attaches itself to Express server
var websocket_path = "/websocket/" + myport + '/'
console.log('websocket path:', websocket_path)
var socketServer = io.listen(webServer, {"log level":1, "path": websocket_path });


//TODO Set options here (ice servers)

var appIceServers = [
  {
    "url":"stun:telesante.3it.usherbrooke.ca:3478"
  },
  {
    "url":"turn:telesante.3it.usherbrooke.ca:50000", 
    "username":"teraplus",
    "credential":"teraplus"
  },
  {
    "url":"turn:telesante.3it.usherbrooke.ca:50000?transport=tcp",
    "username":"teraplus",
    "credential":"teraplus"
  }
];


/*
var appIceServers = [
    {urls: "stun:stun.l.google.com:19302"},
    {urls: "stun:stun.sipgate.net"},
    {urls: "stun:217.10.68.152"},
    {urls: "stun:stun.sipgate.net:10000"},
    {urls: "stun:217.10.68.152:10000"}
];
*/
easyrtc.setOption("appIceServers", appIceServers);
easyrtc.setOption("logLevel", "debug");
easyrtc.setOption("demosEnable", true);
//easyrtc.setOption("updateCheckEnable",false);

//Setup redis client (default configuration)
var client = redis.createClient()

client.on("connect", function() {
  console.log("Redis now connected");

  //Publish message that we are ready
  client.publish("webrtc." + mykey, "Ready!", 
  function(){
    console.log("Message published");
   });
});



// Start EasyRTC server
var rtc = easyrtc.listen(httpApp, socketServer);
