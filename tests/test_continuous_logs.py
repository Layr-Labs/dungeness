"""Exercise real pipes, abrupt termination and bounded continuous capture."""
import importlib.util
import json
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

RUNNER = Path(__file__).resolve().parents[1] / 'adapters/harbor/command_runner.py'

class ContinuousLogTests(unittest.TestCase):
    def test_output_survives_termination_before_harbor_returns(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); log = root/'output.txt'; task = root/'task.json'
            task.write_text(json.dumps({'workspace':temp,'output_log':str(log),'execution':{
                'entrypoint':[sys.executable,'-u','-c',
                    'import sys,time; print("stdout ready"); print("stderr ready",file=sys.stderr); time.sleep(60)']}}))
            child = subprocess.Popen([sys.executable,str(RUNNER),str(task)])
            try:
                deadline = time.monotonic()+5
                while time.monotonic()<deadline:
                    if log.exists() and b'stderr ready' in log.read_bytes(): break
                    time.sleep(.02)
                self.assertIsNone(child.poll())
                self.assertIn(b'stdout ready',log.read_bytes())
                self.assertIn(b'stderr ready',log.read_bytes())
                child.send_signal(signal.SIGTERM);child.wait(timeout=8)
                self.assertFalse(json.loads(log.with_suffix('.coverage.json').read_text())['complete'])
                self.assertEqual(log.stat().st_mode&0o777,0o600)
            finally:
                if child.poll() is None: child.kill();child.wait()

    def test_truncation_drains_output_and_reports_actual_size(self):
        spec=importlib.util.spec_from_file_location('log_runner',RUNNER)
        runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
        runner.MAX_LOG_BYTES=128
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'out.txt'
            process=subprocess.Popen([sys.executable,'-c','import sys;sys.stdout.write("x"*200000)'],
                stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True)
            self.assertEqual(runner.capture(process,path,[]),0)
            report=json.loads(path.with_suffix('.coverage.json').read_text())
            self.assertEqual(path.stat().st_size,128)
            self.assertEqual(report['observed_bytes'],200000)
            self.assertTrue(report['truncated']);self.assertTrue(report['complete'])

if __name__=='__main__':unittest.main()
