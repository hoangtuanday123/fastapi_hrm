class isadmindata:
    def __init__(self):
        self.value="None"
is_admin=isadmindata()

class roleuserdata:
    def __init__(self):
        self.value=None
roleuser=roleuserdata()

class rolegroupdata:
    def __init__(self):
        self.value=None
rolegroup=rolegroupdata()

class readrightsdata:
    def __init__(self):
        self.value=None
readrights=readrightsdata()

class writerightsdata:
    def __init__(self):
        self.value=None
writerights=writerightsdata()

class verify_passworddata:
    def __init__(self):
        self.value=None
verify_password=verify_passworddata()

class messagesdata:
    def __init__(self):
        self.categorary=None
        self.message=None
    def message_array(self):
        self.data=[(self.categorary,self.message)]
        return self.data
messages=messagesdata()

class id_useraccountdata:
    def __init__(self):
        self.value=None
id_useraccount=id_useraccountdata()

class idaccountadminmanagerdata:
    def __init__(self):
        self.value=None
idaccountadminmanager=idaccountadminmanagerdata()

class selectionItemdata:
    def __init__(self):
        self.value=None
selectionItem=selectionItemdata()

class tabledata:
    def __init__(self): 
        self.value=None
tablesession=tabledata()

class image_path_admindata:
    def __init__(self): 
        self.value=None
image_path_adminsession=image_path_admindata()

class fullname_admindata:
    def __init__(self): 
        self.value=None
fullname_adminsession=fullname_admindata()
