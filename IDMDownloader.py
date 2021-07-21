import comtypes.client as cc


def download(url, save_path, file_name):
    referrer = ""
    cookie = ""
    post = ""
    user = ""
    password = ""
    cc.GetModule(["{ECF21EAB-3AA8-4355-82BE-F777990001DD}", 1, 0])
    try:
        import comtypes.gen.IDManLib as IDMan
        idm1 = cc.CreateObject("IDMan.CIDMLinkTransmitter", None, None, IDMan.ICIDMLinkTransmitter2)
        idm1.SendLinkToIDM(url, referrer, cookie, post, user, password, save_path, file_name, 2)
    except ImportError:
        print("Couldn't import IDManLib")
