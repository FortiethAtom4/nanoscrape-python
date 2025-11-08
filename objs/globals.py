# file for global variables etc.


# list of recognized domains and the modules that handle them.
DOMAINS = {
    "ciao.shogakukan.co.jp":"objs.ciao",
    "youngchampion.jp":"objs.champion",
    "booklive.jp":"objs.booklive",
    "shonenjumpplus.com":"objs.shonenjumpplus",
    "kuragebunch.com":"objs.kurage-bunch",
    "storia.takeshobo.co.jp":"objs.takeshobo"
}

class BadLogin(Exception):
    def __init__(self):
        self.msg = "Login unsuccessful."
        super().__init__(self.msg)