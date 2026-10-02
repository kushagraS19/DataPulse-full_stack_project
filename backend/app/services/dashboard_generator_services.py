from sqlalchemy.ext.asyncio import AsyncSession

from app.services.dataset_services import (
    get_dataset_columns,
    get_dataset_column_statistics
)

from app.dashboard_engine.column_analyzer import (
    classify_columns
)

from app.dashboard_engine.numeric_analyzer import (
    calculate_numeric_scores,
    get_reliable_numeric_columns,
    get_primary_numeric_column,
    rank_numeric_columns,
    create_numeric_pairs,
    calculate_numeric_correlations
)

from app.dashboard_engine.categorical_analyzer import (
    get_primary_categorical_column
)

from app.dashboard_engine.date_analyzer import (
    analyze_date_columns
)

from app.dashboard_engine.kpi_generator import (
    generate_kpis
)

from app.dashboard_engine.chart_generator import (
    generate_charts
)

from app.dashboard_engine.insight_generator import (
    generate_insights
)


async def generate_dashboard_config(
    db: AsyncSession,
    dataset_id: int
):
    columns = await get_dataset_columns(
        db,
        dataset_id
    )

    if columns is None:
        return None

    statistics = await get_dataset_column_statistics(
        db,
        dataset_id
    )

    if statistics is None:
        return None

    # --------------------------------------------------
    # 1. CLASSIFY COLUMNS
    # --------------------------------------------------

    column_types = classify_columns(
        columns,
        statistics
    )

    numeric_columns = column_types["numeric"]

    categorical_columns = column_types[
        "categorical"
    ]

    date_columns = column_types["date"]

    identifier_columns = column_types[
        "identifier"
    ]

    # --------------------------------------------------
    # 2. NUMERIC ANALYSIS
    # --------------------------------------------------

    numeric_scores = calculate_numeric_scores(
        numeric_columns,
        statistics
    )

    reliable_numeric_columns = (
        get_reliable_numeric_columns(
            numeric_columns,
            statistics
        )
    )

    primary_numeric_column = (
        get_primary_numeric_column(
            reliable_numeric_columns,
            numeric_scores
        )
    )

    ranked_numeric_columns = (
        rank_numeric_columns(
            reliable_numeric_columns,
            numeric_scores
        )
    )

    numeric_pairs = create_numeric_pairs(
        ranked_numeric_columns
    )

    correlations = await calculate_numeric_correlations(
        db,
        dataset_id,
        numeric_pairs
    )

    if correlations is None:
        correlations = []

    # --------------------------------------------------
    # 3. DATE ANALYSIS
    # --------------------------------------------------

    date_profiles = await analyze_date_columns(
        db,
        dataset_id,
        date_columns
    )

    # --------------------------------------------------
    # 4. CATEGORICAL ANALYSIS
    # --------------------------------------------------

    categorical_analysis = (
        get_primary_categorical_column(
            categorical_columns,
            statistics
        )
    )

    primary_categorical_column = (
        categorical_analysis["column"]
    )

    categorical_cardinality = (
        categorical_analysis["cardinality"]
    )

    # --------------------------------------------------
    # 5. KPI GENERATION
    # --------------------------------------------------

    kpis = generate_kpis(
        ranked_numeric_columns,
        primary_numeric_column
    )

    # --------------------------------------------------
    # 6. CHART GENERATION
    # --------------------------------------------------


    print("PRIMARY NUMERIC:", primary_numeric_column)
    print("PRIMARY CATEGORICAL:", primary_categorical_column)
    charts = generate_charts(
        primary_numeric_column=(
            primary_numeric_column
        ),
        primary_categorical_column=(
            primary_categorical_column
        ),
        categorical_cardinality=(
            categorical_cardinality
        ),
        date_profiles=date_profiles,
        correlations=correlations
    )

    # --------------------------------------------------
    # 7. INSIGHT GENERATION
    # --------------------------------------------------

    insights = generate_insights(
        statistics=statistics,
        identifier_columns=identifier_columns,
        correlations=correlations
    )

    # --------------------------------------------------
    # 8. DATE GRANULARITIES
    # --------------------------------------------------

    date_granularities = [
        {
            "column": profile["column"],
            "granularity": profile.get(
                "granularity"
            )
        }
        for profile in date_profiles
    ]

    # --------------------------------------------------
    # 9. FINAL DASHBOARD CONFIGURATION
    # --------------------------------------------------

    return {
        "dataset_id": dataset_id,

        "detected_columns": {
            "numeric": numeric_columns,
            "categorical": categorical_columns,
            "date": date_columns,
            "identifier": identifier_columns
        },

        "numeric_scores": numeric_scores,

        "numeric_pairs": numeric_pairs,

        "correlations": correlations,

        "date_profiles": date_profiles,

        "date_granularities": date_granularities,

        "kpis": kpis,

        "charts": charts,

        "insights": insights
    }