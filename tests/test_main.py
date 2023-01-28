import pytest
import uuid
from environs import Env

from matrix_stickers_manager import MatrixStickersManager, MatrixStickersManagerError


@pytest.fixture
def manager() -> MatrixStickersManager:
    return MatrixStickersManager(path_to_config='../config.yaml')


@pytest.fixture
def env_variables() -> Env:
    env = Env()
    env.read_env('test.env')
    return env


def test_upload_media(manager: MatrixStickersManager):
    # Image
    manager._upload_media('cat.jpg')

    # Not image
    try:
        manager._upload_media('not_cat.txt')
        raise Exception
    except MatrixStickersManagerError:
        pass


def test_get_room_state(manager: MatrixStickersManager, env_variables: Env):
    event: dict = manager._get_room_state(pack_name=env_variables('TEST_EXISTS_PACK'),
                                          room_id=env_variables('TEST_ROOM_ID'))


def test_make_pack(manager: MatrixStickersManager, env_variables: Env):
    # New pack
    pack = manager._make_pack_obj(name=uuid.uuid4().hex)
    # Existed pack
    pack = manager._make_pack_obj(name=env_variables('TEST_EXISTS_PACK'), room_id=env_variables('TEST_ROOM_ID'))


def test_push_pack(manager: MatrixStickersManager, env_variables: Env):
    pack = manager._make_pack_obj(name=env_variables('TEST_EXISTS_PACK'), room_id=env_variables('TEST_ROOM_ID'))
    manager._push_pack(env_variables('TEST_EXISTS_PACK'), room_id=env_variables('TEST_ROOM_ID'), pack=pack)


def test_load_stickers_from_folder(manager: MatrixStickersManager, env_variables: Env):
    pack_name: str = uuid.uuid4().hex

    manager.load_pack_from_folder(
        pack_name=pack_name,
        folder_path='../stickers/',
        room_id=env_variables('TEST_ROOM_ID')
    )
    manager.delete_pack(pack_name=pack_name, room_id=env_variables('TEST_ROOM_ID'))


def test_is_server_admin(manager: MatrixStickersManager):
    manager._is_server_admin()


def test_assemble_mxc_url(manager: MatrixStickersManager):
    assert ('test.matrix.server', 'tyBrcoBDixOSbEYwswVSwZer') == manager._assemble_mxc_url(
        'mxc://test.matrix.server/tyBrcoBDixOSbEYwswVSwZer')
