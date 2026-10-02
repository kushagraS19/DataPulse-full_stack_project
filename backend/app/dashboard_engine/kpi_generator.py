def generate_kpis(
    ranked_numeric_columns: list[str],
    primary_numeric_column: str | None
):
    kpis = [
        {
            "name": "Total Records",
            "operation": "count",
            "column": None
        }
    ]

    for column in ranked_numeric_columns[:2]:

        kpis.append({
            "name": f"Average {column}",
            "operation": "average",
            "column": column
        })

        kpis.append({
            "name": f"Maximum {column}",
            "operation": "max",
            "column": column
        })

        if column == primary_numeric_column:

            kpis.append({
                "name": f"Minimum {column}",
                "operation": "min",
                "column": column
            })

    return kpis