import typer
from typing_extensions import Annotated

from matrix_stickers_manager import MatrixStickersManager


def main(
        homeserver_domain: Annotated[str, typer.Option(
            help='Example: matrix.example.com'
        )],
        access_token: Annotated[str, typer.Option(
            help='Your access token.'
        )]
) -> None:
    manager: MatrixStickersManager = MatrixStickersManager(
        homeserver_domain=homeserver_domain,
        access_token=access_token
    )
    print(f'Hi {manager.user_id}! Your token is valid, Let\'s start a job!')


if __name__ == '__main__':
    typer.run(main)
