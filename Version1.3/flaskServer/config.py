
FLASK_ENV = 'development'
DEBUG = False
SECRET_KEY = 'AlrightThenKeepYourSecrets'

MONGO_URI = 'mongodb+srv://Dev:dev@cluster0.odagz.mongodb.net/lost?retryWrites=true&w=majority'
TESTING = False

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USERNAME = 'LOSTEXPRES1@gmail.com'
MAIL_PASSWORD = 'LostExpres2021'
MAIL_USE_TLS = False
MAIL_USE_SSL = True

ADMIN_EMAIL = 'LOSTEXPRES2@gmail.com'

csv_label = {
    # Dict of csv formatting options.
    # 'type': 'DEFINE LABEL HERE'
    'accept': 'ACCEPT',
    'filename': 'FILENAME',
    'flux': 'FLUX',
    'mjd': 'MJD',
    'v': 'V',
    'wavelength': '# WAVE',

}
rv_label = ['FILENAME', 'MJD', 'V']