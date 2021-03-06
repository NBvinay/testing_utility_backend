def getUrlParamatersGeneral(request):
    db_type, uname, password, domain, dbname = request.GET['db_type'], request.GET['username'], request.GET['password'], \
                                               request.GET['domain'], request.GET['dbName']
    return db_type, uname, password, domain, dbname


def getUrlParamatersLeft(request):
    db_type, uname, password = request.GET['db_type_left'], request.GET['username_left'], request.GET['password_left']
    domain, dbname = request.GET['domain_left'], request.GET['dbName_left']
    return db_type, uname, password, domain, dbname


def getUrlParamatersRight(request):
    db_type, uname, password = request.GET['db_type_right'], request.GET['username_right'], request.GET[
        'password_right']
    domain, dbname = request.GET['domain_right'], request.GET['dbName_right']
    return db_type, uname, password, domain, dbname


def getUrlParamatersLeftWithQuery(request):
    db_type, uname, password, domain, dbname = getUrlParamatersLeft(request)
    sqlQuery_left = request.GET['sqlQuery_left']
    return db_type, uname, password, domain, dbname, sqlQuery_left


def getUrlParamatersRightWithQuery(request):
    db_type, uname, password, domain, dbname = getUrlParamatersRight(request)
    sqlQuery_right = request.GET['sqlQuery_right']
    return db_type, uname, password, domain, dbname, sqlQuery_right


def getDbEngineConnector(db_type):
    db_type = db_type.lower()
    if db_type == 'sqlite':
        return 'sqlite'
    if db_type == 'mysql':
        return 'mysql+pymysql'
    if db_type == 'db2':
        return 'ibm_db_sa'
    if db_type == 'oracle':
        return 'oracle+cx_oracle'
    if db_type == 'teradata':
        return 'teradatasql'


def getConnectorSTring(db_type, uname, password, domain, dbname):
    db_type = db_type.lower()

    if db_type == 'sqlite':
        return getDbEngineConnector(db_type) + ":///" + dbname
    if db_type == 'mysql':
        return getDbEngineConnector(db_type) + "://" + uname + ":" + password + "@" + domain + "/" + dbname
    if db_type == "db2":
        return getDbEngineConnector(db_type) + "://" + uname + ":" + password + "@" + domain + "/" + dbname


def get_filtered_schema_compare(nested_dictionary):
    source_only = {}
    target_only = {}
    others = {}
    finalDict = {}
    new_key = ''

    def get_all_values(nested_dictionary, new_key):
        for key, value in nested_dictionary.items():
            if type(value) is dict:
                new_key += ' --> ' + key
                get_all_values(value, new_key)
                new_key = new_key[: new_key.rfind(' --> ')]
            else:
                key = key.replace('right', 'target')
                key = key.replace('left', 'source')
                key = new_key + ' --> ' + key
                temp = {key: value}
                finalDict.update(temp)
    get_all_values(nested_dictionary, '')
    return finalDict
