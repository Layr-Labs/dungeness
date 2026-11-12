"""Both auth paths apply identical filesystem checks without changing schemas."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from gateway_auth import authentication_headers, credential_value

RECIPE = {'sources': [
    {'file_env': 'TEST_AUTH_FILE', 'headers': {'authorization': {'path': ['tokens','access_token'], 'prefix':'Bearer '},
                                             'account-id': {'path':['tokens','account_id']}}},
    {'headers': {'authorization': {'env':'FALLBACK_TOKEN'}}},
]}


class PrivateAuthFilesTests(unittest.TestCase):
    def read(self, path, nested):
        with patch.dict(os.environ, {'DUNGENESS_CREDENTIALS_FILE':str(path),
                                    'TEST_AUTH_FILE':str(path), 'FALLBACK_TOKEN':'must-not-use', 'token':'must-not-use'}):
            return authentication_headers(RECIPE) if nested else credential_value('token')

    def test_private_regular_files_and_nested_account_fields(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'auth.json';p.touch(mode=0o600)
            p.write_text(json.dumps({'tokens':{'access_token':'synthetic','account_id':'account'}}))
            self.assertEqual(self.read(p, True), {'authorization':'Bearer synthetic','account-id':'account'})
            p.write_text(json.dumps({'token':'synthetic'}))
            self.assertEqual(self.read(p, False), 'synthetic')

    def test_unsafe_files_fail_closed_with_redacted_errors(self):
        for nested in (False,True):
            for case in ('permissions','symlink','hardlink','directory','malformed','oversized'):
                with self.subTest(nested=nested,case=case), tempfile.TemporaryDirectory() as d:
                    p=Path(d)/'auth.json';p.touch(mode=0o600)
                    p.write_text(json.dumps({'token':'private-canary','tokens':{'access_token':'private-canary','account_id':'account'}}))
                    if case=='permissions':p.chmod(0o644)
                    elif case=='symlink':
                        link=Path(d)/'link';link.symlink_to(p);p=link
                    elif case=='hardlink':os.link(p,Path(d)/'other')
                    elif case=='directory':p=Path(d)
                    elif case=='malformed':p.write_text('{private-canary')
                    elif case=='oversized':p.write_text('private-canary'+'x'*131072)
                    with self.assertRaisesRegex(ValueError,'unavailable or invalid') as error:
                        self.read(p,nested)
                    self.assertNotIn('private-canary',str(error.exception))

    def test_fifo_rejected_without_waiting_for_writer(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'fifo';os.mkfifo(p,0o600)
            code="""import os
from gateway_auth import authentication_headers, credential_value
for fn in (lambda: credential_value('token'), lambda: authentication_headers({'sources':[{'file_env':'TEST_AUTH_FILE','headers':{}}]})):
 try: fn()
 except ValueError: pass
 else: raise AssertionError('FIFO was accepted')
"""
            subprocess.run([sys.executable,'-c',code],timeout=2,check=True,
                           env={**os.environ,'DUNGENESS_CREDENTIALS_FILE':str(p),'TEST_AUTH_FILE':str(p)})
