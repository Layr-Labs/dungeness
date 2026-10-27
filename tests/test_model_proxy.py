"""Explicit operator proxy routing; ambient proxies must remain ignored."""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'services/gateway'))
from gateway_runtime import trusted_model_proxy

class ProxyTests(unittest.TestCase):
    def test_ambient_proxy_is_ignored(self):
        with patch.dict(os.environ,{'HTTPS_PROXY':'http://unexpected:3128'},clear=True):
            self.assertIsNone(trusted_model_proxy())
    def test_explicit_proxy_has_no_embedded_credential_or_path(self):
        for value in ('https://proxy:3128','http://user:password@proxy:3128','http://proxy:3128/path',
                      'http://proxy','http://proxy:3128?secret=x','http://proxy:3128#fragment'):
            with patch.dict(os.environ,{'DUNGENESS_MODEL_HTTPS_PROXY':value},clear=True):
                with self.assertRaises(ValueError):trusted_model_proxy()
        with patch.dict(os.environ,{'DUNGENESS_MODEL_HTTPS_PROXY':'http://172.30.0.1:3129'},clear=True):
            self.assertEqual(trusted_model_proxy(),'http://172.30.0.1:3129')

if __name__=='__main__':unittest.main()
