from matrix_stickers_manager import MatrixStickersManager

manager: MatrixStickersManager


def test_init_manager():
    manager = MatrixStickersManager(path_to_config='../config.yaml')
