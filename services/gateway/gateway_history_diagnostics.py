"""Structural rejection details; never retain conversation values or unknown keys."""
from contextlib import contextmanager

DIAGNOSTICS_VERSION = 1
KNOWN_TYPES = frozenset('''message reasoning compaction function_call function_call_output
custom_tool_call custom_tool_call_output local_shell_call local_shell_call_output
shell_call shell_call_output apply_patch_call apply_patch_call_output tool_search_call
tool_search_output text input_text output_text thinking redacted_thinking tool_use
tool_result refusal input_image image input_audio audio document input_file file
server_tool_use web_search_call file_search_call mcp_call'''.split())
PROVIDERS = frozenset(('openai', 'openai-chatgpt', 'anthropic', 'claude-subscription',
                       'openrouter', 'grok-subscription', 'minimax', 'gemini'))
OPERATIONS = frozenset(('responses', 'responses/compact', 'chat/completions',
                        'messages', 'messages/count_tokens'))


def value_type(value):
    return {dict: 'object', list: 'array', str: 'string', int: 'number',
            float: 'number', bool: 'boolean', type(None): 'null'}.get(type(value), 'other')


def known_type(value):
    return value if isinstance(value, str) and value in KNOWN_TYPES else 'other'


class HistoryShapeError(ValueError):
    def __init__(self, rule, message, *, path=(), expected=None, actual=None, field_index=None):
        super().__init__(message)
        self.history_path = list(path)
        self.shape = {'validation_rule': rule}
        if expected is not None:
            self.shape.update(expected_type=expected, actual_type=value_type(actual))
        if field_index is not None:
            self.shape['field_index'] = field_index


@contextmanager
def history_at(segment, **labels):
    """Attach only programmer-supplied path segments and numeric positions."""
    try:
        yield
    except ValueError as error:
        error.history_path = [segment, *getattr(error, 'history_path', [])]
        metadata = getattr(error, 'history_labels', {})
        # Outer item labels identify the input/message, not a nested tool block.
        for key, value in labels.items():
            metadata.setdefault(key, value)
        error.history_labels = metadata
        raise


def describe(error, provider, operation):
    path = getattr(error, 'history_path', [])
    rendered = ''.join(('[' + str(part) + ']') if isinstance(part, int)
                       else ('.' if index else '') + part for index, part in enumerate(path))
    details = {'diagnostics_version': DIAGNOSTICS_VERSION,
               'provider': provider if provider in PROVIDERS else 'other',
               'operation': operation if operation in OPERATIONS else 'other'}
    if rendered:
        details['path'] = rendered
    details.update(getattr(error, 'history_labels', {}))
    details.update(getattr(error, 'shape', {}))
    details.setdefault('validation_rule', 'unsupported_structure')
    return details
