import pandas as pd

from app.services.data_profiling_services import profile_dataset


df = pd.DataFrame(
    {
        "name": ["Alice", "Bob", "Charlie", "Alice", "Eve"],
        "age": [20, 25, 30, 20, 100],
        "score": [80, 90, 85, 80, 95],
        "city": ["Indore", "Delhi", "Indore", "Indore", "Mumbai"],
    }
)


profile = profile_dataset(df)

print("\nDATASET SUMMARY")
print(profile["summary"])

print("\nCOLUMN PROFILES")

for column in profile["columns"]:
    print("\n----------------------------")
    print(f"Column: {column['column']}")
    print(f"Type: {column['data_type']}")
    print(f"Missing: {column['missing_percentage']}%")
    print(f"Unique: {column['unique_count']}")
    print(f"Constant: {column['is_constant']}")
    print(f"High Cardinality: {column['is_high_cardinality']}")

    if "statistics" in column:
        print("Statistics:")
        print(column["statistics"])

    if "date_profile" in column:
        print("Date Profile:")
        print(column["date_profile"])