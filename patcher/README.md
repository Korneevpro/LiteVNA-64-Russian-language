# Патчер

`patch_litevna_ru.py` создаёт локализованный BIN из чистой официальной прошивки LiteVNA64 v1.4.08.

## Требования

- Python 3.9+;
- внешние библиотеки не нужны.

## Использование

```bash
python patcher/patch_litevna_ru.py "LiteVNA64 v1.4.08.bin"
```

С выбором имени результата:

```bash
python patcher/patch_litevna_ru.py "LiteVNA64 v1.4.08.bin" -o litevna_ru.bin
```

Патчер жёстко проверяет SHA-256 исходного образа и не применяет смещения к неизвестной версии прошивки.
