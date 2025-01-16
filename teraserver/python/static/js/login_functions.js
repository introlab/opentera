var endpointUrl = "";
var qtObject = undefined;
if (typeof QWebChannel !== "undefined"){
    new QWebChannel(qt.webChannelTransport, function(channel) {
        qtObject = channel.objects.qtObject;
    });
};

function login_redirect(target_url){
    let redirect_url;
    try{
        redirect_url = new URL(target_url);
        console.log("OK - Redirecting to " + redirect_url);
    }catch(err){
        redirect_url = new URL(window.location.origin);
        let parts = target_url.split("?");
        redirect_url.pathname = parts[0];
        if (parts.length > 1){
            redirect_url.search = new URLSearchParams(parts[1]);
        }
        console.log("Error - Redirecting to " + redirect_url);
    }

    //console.log(redirect_url);
    window.location.href = redirect_url.toString();
}

function redirectToLogin(){
    if (qtObject)
        qtObject.sendRedirectToLogin();
    else
        login_redirect("/login");
}
