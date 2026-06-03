import kaloricketabulky.sdk as sdk


def test_public_exports() -> None:
    for name in [
        "KaloricketabulkyClient",
        "SnapshotType",
        "Diary",
        "Snapshot",
        "DiarySummary",
        "StatisticsSummary",
        "Tip",
        "MeasurementPoint",
        "KaloricError",
        "ApiError",
        "AuthError",
    ]:
        assert hasattr(sdk, name), name
