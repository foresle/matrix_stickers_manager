import pytest
import uuid

from matrix_stickers_manager import MatrixStickersManager


@pytest.fixture
def manager() -> MatrixStickersManager:
    return MatrixStickersManager(path_to_config='../config.yaml')


def test_upload_media(manager):
    manager._upload_media('cat.jpg')


def test_get_room_state(manager):
    event: dict = manager._get_room_state(pack_name='кітики',
                                          room_id='!DFbnbNTzbZVVjjnRUz:matrix.opulus.space')  # Pls replace to your room


def test_make_pack(manager):
    # New pack
    pack = manager._make_pack_obj(name='test_pack_1')

    # Existed pack
    pack = manager._make_pack_obj(name='test_pack_1', room_id='!DFbnbNTzbZVVjjnRUz:matrix.opulus.space')


def test_push_pack(manager):
    pack = manager._make_pack_obj(name='test_pack_1', room_id='!DFbnbNTzbZVVjjnRUz:matrix.opulus.space')
    manager._push_pack('test_pack_1', room_id='!DFbnbNTzbZVVjjnRUz:matrix.opulus.space', pack=pack)


def test_load_stickers_from_folder(manager):
    manager.load_pack_from_folder(
        pack_name=uuid.uuid4().hex,
        folder_path='../stickers/',
        room_id='!DFbnbNTzbZVVjjnRUz:matrix.opulus.space'
    )
