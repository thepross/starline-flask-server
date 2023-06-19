class DevelopmentConfig():
    DEBUG=True

    MYSQL_HOST = '34.31.245.198'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '12345678'
    MYSQL_DB = 'db_starline'

config = {
    'development': DevelopmentConfig
}