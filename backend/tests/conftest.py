def pytest_addoption(parser):
    parser.addoption(
        "--run-mysql-integration",
        action="store_true",
        default=False,
        help="run tests that prompt for the isolated MySQL test account password",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "mysql_integration: uses the isolated local quanlykho_test MySQL schema",
    )
