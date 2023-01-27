# matrix_stickers_manager

> "Its solution for massive upload your stickers into Matrix." 

### Config

Just copy `example.config.yaml` to `config.yaml` and write your values.

**Must be token for admin account in the target room.**

### Example usage

```python
from matrix_stickers_manager import MatrixStickersManager

manager = MatrixStickersManager()
manager.load_pack_from_folder(
        pack_name='my_new_stickers_pack',
        folder_path='../stickers/',
        room_id='your_room_id'
)
```

```text
stickers
├── 1.png
├── 2.png
├── 3.png
├── 4.png
```