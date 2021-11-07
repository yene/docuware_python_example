from .docuware import Docuware
import os

def main():
  dw = Docuware()
  credentials = {'user': os.environ['DOCUWARE_USER'], 'password': os.environ['DOCUWARE_PASSWORD']}
  dw.login(credentials)
  fields = {
    'FIELDNAME': 'field value'
  }
  res = dw.upload('file_path.pdf', fields)
  dw.logout()

if __name__ == "__main__":
    main()
