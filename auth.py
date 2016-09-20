from werkzeug.security import generate_password_hash, \
     check_password_hash

class User(object):

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

if __name__ == '__main__':
	Steve = User('test','defaultpassword')

	print Steve.pw_hash
	print Steve.check_password('password')
	print Steve.check_password('defaultpassword')