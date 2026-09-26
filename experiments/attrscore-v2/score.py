"""Classification metrics with explicit missing/failed outputs in denominators."""
LABELS=('supported','contradicted','insufficient')


def classification_scores(gold,predictions):
    unknown=set(predictions)-set(gold)
    if unknown:raise ValueError('unknown_prediction_ids')
    if any(x not in LABELS for x in gold.values()):raise ValueError('unknown_gold_label')
    columns=LABELS+('failed','not_run')
    if any(x not in columns for x in predictions.values()):raise ValueError('unknown_prediction_label')
    matrix={x:{y:0 for y in columns} for x in LABELS}
    for cid,true in gold.items():matrix[true][predictions.get(cid,'not_run')]+=1
    by_class={}
    for label in LABELS:
        tp=matrix[label][label];fp=sum(matrix[x][label] for x in LABELS if x!=label)
        fn=sum(matrix[label][x] for x in columns if x!=label)
        precision=tp/(tp+fp) if tp+fp else 0;recall=tp/(tp+fn) if tp+fn else 0
        by_class[label]={'precision':precision,'recall':recall,'f1':2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0,'support':sum(matrix[label].values())}
    n=len(gold);valid=sum(matrix[x][y] for x in LABELS for y in LABELS)
    correct=sum(matrix[x][x] for x in LABELS)
    supported=sum(matrix['supported'].values());unsupported=n-supported
    return {'cases':n,'valid_predictions':valid,'failed':sum(matrix[x]['failed'] for x in LABELS),
            'not_run':sum(matrix[x]['not_run'] for x in LABELS),'correct':correct,
            'accuracy_all_cases':correct/n if n else None,'coverage':valid/n if n else None,
            'macro_f1':sum(v['f1'] for v in by_class.values())/3,
            'unsupported_accepted':{'count':matrix['contradicted']['supported']+matrix['insufficient']['supported'],'denominator':unsupported},
            'supported_rejected':{'count':matrix['supported']['contradicted']+matrix['supported']['insufficient'],'denominator':supported},
            'supported_failed_or_not_run':matrix['supported']['failed']+matrix['supported']['not_run'],
            'confusion':matrix,'by_class':by_class}
