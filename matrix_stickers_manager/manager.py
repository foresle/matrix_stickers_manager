import requests


def need_room_moderator_access_level(func):
    """
    This decorator checks user access for room stickers object.
    """

    def wrapper(self):
        if self._room_access_level is None:
            self._get_room_access_level()

        if self._room_access_level < 60:
            raise ValueError('For this operation level access must be more 60.')

        return func(self)

    return wrapper


def need_homeserver_admin_access_level(func):
    """
    This decorator checks user access for protecting media on the homeserver.
    """

    def wrapper(self):
        if self._homeserver_access_level is None:
            self._get_homeserver_access_level()

        if self._room_access_level < 60:
            raise ValueError('For this operation level access must be more 60.')

        return func(self)

    return wrapper


class MatrixStickersManager:
    __homeserver_domain: str
    __access_token: str
    _room_access_level: int
    _homeserver_access_level: int
    __room_id: str
    __user_id: str

    def __init__(self, homeserver_domain: str, access_token: str):
        self.__homeserver_domain = homeserver_domain
        self.__access_token = access_token

        if not self.__is_token_valid():
            raise ValueError('Your token is invalid.')

    def __is_token_valid(self) -> bool:
        """
        Try to get information of user token.

        https://playground.matrix.org/#get-/_matrix/client/v3/account/whoami
        """

        response = requests.get(
            url=f'https://{self.__homeserver_domain}/_matrix/client/v3/account/whoami?access_token={self.__access_token}'
        )

        if response.ok:
            self.__user_id = response.json()['user_id']
            return True
        else:
            return False

    def download_media(self, media_id: str) -> None:
        pass

    def upload_media(self, file_path: str) -> str:
        pass

    @need_room_moderator_access_level
    def __create_new_pack_object(self, name: str) -> None:
        pass

    @need_homeserver_admin_access_level
    def protect_media(self, file_path: str) -> None:
        pass

    def _get_room_access_level(self) -> None:
        pass

    def _get_homeserver_access_level(self) -> None:
        pass

    @property
    def user_id(self):
        return self.__user_id
