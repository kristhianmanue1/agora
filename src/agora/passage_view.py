"""Display a stored passage result without generating or validating its claims."""
import argparse
import hashlib
import json
from pathlib import Path
from .transform import unique_object


def display(result):
    """Keep answer, omissions and scope together; never salvage rejected content."""
    if type(result) is not dict:
        raise ValueError('invalid_result_object')
    complete = result.get('execution_status') == 'complete'
    answer = result.get('answer') if complete else None
    missing = result.get('missing') if complete else None
    parts = []
    if complete and result.get('schema') in ('agora/claim-evidence-query/v1', 'agora/claim-evidence-query/v2'):
        raw_parts = result.get('parts')
        if type(raw_parts) is not list or not raw_parts:
            raise ValueError('invalid_display_parts')
        for part in raw_parts:
            if (type(part) is not dict or type(part.get('id')) is not str
                    or type(part.get('claims')) is not list or type(part.get('missing')) is not list
                    or any(type(item) is not str for item in part['missing'])
                    or any(type(c) is not dict or type(c.get('text')) is not str for c in part['claims'])):
                raise ValueError('invalid_display_parts')
            parts.append({'id': part['id'], 'status': part.get('status'),
                          'answer': '\n'.join(c['text'] for c in part['claims']),
                          'missing': part['missing']})
        if 'answer' not in result:
            answer = '\n'.join(p['answer'] for p in parts)
        if 'missing' not in result:
            missing = [item for p in parts for item in p['missing']]
    warnings = ['Esta vista muestra datos guardados; no verifica su respaldo semántico.']
    if missing is None:
        warnings.append('Información faltante no declarada: no equivale a ausencia de faltantes.')
    if result.get('requires_expansion') is True:
        warnings.append('Lectura parcial: requiere ampliación antes de un cierre sobre la fuente completa.')
    if not complete:
        warnings.append('Ejecución no completada: la salida del proveedor no se presenta como respuesta candidata.')
    return {
        'schema': 'agora/passage-display/v1',
        'execution_status': result.get('execution_status'),
        'answer_status': result.get('answer_status'),
        'http_attempts': result.get('http_attempts'),
        'answer': answer,
        'parts': parts,
        'missing': missing,
        'answer_scope': result.get('answer_scope', 'unknown'),
        'requires_expansion': result.get('requires_expansion'),
        'document_absence_established': result.get('document_absence_established'),
        'semantic_support': result.get('semantic_support', 'unknown'),
        'review_status': result.get('review_status', 'unknown'),
        'memory_admission': result.get('memory_admission', 'unknown'),
        'diagnostic': result.get('diagnostic'),
        'warnings': warnings,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('result', type=Path)
    args = parser.parse_args()
    try:
        with args.result.open('rb') as stream:
            raw = stream.read(16 * 1024 * 1024 + 1)
        if len(raw) > 16 * 1024 * 1024:
            raise ValueError('result_too_large')
        view = display(json.loads(raw, object_pairs_hook=unique_object))
        view['result_sha256'] = hashlib.sha256(raw).hexdigest()
        view['result_path'] = str(args.result.resolve())
        print(json.dumps(view, ensure_ascii=True))
        return 0
    except (OSError, ValueError, UnicodeError) as exc:
        print(json.dumps({'display_status': 'rejected', 'diagnostic': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
