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
    missing = result.get('missing') if complete else None
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
        'answer': result.get('answer') if complete else None,
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
