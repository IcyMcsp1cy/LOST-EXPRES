
FLASK_ENV = 'development'
DEBUG = True
SECRET_KEY = 'AlrightThenKeepYourSecrets'

MONGO_URI = 'mongodb+srv://Dev:dev@cluster0.odagz.mongodb.net/SolarExpres?retryWrites=true&w=majority'

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
    'velocity': 'V',
    'wavelength': '# WAVE',
}