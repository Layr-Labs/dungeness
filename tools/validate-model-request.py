#!/usr/bin/env python3
"""Offline field and reservation validation; no credentials or model calls."""
import argparse
import json
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'services/gateway'))
from gateway_reservations import validate_generation
from model_access import MODEL_ACCESS, upstream_model

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--provider', required=True)
parser.add_argument('--operation', required=True, choices=['messages', 'responses', 'chat/completions', 'completions'])
parser.add_argument('--request', type=Path, required=True)
parser.add_argument('--pricing', type=Path, default=ROOT / 'services/gateway/pricing.yaml',
                    help='JSON or YAML schedule; defaults to the bundled reference prices')
parser.add_argument('--max-output-tokens', type=int, default=65536)
args = parser.parse_args()
try:
    if args.provider not in MODEL_ACCESS:
        raise ValueError('Unknown access route; inspect dungeness providers --details')
    if args.operation not in MODEL_ACCESS[args.provider]['routes']:
        raise ValueError('Operation is not supported by the selected access route')
    payload = json.loads(args.request.read_text())
    if not isinstance(payload, dict):
        raise ValueError('Request must be a JSON object')
    schedule = yaml.safe_load(args.pricing.read_text())
    matches = [e for e in schedule['entries'] if e['provider'] == args.provider and payload.get('model') in e['request_models']]
    if len(matches) != 1:
        raise ValueError('Pricing must contain exactly one entry for this provider/model')
    checked, tokens, usd = validate_generation(args.provider, args.operation, payload, matches[0], maximum=args.max_output_tokens)
    config = MODEL_ACCESS[args.provider]
    if config.get('transport', 'passthrough') != 'passthrough':
        from gateway_google import request_body
        upstream_model(config, checked['model'])
        request_body(checked)
    print(json.dumps({'valid': True, 'reservation_tokens': tokens, 'reservation_usd': usd,
                      'limitations': 'No authentication, live balance, routing or upstream compatibility check.'}))
except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as error:
    print(json.dumps({'valid': False, 'error': str(error)}))
    raise SystemExit(1)
