// Load required modules
var https   = require("https");     // https server core module
var fs      = require("fs");        // file system core module
var express = require("express");   // web framework external module
var io      = require("socket.io"); // web socket external module
var easyrtc = require("easyrtc");   // EasyRTC external module
var myport = 40051;
var mykey = "";

if (process.argv[2])
    myport = process.argv[2];

if (process.argv[3])
    mykey = process.argv[3];


// Setup and configure Express http server. Expect a subfolder called "static" to be the web root.
var httpApp = express();
httpApp.use(express.static(__dirname + "/static/"));


httpApp.use('/teraplus', function(req, res){
        //res.send('key: ' + req.query.key);
        if (req.query.key == mykey || mykey == ""){
                // Authorized
                res.sendFile('/index.html',{ root: __dirname + "/protected/"});
        }else{
                // Not authorized
                res.sendFile('/denied.html',{ root: __dirname + "/static/"});
        }
        //res.sendFile('/index.html',{ root: __dirname + "/protected/"});
});


// Start Express https server on port 8443
var webServer = https.createServer(
{
    key:  fs.readFileSync("ssl/privkey.pem"),
    cert: fs.readFileSync("ssl/cert.pem")
},
httpApp).listen(myport);

// Start Socket.io so it attaches itself to Express server
var socketServer = io.listen(webServer, {"log level":1});


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
easyrtc.setOption("updateCheckEnable",false);


// Start EasyRTC server
var rtc = easyrtc.listen(httpApp, socketServer);
