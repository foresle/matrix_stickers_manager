# matrix_stickers_manager

> "Its solution for massive upload your stickers into Matrix." 

This code using [MSC2545](https://github.com/Sorunome/matrix-doc/blob/soru/emotes/proposals/2545-emotes.md) aka native stickers. Cinny and FluffyChat support this specs already.

### Config

Just copy `example.config.yaml` to `config.yaml` and write your values.

**Required room admin token. For protection images also user must be server admin.**

### Example usage

```python
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
```

```text
stickers
├── 1.png
├── 2.png
├── 3.png
├── 4.png
```

### Protection media

> "Protection works only in Synapse Server API."