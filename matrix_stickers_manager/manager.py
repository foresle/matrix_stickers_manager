from dataclasses import dataclass
import requests
from dataclass_wizard import YAMLWizard


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
    I cant found API for stickers/emotes, but Cinny use something and Synapse server support his.
    I think can solve my problem with use API from Cinny code.
    
    Some useful links:
    https://github.com/cinnyapp/cinny/pull/209
    https://github.com/matrix-org/matrix-spec-proposals/pull/2545
    https://github.com/cinnyapp/cinny/tree/dev/src/app/molecules/image-pack
    
    Then I found next link in Cinny code:
    https://github.com/Sorunome/matrix-doc/blob/soru/emotes/proposals/2545-emotes.md
    """

    @staticmethod
    def __need_room_admin_permissions(func):
        """Check admin permission for room"""

        def wrapper(self, room_id: str = 'test', **kwargs):
            # # https://spec.matrix.org/v1.5/client-server-api/#get_matrixclientv3accountwhoami
            # response = requests.get(f'https://{self._config.matrix_domain}/_matrix/client/v3/account/whoami'
            #                         f'?access_token={self._config.matrix_token}')
            # if response.status_code != 200:
            #     raise MatrixStickersManagerError(text=response.text)
            #
            # user_id: str = response.json()['user_id']
            #
            # response = requests.get(f'/_matrix/client/v3/user/{user_id}/rooms/{room_id}/account_data/{type}'
            #                         f'?access_token={self._config.matrix_token}')

            return func(self, roon_id=room_id, **kwargs)

        return wrapper
