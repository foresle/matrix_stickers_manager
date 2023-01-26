from dataclasses import dataclass
import requests
from dataclass_wizard import YAMLWizard
import os
import filetype


@dataclass()
class Config(YAMLWizard):
    matrix_token: str
    matrix_domain: str
    max_media_upload_size: int = 1


class MatrixStickersManagerError(Exception):
    text: str

    def __init__(self, text: str = 'Unknown'):
        self.text = text

    def __str__(self):
        return self.text


class MatrixStickersManager:
    _config: Config

    def __init__(self, path_to_config: str = 'config.yaml'):
        self._config = Config.from_yaml_file(file=path_to_config)
        self._config.max_media_upload_size = self._check_max_media_upload_size()

    def _check_max_media_upload_size(self) -> int:
        response = requests.get(f'https://{self._config.matrix_domain}/_matrix/media/v3/config'
                                f'?access_token={self._config.matrix_token}')
        assert response.status_code == 200
        return response.json()['m.upload.size']

    """
    This code can simplify manage with your native stickers packs.
    Stickers specs: https://github.com/Sorunome/matrix-doc/blob/soru/emotes/proposals/2545-emotes.md
    """

    def _upload_media(self, file_path: str) -> str:
        """
        Just upload file to matrix storage and return mxc url
        https://matrix.org/docs/api/#post-/_matrix/media/v3/upload
        """

        if not os.path.exists(file_path):
            raise MatrixStickersManagerError(text=f'File {file_path} doest exist.')

        filename = os.path.basename(file_path)
        filemime = filetype.guess(file_path).mime

        with open(file_path, 'rb') as file:
            response = requests.post(f'https://{self._config.matrix_domain}/_matrix/media/v3/upload'
                                     f'?filename={filename}'
                                     f'&access_token={self._config.matrix_token}',
                                     headers={
                                         'Content-Type': filemime
                                     }, data=file)

            if response.status_code != 200:
                raise MatrixStickersManagerError(text=response.text)
            else:
                return response.json()['content_uri']

    def _get_room_state(self, pack_name: str, room_id: str) -> dict:
        """
        Get im.ponies.room_emotes state for pack_name
        https://matrix.org/docs/api/#get-/_matrix/client/v3/rooms/-roomId-/state/-eventType-/-stateKey-
        """

        response = requests.get(f'https://{self._config.matrix_domain}/_matrix/client/v3/rooms/{room_id}'
                                # https://github.com/Sorunome/matrix-doc/blob/soru/emotes/proposals/2545-emotes.md#unstable-prefix
                                f'/state/im.ponies.room_emotes/{pack_name}'
                                f'?access_token={self._config.matrix_token}')

        if response.status_code != 200:
            raise MatrixStickersManagerError(text=response.text)
        else:
            return response.json()

    def _make_pack_obj(self, name: str, room_id: str | None = None) -> dict:
        """
        If room_id specified try to get state and return dict.
        If state doest exist create return new dict.
        """

        if room_id is not None:
            try:
                pack = self._get_room_state(pack_name=name, room_id=room_id)
                assert pack.get('pack', default=False)
                assert pack['pack'].get('display_name', default=False)
                assert pack.get('images', default=False)
                return pack
            except MatrixStickersManagerError:
                pass

        pack: dict = {
            'pack': {'display_name': name},
            'images': {}
        }

        return pack

    def _push_pack(self, name: str, room_id: str, pack: dict) -> None:
        """
        Update pack with his name.
        """

        response = requests.put(f'https://{self._config.matrix_domain}/_matrix/client/v3/rooms/{room_id}'
                                f'/state/im.ponies.room_emotes/{name}'
                                f'?access_token={self._config.matrix_token}', json=pack)

        if response.status_code != 200:
            raise MatrixStickersManagerError(text=response.text)

    @staticmethod
    def _add_sticker_to_pack(pack: dict, shortcode: str, image_mxc: str, usage: str | None = None):
        """
        Add sticker to pack.
        https://github.com/Sorunome/matrix-doc/blob/soru/emotes/proposals/2545-emotes.md#example-image-pack-event
        Usage can be "sticker" or "emoticon" else both.

        If shortcode already exist raise error.
        """

        if pack['images'].get(shortcode, False):
            raise MatrixStickersManagerError(f'This shortcode "{shortcode}" already exist.')

        if usage is not None:
            pack['images'][shortcode] = {
                'url': image_mxc,
                'usage': (usage,)
            }
        else:
            pack['images'][shortcode] = {
                'url': image_mxc
            }

    def load_pack_from_folder(self, pack_name: str, folder_path: str, room_id: str,
                              number_as_shortcode: bool = False, skip_duplicates: bool = False) -> None:
        """
        Load all images from folder to pack.
        """

        image_pack: dict = self._make_pack_obj(name=pack_name, room_id=room_id)
        all_files: list = []

        for file_path in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, file_path)):
                all_files.append(file_path)

        count: int = 1
        for file_path in all_files:
            # Upload image
            image_url: str = self._upload_media(os.path.join(folder_path, file_path))

            try:
                self._add_sticker_to_pack(pack=image_pack,
                                          shortcode=count if number_as_shortcode else os.path.splitext(file_path)[0],
                                          image_mxc=image_url)
            except MatrixStickersManagerError as e:
                if skip_duplicates:
                    pass
                else:
                    raise e

            self._push_pack(name=pack_name, room_id=room_id, pack=image_pack)

            count += 1
