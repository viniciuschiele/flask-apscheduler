"""App configuration."""


class Config:
    """Prod config."""

    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Dev config."""

    DEBUG = True
