import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = '8d6703b7bee093c9dbfbdb38pyth98eae3087046b051b728734ba4de9d7ebfbb05be'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_DATABASE_URI =  os.environ.get('DATABASE_URL') or \
    #     'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_DATABASE_URI =  os.environ.get('DATABASE_URL')
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    S3_BUCKET=os.environ.get("S3_BUCKET")
    AWS_ACCESS_KEY_ID=os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY=os.environ.get("AWS_SECRET_ACCESS_KEY")
    IMAGE_DEPLOY_FOLDER_LOCATION=os.environ.get("IMAGE_DEPLOY_FOLDER_LOCATION")

