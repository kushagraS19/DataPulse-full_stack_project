import pandas as pd
import pytest

from app.services import data_processing_services as csv_service
from app.services.data_processing_services import process_csv


def write_csv(tmp_path, content, filename="sample.csv"):
    file_path = tmp_path / filename
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)


def test_process_valid_csv(tmp_path):
    path = write_csv(
        tmp_path,
        "Name,Age\nAlice,20\nBob,30\n",
    )

    df = process_csv(path)

    assert len(df) == 2
    assert list(df.columns) == ["name", "age"]
    assert df["name"].tolist() == ["Alice", "Bob"]
    assert df["age"].tolist() == [20, 30]


def test_reject_empty_file(tmp_path):
    path = write_csv(tmp_path, "")

    with pytest.raises(ValueError, match="no data"):
        process_csv(path)


def test_reject_csv_without_data_rows(tmp_path):
    path = write_csv(tmp_path, "name,age\n")

    with pytest.raises(ValueError, match="no data rows"):
        process_csv(path)


def test_reject_malformed_csv(tmp_path):
    path = write_csv(
        tmp_path,
        "name,age\nAlice,20\nBob,30,unexpected\n",
    )

    with pytest.raises(ValueError, match="Invalid CSV format"):
        process_csv(path)


def test_normalizes_duplicate_column_names(tmp_path):
    path = write_csv(
        tmp_path,
        "User Name,user-name\nAlice,Admin\nBob,User\n",
    )

    df = process_csv(path)

    assert df.columns.is_unique
    assert list(df.columns) == ["user_name", "user_name_2"]


def test_removes_duplicate_rows(tmp_path):
    path = write_csv(
        tmp_path,
        "name,age\nAlice,20\nAlice,20\nBob,30\n",
    )

    df = process_csv(path)

    assert len(df) == 2


def test_fills_missing_numeric_values_with_median(tmp_path):
    path = write_csv(
        tmp_path,
        "age,name\n10,Alice\n,Bob\n30,Charlie\n",
    )

    df = process_csv(path)

    assert df["age"].tolist() == [10, 20, 30]


def test_fills_missing_text_values(tmp_path):
    path = write_csv(
        tmp_path,
        "name,city\nAlice,Indore\nBob,\n",
    )

    df = process_csv(path)

    assert df["city"].tolist() == ["Indore", "Unknown"]


def test_rejects_too_many_rows(tmp_path, monkeypatch):
    monkeypatch.setattr(csv_service, "MAX_ROWS", 2)

    path = write_csv(
        tmp_path,
        "value\n1\n2\n3\n",
    )

    with pytest.raises(ValueError, match="maximum of 2"):
        process_csv(path)


def test_rejects_too_many_columns(tmp_path, monkeypatch):
    monkeypatch.setattr(csv_service, "MAX_COLUMNS", 2)

    path = write_csv(
        tmp_path,
        "a,b,c\n1,2,3\n",
    )

    with pytest.raises(ValueError, match="more than 2 columns"):
        process_csv(path)


def test_strips_whitespace_from_text(tmp_path):
    path = write_csv(
        tmp_path,
        "name\n  Alice  \n  Bob  \n",
    )

    df = process_csv(path)

    assert df["name"].tolist() == ["Alice", "Bob"]


def test_drops_completely_empty_rows(tmp_path):
    path = write_csv(
        tmp_path,
        "name,age\nAlice,20\n,\nBob,30\n",
    )

    df = process_csv(path)

    assert len(df) == 2