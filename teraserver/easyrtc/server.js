// Load required modules
var https   = require("https");     // https server core module
var http = require("http");         // http server core module
var fs      = require("fs");        // file system core module
var express = require("express");   // web framework external module
var io      = require("socket.io"); // web socket external module
var easyrtc = require("open-easyrtc");   // EasyRTC external module
var ejs = require("ejs");
var redis = require('redis')

const minimist = require('minimist');

let args = minimist(process.argv.slice(2), {
    default: {
        port: 8080,
        key: "",
        local_ssl: false,
        debug: false
    },
});

console.log('args:', args);

// Setup and configure Express http server. Expect a subfolder called "static" to be the web root.
var httpApp = express();
httpApp.engine('html', require('ejs').renderFile)
httpApp.use(express.static(__dirname + "/static/"));
httpApp.set('view engine', 'html');
httpApp.set('views', __dirname + '/protected');

httpApp.use('/users', function(req, res){
        //res.send('key: ' + req.query.key);
        console.log(req.query.key);
        console.log(args.key);
        if (req.query.key == args.key || args.key == ""){
                // Authorized
                res.render('index_users.html', {teraplus_port: args.port})
                //res.render('/index.html',{ root: __dirname + "/protected/"});
        }else{
                // Not authorized
                res.sendFile('/denied.html',{ root: __dirname + "/static/"});
        }
        //res.sendFile('/index.html',{ root: __dirname + "/protected/"});
});

httpApp.use('/participants', function(req, res){
        //res.send('key: ' + req.query.key);
        if (req.query.key == args.key || args.key == ""){
                // Authorized
                res.render('index_participants.html', {teraplus_port: args.port})
                //res.render('/index.html',{ root: __dirname + "/protected/"});
        }else{
                // Not authorized
                res.sendFile('/denied.html',{ root: __dirname + "/static/"});
        }
        //res.sendFile('/index.html',{ root: __dirname + "/protected/"});
});

httpApp.use('/devices', function(req, res){
    //res.send('key: ' + req.query.key);
    if (req.query.key == args.key || args.key == ""){
        // Authorized
        res.render('index_participants.html', {teraplus_port: args.port}) // Same as participants for now.
        //res.render('/index.html',{ root: __dirname + "/protected/"});
    }else{
        // Not authorized
        res.sendFile('/denied.html',{ root: __dirname + "/static/"});
    }
    //res.sendFile('/index.html',{ root: __dirname + "/protected/"});
});

httpApp.use('/status', function(req,res) {
  //Query server status
  if (req.query.key == args.key || args.key == "") {
    //Send the status of the server
    //TODO: add connected user information?
    //TODO: add active sessions informations?
    res.send({status: 'OK'})
  } else {
    // Not authorized
    res.sendFile('/denied.html',{ root: __dirname + "/static/"});
  }

});

// Start Express https server on port 8443
if (args.local_ssl == false){
    var webServer = http.createServer(httpApp).listen(args.port);
}else{
    var webServer = https.createServer(
        {
            key:  fs.readFileSync("../python/certificates/site_key.pem"),
            cert: fs.readFileSync("../python/certificates/site_cert.pem")
        },
        httpApp).listen(args.port);
}

// Start Socket.io so it attaches itself to Express server
var websocket_path = "/websocket/" + args.port + '/'
//console.log('websocket path:', websocket_path)
var socketServer = io.listen(webServer, {"log level":1, "path": websocket_path, "cookie": false});


//TODO Set options here (ice servers)
const ice_file = './ice_servers.json'
var appIceServers = [];

try {
    if (fs.existsSync(ice_file)) {
        appIceServers = JSON.parse(fs.readFileSync(ice_file, "utf8"));
    }else{
        // Defaults to Google servers
        console.log('Using default ICE Servers...');
        appIceServers = [
            {urls: "stun:stun.l.google.com:19302"},
            {urls: "stun:stun.sipgate.net"},
            {urls: "stun:217.10.68.152"},
            {urls: "stun:stun.sipgate.net:10000"},
            {urls: "stun:217.10.68.152:10000"}
        ];
    }
} catch(err) {
    console.error(err)
}

console.log('Using ICE Servers: ' + appIceServers);
easyrtc.setOption("appIceServers", appIceServers);
if (args.debug != false){
    easyrtc.setOption("logLevel", "debug");
    easyrtc.setOption("demosEnable", true);
}
//easyrtc.setOption("updateCheckEnable",false);

//Setup redis client (default configuration)
var client = redis.createClient()

client.on("connect", function() {
  console.log("Redis now connected");

  //Publish message that we are ready
  client.publish("webrtc." + args.key, "Ready!",
  function(){
    console.log("Message published");
   });
});



// Start EasyRTC server
var rtc = easyrtc.listen(httpApp, socketServer);

