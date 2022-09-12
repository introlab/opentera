let isWeb = true;
let translator = null;
let currentLang = 'fr';
const maxRemoteSourceNum = 8;
let browser = null;

function preInitSystem(){
    console.log("Pre-initializing system...");
    let urlParams = new URLSearchParams(window.location.search);
    let sourceParam = urlParams.get('source');
    if (sourceParam !== null)
        isWeb = (sourceParam === 'web');

    if (isWeb === false) {
        // Load QWebChannel library
        include("qrc:///qtwebchannel/qwebchannel.js");
    }

}

function initTranslator(){
    // Check for url parameters
    let urlParams = new URLSearchParams(window.location.search);

    let langParam = urlParams.get('lang');
    if (langParam !== null)
        currentLang = langParam;

    // Load translation module
    console.log("Loading translation module...");
    translator = new Translator({
        defaultLanguage: 'fr',
        filesLocation: 'i18n',
        debug: true
    });
    translator.fetch(['en', 'fr']).then(() => {
        // -> Translations are ready...
        translator.translatePageTo(currentLang);
    });
}

function initSystem(){
    console.log("Initializing system...");
    let urlParams = new URLSearchParams(window.location.search);
    let port = getTeraPlusPort(); // This function is rendered in the main html document
    let websocket_path =  "/websocket/" + port
    easyrtc.setSocketUrl(window.location.origin, {path: websocket_path});

    deviceEnumCompleted = false;

    let local_uuid = urlParams.get('uuid');
    if (local_uuid)
        localContact.uuid = local_uuid;

    let local_name = urlParams.get('name');
    if (local_name) {
        localContact.name = local_name;
        // Set names on local videos
        setTitle(true, 1, local_name);
        setTitle(true, 2, local_name);
    }

    // Initial local status
    localContact.status = {'microMuted': false, 'videoMuted': false, 'speakerMuted': false, 'sharing2ndSource': false,
                           'sharingScreen': false};

    // Initial capabilities
    browser = bowser.getParser(window.navigator.userAgent);
    localCapabilities.screenSharing = browser.getPlatformType() === 'desktop'; // Screen sharing only on desktop

    // Initialize video and audio sources
    fillDefaultSourceList().then(initSystemDone).catch(err => {
        showStatusMsg(translator.translateForKey("status.cant-continue", currentLang))
    })

    // Reset forms
    if ($('#chronosForm')[0] !== undefined)
        $('#chronosForm')[0].reset();
}

function initSystemDone(){

    if (isWeb){
        // Connect to signaling server
        connect();
    }else{
        // Connect Shared Object websocket, which will connect to system when ready
        connectSharedObject();

    }
}
