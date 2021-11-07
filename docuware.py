import pickle, logging, json
import requests
from pathlib import Path

class Docuware:
  filecabinet_id = 'XXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXX'
  c_path = Path('cookies.bin')
  docuware_url = 'https://XXX.docuware.cloud'

  def login(self, credentials) -> None:
    # Session will hold the cookies
    s = requests.Session()
    s.headers.update({'User-Agent': 'welcome-letter'})
    s.headers.update({'Accept': 'application/json'})
    self.s = s
    if self.c_path.exists():
      with open(self.c_path, mode='rb') as f:
        self.s.cookies.update(pickle.load(f))
    else:
      url = f'{self.docuware_url}/docuware/platform/Account/Logon'
      payload = {
          'LicenseType': '',
          'UserName': credentials['user'],
          'Password': credentials['password'],
          'RedirectToMyselfInCaseOfError': 'false',
          'RememberMe': 'false',
      }
      headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
      }
      response = s.request('POST', url, headers=headers, data=payload, timeout=30)
      if response.status_code == 401:
        logging.info('Unable to log-in, this could also mean the user is rate limited, locked or user-agent missmatch.')
      response.raise_for_status()
      with open('cookies.bin', mode='wb') as f:
        pickle.dump(s.cookies, f)

      logging.debug('logged in with ' + credentials['user'])

  def upload(self, path, fields) -> dict:
    # upload file, by reusing login cookie
    p = Path(path)
    file_name = p.name
    url = f'{self.docuware_url}/docuware/platform/FileCabinets/{self.filecabinet_id}/Documents'
    f = []
    for key, value in fields.items():
      f.append({
        'FieldName': key,
        'Item': value,
        'ItemElementName': 'String',
      })

    index_json = '{"Fields": ' + json.dumps(f) + '}'
    multipart_form_data = {
      # name: (filename, data, content_type, headers)
      'document': (None, index_json, 'application/json'),
      'file[]': (file_name, p.read_bytes(), 'application/pdf'),
    }
    r = self.s.request('POST', url, files=multipart_form_data, timeout=30)
    r.raise_for_status()
    return r.json()

  def logout(self) -> None:
    url = f'{self.docuware_url}/docuware/platform/Account/Logoff'
    r = self.s.request('GET', url, timeout=30)
    r.raise_for_status()
    self.c_path.unlink()
