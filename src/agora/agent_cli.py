"""Agent-oriented discovery and explicit dispatch; no implicit provider use."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
# Metadata describes entry points, not permission to execute or semantic guarantees.
ENTRIES = {
    'issues': ('scripts/agora_issues.py', None, 'Preparar, recuperar, generar, revisar y reparar pendientes.', 'workspace y argumentos del subcomando', 'archivos y JSON según operación', 'may_write_workspace', 'explicit_live_only', 'docs/pendientes-cli.md'),
    'relations': ('scripts/agora_relations.py', None, 'Listar evidencia, crear plantilla o validar relación candidata.', 'fuente UTF-8 e identidad; candidato para validate', 'JSON; campos faltantes o revisión pendiente', 'stdout_only', 'none', 'docs/relaciones-candidatas.md'),
    'relation-run': ('scripts/agora_relation_run.py', None, 'Generar o revisar relaciones; v2 separa versión de configuración.', 'fuente, SHA, salida nueva; respuesta conservada o proveedor explícito', 'result.json y candidato si válido', 'writes_new_output_directory', 'explicit_live_only', 'docs/relaciones-candidatas.md'),
    'evidence': ('src/agora/evidence_cli.py', 'agora.evidence_cli', 'Consultar una fuente por aspectos con citas o IDs.', 'fuente, SHA, aspectos, modelo y presupuestos', 'candidato con evidencia y artefactos', 'writes_output_directory', 'provider_call', 'docs/contrato-afirmaciones-evidencia.md'),
    'answer': ('src/agora/evidence_answer_flow.py', 'agora.evidence_answer_flow', 'Responder una pregunta sobre una fuente UTF-8 con generación y revisiones optativas.', 'fuente, SHA, pregunta, requisitos, proveedor explícito y salida nueva', 'candidato, revisiones, manifiesto y recibos; sin admisión', 'writes_new_output_directory', 'explicit_live_or_replay', 'docs/contrato-consulta-evidencia-v1.md'),
    'answer-v2': ('src/agora/evidence_answer_flow_v2.py', 'agora.evidence_answer_flow_v2', 'Responder con presupuestos de salida explícitos para cada etapa.', 'fuente UTF-8 hasta 160 KB, SHA, pregunta, requisitos, presupuestos optativos y salida nueva', 'candidato, revisiones y recibos con presupuesto fijado; sin admisión', 'writes_new_output_directory', 'explicit_live_only', 'docs/contrato-consulta-evidencia-v1.md'),
    'jev-review': ('src/agora/jev_flow_review.py', 'agora.jev_flow_review', 'Añadir consejo Jev a un recorrido answer ya terminado, sin repetir GLM.', 'resultado answer, fuente original y salida nueva', 'etiquetas Jev separadas y recibos; sin admisión', 'writes_new_output_directory', 'explicit_live_only', 'docs/contrato-consulta-evidencia-v1.md'),
    'export-answer': ('src/agora/consultation_package.py', 'agora.consultation_package', 'Exportar candidato y revisiones en un paquete verificable para un consumidor.', 'fuente, recorrido answer, Jev optativo, intercambio y original optativos', 'paquete JSON con afirmaciones, citas, alcances y estados', 'writes_new_output_directory', 'none', 'docs/contrato-consulta-evidencia-v1.md'),
    'skopos-page-v02': ('src/agora/skopos_page_v02_bridge.py', 'agora.skopos_page_v02_bridge', 'Construir derivado y localizadores de página CTIM desde respuesta Skopos v0.2.', 'solicitud, respuesta, manifiesto y SHA esperado, original local e item IDs', 'derived.txt y exchange.json; texto de extracción sin revisión visual', 'writes_new_output_directory', 'none', 'docs/contrato-paquete-consulta-aria-experto-v1.md'),
    'route': ('src/agora/routed_cli.py', 'agora.routed_cli', 'Consultar fuente completa o representación previa.', 'fuente, revisión, pregunta y selección de ruta', 'respuesta candidata y artefactos', 'writes_output_directory', 'provider_call', 'docs/seleccion-ruta-y-partes.md'),
    'traverse': ('src/agora/traversal_cli.py', 'agora.traversal_cli', 'Recorrer una fuente por unidades con presupuesto.', 'fuente, SHA, modelo y límites', 'representaciones y artefactos de recorrido', 'writes_output_directory', 'provider_calls', 'docs/recorrido-acotado.md'),
    'summarize': ('src/agora/__main__.py', 'agora', 'Crear el resumen candidato inicial.', 'fuente, SHA, modelo y salida', 'resumen candidato y referencias', 'writes_output_directory', 'provider_call', 'README.md'),
    'view': ('src/agora/passage_view.py', 'agora.passage_view', 'Inspeccionar respuesta guardada, faltantes y alcance.', 'resultado JSON existente', 'vista sin nueva evaluación semántica', 'stdout_only', 'none', 'README.md'),
}


def command(name):
    entry = ENTRIES[name]
    if entry[1]:
        bootstrap = 'import runpy,sys;sys.path.insert(0,sys.argv.pop(1));runpy.run_module(sys.argv.pop(1),run_name="__main__",alter_sys=True)'
        return [sys.executable, '-c', bootstrap, str(ROOT/'src'), entry[1]]
    return [sys.executable, str(ROOT / entry[0])]


def describe(name):
    path, module, purpose, inputs, outputs, writes, network, guide = ENTRIES[name]
    return {'id': name, 'purpose': purpose, 'maturity': 'experimental',
            'entrypoint': str(ROOT / path), 'inputs': inputs, 'outputs': outputs,
            'filesystem_effects': writes, 'network_effects': network,
            'prerequisites': ['local checkout and Python', 'consult subcommand help for required files and credentials'],
            'help_command': [sys.executable, str(ROOT/'scripts/agora.py'), 'run', name, '--help'],
            'command_prefix': [sys.executable, str(ROOT/'scripts/agora.py'), 'run', name],
            'guide': str(ROOT / guide),
            'result_limits': ['A successful process is not semantic acceptance.', 'No automatic admission.'],
            'errors': 'Native CLI conventions apply; inspect --help and guide. No universal exit/status contract is claimed.'}


def doctor():
    paths = {key: (ROOT/value[0]).is_file() and (ROOT/value[7]).is_file() for key,value in ENTRIES.items()}
    documented_python = sys.version_info >= (3, 10)
    return {'schema': 'agora/doctor/v1', 'status': 'ok' if all(paths.values()) and documented_python else 'attention',
            'python': sys.version.split()[0], 'python_executable': sys.executable,
            'documented_python_minimum': '3.10', 'meets_documented_python': documented_python,
            'entrypoints_and_guides_present': paths, 'repository': str(ROOT),
            'network_calls': 0, 'files_written': 0,
            'not_checked': ['credentials', 'provider availability', 'datasets', 'workspace integrity', 'semantic quality'],
            'next_step': 'Run the offline example, then describe the chosen capability.' if documented_python else 'Use Python 3.10+ (the local .venv if available), then rerun doctor.'}


def example():
    from .relation_candidates import template, evidence, validate
    raw = b'Atlas is a translation system. It receives complete sentences and is evaluated with BLEU.'
    candidate = template(raw, 'offline-example', contract_version='v2')
    uid = evidence(raw, 'offline-example')['units'][0]['id']
    for field,text in [('system','Atlas'),('task','translation'),('input','complete sentences'),('evaluation','BLEU')]:
        candidate['fields'][field] = {'text':text, 'evidence_ids':[uid]}
    candidate['relation_evidence_ids'] = [uid]
    result = validate(raw, 'offline-example', candidate)
    return {'schema':'agora/offline-example/v1', 'example':'relations-offline',
            'network_calls':0, 'files_written':0, 'source':raw.decode(), 'result':result,
            'expected': {'status':'needs_more_evidence','unknown_fields':['software_version','model_configuration'], 'admitted':False},
            'interpretation':'Unknown version/configuration are retained; valid IDs do not prove semantic support.'}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # Pass native help and all native flags unchanged; never use a shell.
    if argv and argv[0] == 'run' and len(argv) >= 2 and argv[1] in ENTRIES:
        args = argv[2:]
        if args[:1] == ['--']: args = args[1:]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(ROOT/'src'))
        return subprocess.run(command(argv[1]) + args, env=env).returncode
    parser = argparse.ArgumentParser(description='Ágora para agentes: descubrir, describir y ejecutar explícitamente. Empezar con capabilities --json; ejemplo sin red: example relations-offline --json.')
    sub = parser.add_subparsers(dest='action', required=True)
    for name in ['capabilities','doctor','examples']:
        sub.add_parser(name).add_argument('--json', action='store_true')
    d = sub.add_parser('describe');d.add_argument('capability',choices=ENTRIES);d.add_argument('--json',action='store_true')
    e = sub.add_parser('example');e.add_argument('name',choices=['relations-offline']);e.add_argument('--json',action='store_true')
    r = sub.add_parser('run',help='Despachar a CLI existente; puede escribir o usar proveedor según capacidad.')
    r.add_argument('capability',choices=ENTRIES);r.add_argument('arguments',nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.action == 'capabilities':
        value = {'schema':'agora/capabilities/v1','coverage':'curated public entrypoints; excludes internal experiments and some specialized modules',
                 'capabilities':[describe(name) for name in ENTRIES],
                 'start_here':'doctor --json; example relations-offline --json; describe <capability> --json',
                 'discovery_network_calls':0, 'admission':'never automatic'}
    elif args.action == 'describe':value = {'schema':'agora/capability-description/v1',**describe(args.capability)}
    elif args.action == 'doctor':value = doctor()
    elif args.action == 'example':value = example()
    elif args.action == 'examples':value = {'schema':'agora/examples/v1','examples':[{'id':'relations-offline','command':[sys.executable,str(ROOT/'scripts/agora.py'),'example','relations-offline','--json'],'network_calls':0,'files_written':0,'purpose':'Resolve evidence IDs and preserve missing version/configuration.'}]}
    else:return 2
    # JSON is also the default, so agents never need to parse prose.
    print(json.dumps(value,ensure_ascii=False,indent=2))
    return 1 if args.action == 'doctor' and value['status'] != 'ok' else 0
