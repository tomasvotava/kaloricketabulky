from kaloricketabulky.sdk.models.snapshot import Snapshot, SnapshotType


def test_snapshot_type_values() -> None:
    assert SnapshotType.ENERGY.value == "energy"
    assert {t.value for t in SnapshotType} == {
        "energy",
        "nutrients",
        "drink",
        "weight",
        "optional",
    }


def test_weight_snapshot_parses_values_and_target() -> None:
    snap = Snapshot.model_validate(
        {
            "type": "weight",
            "unit": "kcal",
            "from": None,
            "to": None,
            "min": 85.25,
            "max": 85.25,
            "values": [{"guid": "v1", "from": 1780351200000, "value": 85.25, "valueString": "85,2"}],
            "target": [{"guid": "t1", "from": 1780351200000, "value": None}],
            "tableData": [
                {
                    "value": {"guid": "v1", "value": 85.25},
                    "target": {"guid": "t1", "value": None},
                }
            ],
            # UI fields that must be dropped:
            "graph": [],
            "limit": 25,
            "page": 1,
            "valuesPaged": [],
        }
    )
    assert snap.type == "weight"
    assert snap.min == 85.25
    assert snap.values[0].value == 85.25
    assert snap.values[0].valid_from is not None
    assert snap.target[0].value is None
    assert snap.table_data[0].value is not None
    assert snap.table_data[0].value.value == 85.25
    assert not hasattr(snap, "graph")


def test_optional_snapshot_null_target_becomes_empty() -> None:
    snap = Snapshot.model_validate(
        {
            "type": "Obvod paže [cm]",
            "unit": None,
            "graph": True,  # bool here, array elsewhere — dropped either way
            "target": None,
            "values": [{"guid": "x", "from": 1756332000000, "value": 35.0, "valueString": "35"}],
            "tableData": [],
            "nutrientsValues": [],
        }
    )
    assert snap.type == "Obvod paže [cm]"
    assert snap.target == []
    assert snap.values[0].value == 35.0


def test_nutrients_snapshot_parses_macro_triplets() -> None:
    snap = Snapshot.model_validate(
        {
            "type": "nutrients",
            "unit": "kcal",
            "values": [],
            "target": [],
            "tableData": [],
            "nutrientsValues": [
                {
                    "createdDate": 1779832800000,
                    "fat": {"value": 109.268, "status": 1},
                    "protein": {"value": 121.65, "status": 2},
                    "carbs": {"value": 324.2, "status": 0},
                }
            ],
            "nutrientsTableData": [
                {
                    "fatTarget": {"value": 71.6},
                    "proteinTarget": {"value": 146.7},
                    "carbsTarget": {"value": 275.9},
                    "fatValue": {"value": 7.3},
                    "proteinValue": {"value": 30.4},
                    "carbsValue": {"value": 87.2},
                }
            ],
            "nutrientsTarget": [],
        }
    )
    assert snap.nutrients_values[0].fat is not None
    assert snap.nutrients_values[0].fat.value == 109.268
    assert snap.nutrients_values[0].created_date is not None
    assert snap.nutrients_table_data[0].protein_value is not None
    assert snap.nutrients_table_data[0].protein_value.value == 30.4
