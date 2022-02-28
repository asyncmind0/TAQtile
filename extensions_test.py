from extensions import list_executables


def test_list_executables():
    results = list_executables()
    assert len(results) > 10
    assert isinstance(results, list), results
