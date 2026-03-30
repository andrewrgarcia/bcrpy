from bcrpy.main import Marco

def get(**kwargs):
    return Marco().GET(**kwargs)

def large_get(**kwargs):
    return Marco().largeGET(**kwargs)