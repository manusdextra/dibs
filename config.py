import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "JuicyReticentLemur"

    @staticmethod
    def init_app(app) -> None:
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
