"""Conservative text-request reservations, not provider-enforced cash limits.

UTF-8 bytes plus framing allowance deliberately overestimate ordinary text
input. Opaque provider state, media and remote history cannot be bounded here.
"""
import json
import math

GENERATION = {'responses', 'chat/completions', 'completions', 'messages'}


def bounded_request(payload, operation, pricing, *, maximum=65536):
    if operation not in GENERATION:
        raise ValueError('This operation has no bounded generation contract; use explicit text generation.')
    if type(maximum) is not int or not 1 <= maximum <= 1048576:
        raise ValueError('Invalid trusted per-request output limit')
    for key in ('n', 'best_of'):
        if payload.get(key, 1) != 1 or isinstance(payload.get(key), bool):
            raise ValueError('Budgeted inference permits only one generated completion per request')
    if payload.get('previous_response_id') or payload.get('conversation'):
        raise ValueError('Send explicit local history for bounded inference')
    def opaque(value):
        if isinstance(value, dict):
            if value.get('encrypted_content') or value.get('type') in ('redacted_thinking', 'reasoning.encrypted', 'compaction'):
                return True
            return any(opaque(item) for item in value.values())
        elif isinstance(value, list):
            return any(opaque(item) for item in value)
        return False
    fields = [k for k in ('max_output_tokens', 'max_completion_tokens', 'max_tokens') if k in payload]
    if len(fields) > 1:
        raise ValueError('Use a single output-token limit')
    allowed_fields = ({'max_output_tokens'} if operation == 'responses'
                      else {'max_tokens', 'max_completion_tokens'} if operation == 'chat/completions'
                      else {'max_tokens'})
    if fields and fields[0] not in allowed_fields:
        raise ValueError('Output-token limit does not match this API operation')
    limit = payload[fields[0]] if fields else min(maximum, 16384)
    if type(limit) is not int or not 1 <= limit <= maximum:
        raise ValueError(f'Per-request output limit must be 1..{maximum} tokens')
    result = dict(payload)
    key = (fields[0] if fields else 'max_output_tokens' if operation == 'responses'
           else 'max_completion_tokens' if operation == 'chat/completions' else 'max_tokens')
    result[key] = limit
    if opaque(payload.get('input', [])) or opaque(payload.get('messages', [])):
        # Ciphertext is not a token count. Preserve supported protocol history,
        # but admit it exclusively against the entire remaining allowance.
        return result, None, None
    # Includes tools and message framing. No claim of exact model tokenization.
    inputs = len(json.dumps(result, ensure_ascii=False, separators=(',', ':')).encode()) + 1024
    tiers = [pricing, *([pricing['long_context']] if pricing.get('long_context') else [])]
    input_rate = max(float(t.get(k, t['input_per_mtok'])) for t in tiers
                     for k in ('input_per_mtok', 'cached_read_per_mtok', 'cache_write_per_mtok', 'cache_write_1h_per_mtok'))
    output_rate = max(float(t['output_per_mtok']) for t in tiers)
    # The optional token ceiling counts weighted cache tokens, not only raw tokens.
    input_weight = max(1.0, *[float(t.get(k, t['input_per_mtok'])) / float(t['input_per_mtok'])
                             for t in tiers if t['input_per_mtok'] > 0
                             for k in ('cached_read_per_mtok', 'cache_write_per_mtok', 'cache_write_1h_per_mtok')])
    tokens = math.ceil(inputs * input_weight) + limit
    usd = (inputs * input_rate + limit * output_rate) / 1e6
    if not math.isfinite(usd) or usd < 0:
        raise ValueError('Invalid request reservation pricing')
    return result, tokens, usd
