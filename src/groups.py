
from plumbum import local

__nodeattr = local['nodeattr']

def list():
    groups = __nodeattr('-l').split("\n")
    groups.remove('')
    return groups


