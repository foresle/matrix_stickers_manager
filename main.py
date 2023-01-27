import uuid

from matrix_stickers_manager import MatrixStickersManager

manager = MatrixStickersManager()
manager.load_pack_from_folder(
        pack_name=uuid.uuid4().hex,
        folder_path='../stickers/',
        room_id='!DFbnbNTzbZVVjjnRUz:matrix.opulus.space'
)
