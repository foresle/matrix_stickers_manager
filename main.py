from matrix_stickers_manager import MatrixStickersManager

manager = MatrixStickersManager()

# Upload multiple images to sticker pack
manager.load_pack_from_folder(
        pack_name='My Funny Sticker Pack',
        folder_path='stickers/',
        room_id='!ahkeeyahPhexohtooh:matrix.your.server',
        protect_media=True,
        number_as_shortcode=False
)

# Download images from pack
manager.export_pack(
        pack_name='My Funny Sticker Pack',
        export_folder='stickers/',
        room_id='!ahkeeyahPhexohtooh:matrix.your.server',
        original_name=True
)

# Delete pack
manager.delete_pack(
        pack_name='My Funny Sticker Pack',
        room_id='!ahkeeyahPhexohtooh:matrix.your.server',
)
