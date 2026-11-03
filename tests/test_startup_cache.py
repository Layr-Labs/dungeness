import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from dungeness.compiler import checkout
from dungeness.execution.timing import StartupTiming


class StartupCacheTests(unittest.TestCase):
    def test_pinned_cache_works_offline_and_materializes_fresh_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); repo=root/'repo'
            def git(*args):
                return subprocess.check_output(['git',*args],stderr=subprocess.DEVNULL,text=True).strip()
            git('init',str(repo));(repo/'file').write_text('official scaffold')
            git('-C',str(repo),'add','file')
            git('-C',str(repo),'-c','user.name=Test','-c','user.email=test@localhost',
                '-c','commit.gpgsign=false','commit','-m','fixture')
            commit=git('-C',str(repo),'rev-parse','HEAD');url='https://unreachable.invalid/problem.git'
            cache=root/'cache';cache.mkdir()
            key=hashlib.sha256((url+'\n'+commit).encode()).hexdigest()
            git('clone','--bare',str(repo),str(cache/key))
            with patch.dict(os.environ,{'DUNGENESS_REPOSITORY_CACHE':str(cache)}):
                checkout(url,commit,root/'one');(root/'one/file').write_text('prior candidate')
                checkout(url,commit,root/'two')
            self.assertEqual((root/'two/file').read_text(),'official scaffold')
            self.assertEqual(git('-C',str(root/'two'),'rev-parse','HEAD'),commit)

    def test_timing_is_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'startup.jsonl';timer=StartupTiming(path)
            for _ in range(200):timer.mark('render_started')
            timer.close()
            self.assertEqual(len(path.read_text().splitlines()),128)
            self.assertEqual(set(json.loads(path.read_text().splitlines()[0])),{'phase','at'})
