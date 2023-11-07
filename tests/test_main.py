import contextlib
import unittest
import uuid

import pytest
from environs import Env
from matrix_stickers_manager import (MatrixStickersManager,
                                     MatrixStickersManagerError)


class TestStringMethods(unittest.TestCase):
    manager: MatrixStickersManager
    env_vars: Env
    test_created_pack: str

    def setUp(self) -> None:
        # Load env variables
        env = Env()
        env.read_env("test.env")
        self.env_vars = env

        # Create manager
        self.manager = MatrixStickersManager(path_to_config="../config.yaml")
        self.test_created_pack = uuid.uuid4().hex

    def test_check_max_media_upload_size(self):
        with contextlib.suppress(AssertionError):
            self.manager._check_max_media_upload_size()

    def test_upload_media(self):
        # Image
        self.manager._upload_media("cat.jpg")

        # Not image
        with contextlib.suppress(MatrixStickersManagerError):
            self.manager._upload_media("not_cat.txt")
            raise Exception

    def test_get_room_state(self):
        exists_event = self.manager._get_room_state(
            pack_name=self.env_vars("TEST_EXISTS_PACK"),
            room_id=self.env_vars("TEST_ROOM_ID"),
        )

        with contextlib.suppress(MatrixStickersManagerError):
            missing_event = self.manager._get_room_state(
                pack_name=uuid.uuid4().hex, room_id=self.env_vars("TEST_ROOM_ID")
            )
            raise Exception

    def test_make_pack_obj(self):
        # Exists pack
        pack = self.manager._make_pack_obj(
            name=self.env_vars("TEST_EXISTS_PACK"),
            room_id=self.env_vars("TEST_ROOM_ID"),
            new_if_missing=False,
        )

        # New pack
        pack = self.manager._make_pack_obj(name=uuid.uuid4().hex)

        # Missing packs
        pack = self.manager._make_pack_obj(
            name=uuid.uuid4().hex,
            room_id=self.env_vars("TEST_ROOM_ID"),
            new_if_missing=True,
        )

        with contextlib.suppress(MatrixStickersManagerError, AssertionError):
            pack = self.manager._make_pack_obj(
                name=uuid.uuid4().hex,
                room_id=self.env_vars("TEST_ROOM_ID"),
                new_if_missing=False,
            )
            raise Exception

    def test_push_pack(self):
        self.manager._push_pack(
            name=self.test_created_pack,
            room_id=self.env_vars("TEST_ROOM_ID"),
            pack=self.manager._make_pack_obj(name=self.test_created_pack),
        )

    def test_add_sticker_to_pack(self):
        pack = self.manager._make_pack_obj(name=self.test_created_pack)
        sticker_name = uuid.uuid4().hex
        self.manager._add_sticker_to_pack(
            pack=pack,
            shortcode=sticker_name,
            image_mxc="mxc://matrix.test.server/maeNguayielahseeci",
            usage="sticker",
        )
        self.assertIn(sticker_name, pack["images"])

    def test_load_stickers_from_folder(self):
        self.manager.load_pack_from_folder(
            pack_name=self.test_created_pack,
            folder_path="../stickers/",
            room_id=self.env_vars("TEST_ROOM_ID"),
        )

    def test_delete_pack(self):
        self.manager.delete_pack(
            pack_name=self.test_created_pack, room_id=self.env_vars("TEST_ROOM_ID")
        )

    def test_is_server_admin(self):
        self.manager._is_server_admin()

    def test_assemble_mxc_url(self):
        assert (
            "test.matrix.server",
            "tyBrcoBDixOSbEYwswVSwZer",
        ) == self.manager._assemble_mxc_url(
            "mxc://test.matrix.server/tyBrcoBDixOSbEYwswVSwZer"
        )

    def test_export_pack(self):
        self.manager.export_pack(
            pack_name=self.env_vars("TEST_EXISTS_PACK"),
            room_id=self.env_vars("TEST_ROOM_ID"),
            export_folder="stickers_test/",
            original_name=True,
        )
        self.manager.export_pack(
            pack_name=self.env_vars("TEST_EXISTS_PACK"),
            room_id=self.env_vars("TEST_ROOM_ID"),
            export_folder="stickers_test/",
            original_name=False,
        )
