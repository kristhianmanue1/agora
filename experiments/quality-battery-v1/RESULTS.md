# Resultados de la batería de calidad v1

Fecha de observación: 2026-10-19. Ejecución offline:
cero llamadas a proveedores vivos; juicios simulados.

| Escenario | Comprobación | Esperado | Observado | Resultado |
|---|---|---|---|---|
| S2 absent_mandatory_declared_not_invented | flow_status | 'candidate_reviewed' | 'candidate_reviewed' | pass |
|  | no_invented_claims | 0 | 0 | pass |
|  | missing_visible | True | True | pass |
|  | part_status | 'not_in_passages' | 'not_in_passages' | pass |
|  | claim_review_not_run | ('not_run', 'no_claims') | ('not_run', 'no_claims') | pass |
|  | memory_admission | 'not_performed' | 'not_performed' | pass |
| S5 reference_validity_is_not_semantic_backing | references_resolve | True | True | pass |
|  | support_axis | 'insufficient' | 'insufficient' | pass |
|  | review_flags_revision | 'needs_revision' | 'needs_revision' | pass |
|  | adjudication_not_performed | 'not_performed' | 'not_performed' | pass |
|  | disposition | 'requires_review' | 'requires_review' | pass |
|  | completeness_not_established | 'not_established' | 'not_established' | pass |
| S6 altered_source_rejected_before_dispatch | flow_status | 'rejected' | 'rejected' | pass |
|  | diagnostic | 'SourceError' | 'SourceError' | pass |
|  | zero_dispatches | 0 | 0 | pass |
|  | zero_provider_calls | 0 | 0 | pass |
| S7 partial_derivative_gap_not_citable | coverage_declared_partial | 'partial' | 'partial' | pass |
|  | gap_citation_rejected | 'evidence_outside_segment' | 'evidence_outside_segment' | pass |
|  | literal_is_source_bytes | 'Alpha' | 'Alpha' | pass |
|  | semantic_support | 'not_verified' | 'not_verified' | pass |
|  | not_admitted | False | False | pass |
|  | original_integrity | 'sha256_verified' | 'sha256_verified' | pass |
| S8 uncertain_remote_durable_no_retry | flow_status | 'remote_outcome_unknown' | 'remote_outcome_unknown' | pass |
|  | calls_without_retry | ['generation', 'support'] | ['generation', 'support'] | pass |
|  | dispatches_count | 2 | 2 | pass |
|  | attempt_receipts | 2 | 2 | pass |
|  | no_support_response | False | False | pass |

Escenarios fallidos: 0.

Límites: los juicios del proveedor son simulados; esta batería
verifica separación de ejes, procedencia y estados, no calidad
semántica. S1/S3/S4 requieren la fase con modelos y sus puertas.
