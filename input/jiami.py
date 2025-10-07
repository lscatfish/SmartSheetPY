from encryption.encrypted import encrypt_email_authorization_code
from encryption.decrypted import decrypt_email_authorization_code

if __name__ == '__main__':
    yaml_path = 'email_yaml.yaml'
    key_path = '../my_secret.key'
    # encrypt_email_authorization_code(yaml_path, key_path)
    # aa = decrypt_email_authorization_code(yaml_path, key_path)
    # print(aa)
