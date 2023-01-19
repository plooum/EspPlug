import hashlib
import utils
import binascii
import json

file_pass = "pass.json"
key_pass = "password"
default_password = "esp"

class Security:

    def __init__(self):
        self.pass_tab = {}        
        try:
            f = open(file_pass, 'r')
            s = f.read()
            self.pass_tab = json.loads(s)
        except Exception as e:
            pass
        
        if(not(key_pass in self.pass_tab.keys()) or str(self.pass_tab[key_pass]) == ""):
            print(default_password)
            self.pass_tab[key_pass] = default_password
        cnt = len(self.pass_tab[key_pass])

        if (not( cnt > 1 and self.pass_tab[key_pass][0] == '{' and self.pass_tab[key_pass][cnt-1] == '}')):
            sha256 = hashlib.sha256(self.pass_tab[key_pass].encode('UTF-8'))
            hash_ = "{"+binascii.hexlify(sha256.digest()).decode('UTF-8')+"}"
            self.pass_tab[key_pass] = hash_
            self.save()

    def check_password(self, input_):
        try:
            sha256 = hashlib.sha256(input_.encode('UTF-8'))
            input_sha = "{" + binascii.hexlify(sha256.digest()).decode('UTF-8') + "}"
            if (input_sha == self.password_sha()):
                return True
            else:
                return False
        except Exception as e:
            utils.trace("Security : Error, " + str(e))
            pass
    def password_sha(self):
        return self.pass_tab[key_pass]
    
    def change(self, new_input):
        try:
            if(new_input is None or new_input == ""):
                return False
            sha256 = hashlib.sha256(new_input.encode('UTF-8'))
            new_input_sha = "{" + binascii.hexlify(sha256.digest()).decode('UTF-8') + "}"
            self.pass_tab[key_pass] = new_input_sha
            self.save()
            return True
        except Exception as e:
            utils.trace("Security : Error, " + str(e))
            return False

    def save(self):
        try:
            f = open(file_pass, 'w')
            f.write(json.dumps(self.pass_tab))
            f.close()
        except Exception as e:
            utils.trace("Security : Error, " + str(e))

