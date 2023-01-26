import pytest

from matrix_stickers_manager import MatrixStickersManager


@pytest.fixture
def manager() -> MatrixStickersManager:
    return MatrixStickersManager(path_to_config='../config.yaml')


def test_upload_media(manager):
    manager._upload_media('cat.jpg')
