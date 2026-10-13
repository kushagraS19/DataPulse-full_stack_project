from datetime import date, datetime

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from app.dashboard_engine.categorical_analyzer import (
    get_primary_categorical_column,
)
from app.dashboard_engine.chart_generator import generate_charts
from app.dashboard_engine.column_analyzer import classify_columns
from app.dashboard_engine.date_analyzer import analyze_date_columns
from app.dashboard_engine.insight_generator import generate_insights
from app.dashboard_engine.kpi_generator import generate_kpis
from app.dashboard_engine.numeric_analyzer import (
    calculate_numeric_correlations,
    calculate_numeric_scores,
    create_numeric_pairs,
    get_primary_numeric_column,
    get_reliable_numeric_columns,
    rank_numeric_columns,
)
from app.services.analytics_services import calculate_kpi
from app.services.dataset_services import (
    detect_text_date_columns,
    get_dataset_column_statistics,
    get_dataset_columns,
)


def make_json_safe(value):
    """Convert NumPy and common Python values to JSON-safe values."""
    if isinstance(value, np.generic):
        return make_json_safe(value.item())

    if isinstance(value, np.ndarray):
        return make_json_safe(value.tolist())

    if isinstance(value, dict):
        return {
            str(key): make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [make_json_safe(item) for item in value]

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    return value


async def generate_dashboard_config(
    db: AsyncSession,
    dataset_id: int,
):
    columns = await get_dataset_columns(db, dataset_id)
    if columns is None:
        return None

    statistics = await get_dataset_column_statistics(db, dataset_id)
    if statistics is None:
        return None

    # 1. Detect native column types.
    column_types = classify_columns(columns, statistics)

    # 2. Detect ISO date values stored in text columns.
    text_date_columns = await detect_text_date_columns(db, dataset_id)

    for column in text_date_columns:
        if column not in column_types["date"]:
            column_types["date"].append(column)
        if column in column_types["categorical"]:
            column_types["categorical"].remove(column)
        if column in column_types["identifier"]:
            column_types["identifier"].remove(column)

    numeric_columns = column_types["numeric"]
    categorical_columns = column_types["categorical"]
    date_columns = column_types["date"]
    identifier_columns = column_types["identifier"]

    # 3. Numeric analysis and correlations.
    numeric_scores = calculate_numeric_scores(numeric_columns, statistics)
    reliable_numeric_columns = get_reliable_numeric_columns(
        numeric_columns,
        statistics,
    )
    primary_numeric_column = get_primary_numeric_column(
        reliable_numeric_columns,
        numeric_scores,
    )
    ranked_numeric_columns = rank_numeric_columns(
        reliable_numeric_columns,
        numeric_scores,
    )
    numeric_pairs = create_numeric_pairs(ranked_numeric_columns)

    correlations = await calculate_numeric_correlations(
        db,
        dataset_id,
        numeric_pairs,
    )
    if correlations is None:
        correlations = []

    # 4. Profile date fields.
    date_profiles = await analyze_date_columns(
        db,
        dataset_id,
        date_columns,
    )

    # 5. Select primary categorical field for existing dashboard metadata.
    categorical_analysis = get_primary_categorical_column(
        categorical_columns,
        statistics,
    )
    primary_categorical_column = categorical_analysis["column"]
    categorical_cardinality = categorical_analysis["cardinality"]

    # 6. Generate KPIs.
    kpi_definitions = generate_kpis(
        ranked_numeric_columns,
        primary_numeric_column,
    )
    kpis = []

    for kpi in kpi_definitions:
        value = await calculate_kpi(
            db,
            dataset_id,
            kpi["operation"],
            kpi["column"],
        )
        kpis.append({**kpi, "value": value})

    # 7. Generate charts using every relevant detected field.
    charts = generate_charts(
        primary_numeric_column=primary_numeric_column,
        primary_categorical_column=primary_categorical_column,
        categorical_cardinality=categorical_cardinality,
        date_profiles=date_profiles,
        correlations=correlations,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        statistics=statistics,
        max_charts=12,
    )

    # 8. Generate data-quality and relationship insights.
    insights = await generate_insights(
        statistics=statistics,
        identifier_columns=identifier_columns,
        correlations=correlations,
        db=db,
        dataset_id=dataset_id,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        max_insights=10,
    )

    date_granularities = [
        {
            "column": profile["column"],
            "granularity": profile.get("granularity"),
        }
        for profile in date_profiles
    ]

    config = {
        "dataset_id": dataset_id,
        "detected_columns": {
            "numeric": numeric_columns,
            "categorical": categorical_columns,
            "date": date_columns,
            "identifier": identifier_columns,
        },
        "numeric_scores": numeric_scores,
        "numeric_pairs": numeric_pairs,
        "correlations": correlations,
        "date_profiles": date_profiles,
        "date_granularities": date_granularities,
        "kpis": kpis,
        "charts": charts,
        "insights": insights,
    }

    print("DETECTED NUMERIC:", numeric_columns)
    print("DETECTED CATEGORICAL:", categorical_columns)
    print("DETECTED DATES:", date_columns)
    print("DETECTED IDENTIFIERS:", identifier_columns)
    print("GENERATED CHART TYPES:", [chart["chart_type"] for chart in charts])

    return make_json_safe(config)
