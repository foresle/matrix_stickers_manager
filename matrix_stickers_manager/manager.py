import urllib
from dataclasses import dataclass
import requests
from dataclass_wizard import YAMLWizard
import os
import filetype
import cgi


@dataclass()
class Config(YAMLWizard):
    matrix_token: str
    matrix_domain: str
    max_media_upload_size: int = 1
    is_server_admin: bool = False


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
        self._config.is_server_admin = self._is_server_admin()

    def _check_max_media_upload_size(self) -> int:
        response = requests.get(f'https://{self._config.matrix_domain}/_matrix/media/v3/config'
                                f'?access_token={self._config.matrix_token}')
        assert response.status_code == 200
        return response.json()['m.upload.size']

    """
    This code can simplify manage with your native stickers packs.
    Stickers specs: https://github.com/Sorunome/matrix-doc/blob/soru/emotes/proposals/2545-emotes.md
    """

    def _upload_media(self, file_path: str, image_type_only: bool = True) -> str:
        """
        Just upload media file to matrix storage and return mxc url.
        https://matrix.org/docs/api/#post-/_matrix/media/v3/upload
        """

        if not os.path.exists(file_path):
            raise MatrixStickersManagerError(text=f'File {file_path} doest exist.')

        if os.path.getsize(file_path) > self._config.max_media_upload_size:
            raise MatrixStickersManagerError(text=f'File is so large. '
                                                  f'Max upload size is {self._config.max_media_upload_size}bytes.')

        filename = os.path.basename(file_path)
        filemime = filetype.guess(file_path)

        if filemime is not None:
            filemime = filemime.mime
        else:
            raise MatrixStickersManagerError(text='Unknown file type.')

        if image_type_only:
            if filemime not in ('image/png', 'image/jpeg', 'image/gif', 'image/webp'):
                raise MatrixStickersManagerError(text='Invalid media file format.')

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
        Get im.ponies.room_emotes state for pack_name.
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

    def _make_pack_obj(self, name: str, room_id: str | None = None, new_if_missing: bool = True) -> dict:
        """
        If room_id specified try to get state and return dict.
        If state doest exist create new dict.
        """

        if room_id is not None:
            try:
                pack = self._get_room_state(pack_name=name, room_id=room_id)
                assert 'pack' in pack
                assert 'display_name' in pack['pack']
                assert 'images' in pack
                return pack
            except (MatrixStickersManagerError, AssertionError) as e:
                if new_if_missing:
                    pass
                else:
                    raise e

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

    def delete_pack(self, pack_name: str, room_id: str) -> None:
        """
        Delete pack if it already exists.
        """

        try:
            pack = self._get_room_state(pack_name=pack_name, room_id=room_id)
        except MatrixStickersManagerError:
            return None

        # Unprotect all media
        if self._config.is_server_admin:
            for image in pack['images'].values():
                try:
                    self._unprotect_media(image['url'])
                except MatrixStickersManagerError:
                    pass

        response = requests.put(f'https://{self._config.matrix_domain}/_matrix/client/v3/rooms/{room_id}'
                                f'/state/im.ponies.room_emotes/{pack_name}'
                                f'?access_token={self._config.matrix_token}', json={})

        if response.status_code != 200:
            raise MatrixStickersManagerError(text=response.text)

    def load_pack_from_folder(self, pack_name: str, folder_path: str, room_id: str, usage: str | None = None,
                              number_as_shortcode: bool = False, skip_duplicate_errors: bool = False,
                              skip_upload_errors: bool = False, protect_media: bool = True) -> None:
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
            try:
                image_url: str = self._upload_media(os.path.join(folder_path, file_path))
                if self._config.is_server_admin and protect_media:
                    self._protect_media(image_url)

            except MatrixStickersManagerError as e:
                if skip_upload_errors:
                    continue
                else:
                    raise e

            try:
                self._add_sticker_to_pack(pack=image_pack,
                                          shortcode=count if number_as_shortcode else os.path.splitext(file_path)[0],
                                          image_mxc=image_url, usage=usage)
            except MatrixStickersManagerError as e:
                if skip_duplicate_errors:
                    continue
                else:
                    raise e

            self._push_pack(name=pack_name, room_id=room_id, pack=image_pack)

            count += 1

    def _is_server_admin(self, user_id: str | None = None) -> bool:
        """
        Check is user be admin in server.
        If user_id not specify check by token.
        """

        if user_id is None:
            response = requests.get(f'https://{self._config.matrix_domain}/_matrix/client/v3/account/whoami'
                                    f'?access_token={self._config.matrix_token}')

            if response.status_code != 200:
                raise MatrixStickersManagerError(text=response.text)

            user_id = response.json()['user_id']

        response = requests.get(f'https://{self._config.matrix_domain}/_synapse/admin/v1/users/{user_id}/admin',
                                headers={'Authorization': f'Bearer {self._config.matrix_token}'})

        if response.status_code == 403:
            return False
        elif response.status_code != 200:
            raise MatrixStickersManagerError(text=response.text)

        return response.json()['admin']

    @staticmethod
    def _assemble_mxc_url(mxc_url: str) -> (str, str):
        """
        Return parsed mxc url:
        mxc://<server-name>/<media-id> -> (server_name, media_id)

        https://spec.matrix.org/v1.5/client-server-api/#matrix-content-mxc-uris
        """

        return tuple(mxc_url[6:].split('/'))

    def _protect_media(self, mxc_url: str) -> None:
        """
        Protect media from deleting.
        """

        mxc_url: tuple = self._assemble_mxc_url(mxc_url)
        response = requests.post(f'https://{self._config.matrix_domain}'
                                 f'/_synapse/admin/v1/media/protect/{mxc_url[1]}',
                                 headers={'Authorization': f'Bearer {self._config.matrix_token}'})

        if response.status_code != 200:
            raise MatrixStickersManagerError(text=response.text)

    def _unprotect_media(self, mxc_url: str) -> None:
        """
        Unprotect media.
        """

        mxc_url: tuple = self._assemble_mxc_url(mxc_url)
        response = requests.post(f'https://{self._config.matrix_domain}'
                                 f'/_synapse/admin/v1/media/unprotect/{mxc_url[1]}',
                                 headers={'Authorization': f'Bearer {self._config.matrix_token}'})

        if response.status_code != 200:
            raise MatrixStickersManagerError(text=response.text)

    def export_pack(self, pack_name: str, room_id: str,
                    export_folder: str = 'stickers/', original_name: bool = True) -> None:
        """
        Download all images from pack to folder.
        Set original file name or number.
        """

        pack = self._make_pack_obj(name=pack_name, room_id=room_id, new_if_missing=False)

        os.makedirs(export_folder, exist_ok=True)
        if export_folder[-1:] != '/':
            export_folder = f'{export_folder}/'

        count: int = 1
        for image in pack['images'].values():
            image_url = self._assemble_mxc_url(image['url'])
            response = requests.get(f'https://{self._config.matrix_domain}/_matrix/media/v3/download'
                                    f'/{image_url[0]}/{image_url[1]}'
                                    f'?access_token={self._config.matrix_token}')

            if response.status_code != 200:
                raise MatrixStickersManagerError(text=response.text)

            if original_name:
                value, params = cgi.parse_header(response.headers["Content-Disposition"])

                # Check cyrillic
                if params.get('filename', None) is None:
                    file_name = urllib.parse.unquote(params['filename*'])
                    file_name = file_name.split('\'')[2]
                else:
                    file_name = params['filename']
            else:
                file_name = f'{count}.{response.headers["Content-Type"].split("/")[1]}'

            with open(f'{export_folder}{file_name}', 'wb') as file:
                file.write(response.content)

            count += 1
