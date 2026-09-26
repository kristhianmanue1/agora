"""Strict byte coverage preflight, separate from semantic model judgments."""
from .source import SourceError
from .sufficiency import assess, verify_envelope


def assess_with_coverage(adapter, revision, question, envelope_data, envelope_hash,
                         provider, *, scope, prompt_budget=65536):
    """Global scope requires every source byte in this context, not a prior scan.

    Full coverage permits a model judgment but never certifies completeness of
    its interpretation. Local scope explicitly limits conclusions to supplied text.
    Legacy assess() is unchanged. This API performs no retrieval or admission.
    """
    result = {'schema': 'agora/coverage-assessment/v0.1', 'scope': scope,
              'source_id': adapter.source_id, 'source_sha256': revision,
              'envelope_sha256': envelope_hash, 'question': question,
              'provider_calls': 0, 'mode': 'observe_only', 'action_taken': 'none',
              'memory_admission': 'not_performed',
              'semantic_verification': 'not_performed',
              'global_completeness': 'not_established'}
    try:
        if scope not in ('global', 'local'):
            raise SourceError('invalid_coverage_scope')
        if type(question) is not str or not question.strip() or len(question) > 2000:
            raise SourceError('invalid_question')
        envelope = verify_envelope(adapter, revision, envelope_data, envelope_hash)
        size = envelope['source']['source_bytes']
        missing = []
        cursor = 0
        for span in envelope['spans']:
            if span['start_byte'] > cursor:
                missing.append([cursor, span['start_byte']])
            cursor = span['end_byte']
        if cursor < size:
            missing.append([cursor, size])
        coverage = {'basis': 'exact_source_bytes_in_supplied_context',
                    'source_bytes': size, 'supplied_bytes': envelope['delivered_bytes'],
                    'missing_bytes': size - envelope['delivered_bytes'],
                    'missing_ranges': missing,
                    'status': 'partial' if missing else 'full',
                    'semantic_coverage': 'unknown'}
        result['coverage_check'] = coverage
        if scope == 'global' and missing:
            result.update(execution_status='complete',
                          assessment_status='not_run_incomplete_coverage',
                          global_review_status='blocked_incomplete_context')
            return result
        assessment = assess(adapter, revision, question, envelope_data, envelope_hash,
                            provider, prompt_budget=prompt_budget)
        result.update(assessment)
        result.update(schema='agora/coverage-assessment/v0.1', scope=scope,
                      coverage_check=coverage, global_completeness='not_established',
                      global_review_status='semantic_review_required' if scope == 'global'
                      else 'not_requested')
    except SourceError as exc:
        result.update(execution_status='rejected', diagnostic=str(exc))
    return result
