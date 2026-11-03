#!/usr/bin/env python3
"""Offline field and reservation validation; no credentials or model calls."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'services/gateway'))
from gateway_reservations import validate_generation

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--provider', required=True)
parser.add_argument('--operation', required=True, choices=['messages', 'responses', 'chat/completions', 'completions'])
parser.add_argument('--request', type=Path, required=True)
parser.add_argument('--pricing', type=Path, required=True, help='JSON schedule containing the exact provider/model')
parser.add_argument('--max-output-tokens', type=int, default=65536)
args = parser.parse_args()
try:
    payload = json.loads(args.request.read_text())
    schedule = json.loads(args.pricing.read_text())
    matches = [e for e in schedule['entries'] if e['provider'] == args.provider and payload.get('model') in e['request_models']]
    if len(matches) != 1:
        raise ValueError('Pricing must contain exactly one entry for this provider/model')
    _, tokens, usd = validate_generation(args.provider, args.operation, payload, matches[0], maximum=args.max_output_tokens)
    print(json.dumps({'valid': True, 'reservation_tokens': tokens, 'reservation_usd': usd,
                      'limitations': 'No authentication, live balance, routing or upstream compatibility check.'}))
except (ValueError, KeyError, TypeError) as error:
    print(json.dumps({'valid': False, 'error': str(error)}))
    raise SystemExit(1)
