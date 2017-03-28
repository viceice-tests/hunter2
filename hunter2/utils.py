import random
import configparser

def generate_secret_key():
    return ''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789_') for i in range(50)])

def load_or_create_secret_key(secrets_file):
    config = configparser.ConfigParser()
    config.read(secrets_file)

    if config.has_option('Secrets', 'django_secret_key'):
        secret_key = config.get('Secrets', 'django_secret_key')
    else:
        secret_key = generate_secret_key()

        # Write the configuration to the secrets file.
        config.add_section('Secrets')
        config.set('Secrets', 'django_secret_key', secret_key)
        with open(secrets_file, 'w+') as configfile:
            config.write(configfile)

    return secret_key