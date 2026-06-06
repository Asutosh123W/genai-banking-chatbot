from database.models import (
    EvaluationMetric
)


def save_evaluation_metric(
    session_id,
    answer_relevancy,
    faithfulness,
    context_precision,
    db
):

    metric = EvaluationMetric(

        session_id=session_id,

        answer_relevancy=str(
            answer_relevancy
        ),

        faithfulness=str(
            faithfulness
        ),

        context_precision=str(
            context_precision
        )
    )

    db.add(metric)

    db.commit()

    return metric