# tera
Tera (TeraPlus, TeraServer, TeraWeb)


# Compilation dans Windows

* Attention, les librairies OpenSSL (libeay32.dll et ssleay32.dll) doivent être copiées dans le répertoire BIN pour que l'encryption fonctionne (HTTPS).

# Compilation pour Mac

Bug report:
* changer #ifdef QT_NO_OPENSSL pour #ifdef  QT_NO_SSL dans : [sslloader.cpp](https://github.com/HerikLyma/CPPWebFramework/blob/20c1bc900614eb04c3b97adfec6115d570aea733/CPPWebFramework/cwf/sslloader.cpp#L41)
and [httpreadrequest.cpp](https://github.com/HerikLyma/CPPWebFramework/blob/20c1bc900614eb04c3b97adfec6115d570aea733/CPPWebFramework/cwf/httpreadrequest.cpp#L36)
