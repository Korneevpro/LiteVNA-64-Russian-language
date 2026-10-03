#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Патчер русской локализации LiteVNA64 v1.4.08.

Патчер не содержит полного исходного образа LiteVNA. Он собирает локализованный
образ из официального исходного BIN пользователя и небольшого набора новых
данных/ссылок на диапазоны исходного файла.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import struct
from pathlib import Path
import sys

BASE_SHA256 = "22f91d4769b81b058343ad94055cbd94a2cffbc7e0378619a94d6abfc515d501"
LEGACY_OUTPUT_SHA256 = "368f443dc288b7be337d638db00b2858bd0f1530154de81449391ed3b7fb1bc7"
OUTPUT_SHA256 = "67fa2538b87730aa74aef6517d99aca834eee58ea4e4d26d01952f74c88f7516"
BASE_SIZE = 88128
LEGACY_OUTPUT_SIZE = 92853
OUTPUT_SIZE = 94506
DEFAULT_OUTPUT = "LiteVNA64_v1.4.08_RU_R3DQB.bin"

FLASH_BASE = 0x08004000
FONT_PTR_SITES = (0x009F8, 0x0A5FC, 0x0A6F8)
ORIG_FONT_BASE = 0x1126C
RU_FONT_BASE = 0x157C7
FONT_FIRST_CHAR = 0x0B
RU_FONT_FIRST_VALID_CHAR = 0x16
FONT_LAST_CHAR = 0xA0
FONT_GLYPH_SIZE = 11
OLD_RU_FONT_ADDR = FLASH_BASE + RU_FONT_BASE

# C = скопировать диапазон из исходной прошивки: ('C', offset, length)
# D = добавить новые данные, закодированные Base64: ('D', '...')
OPS = [
    ('C', 0, 2552),
    ('D', 'x5c='),
    ('C', 2554, 2694),
    ('D', 'hJ4BCIye'),
    ('C', 5254, 13394),
    ('D', 'UKcBCGinAQhcpw=='),
    ('C', 18658, 9666),
    ('D', 'CKABCBCgAQgYoAEIIKA='),
    ('C', 28338, 1658),
    ('D', 'HKMBCCSj'),
    ('C', 30002, 98),
    ('D', 'KKM='),
    ('C', 30102, 422),
    ('D', 'RKY='),
    ('C', 30526, 1298),
    ('D', 'cCIrRkDycA=='),
    ('C', 31831, 41),
    ('D', 'QPJ1EBpGibIC8Dr8QPKDEAHgQPJ3EA=='),
    ('C', 31894, 90),
    ('D', 'cCJJRkDycA=='),
    ('C', 31991, 165),
    ('D', 'QPJhEg=='),
    ('C', 32160, 5008),
    ('D', 'jKo='),
    ('C', 37170, 5322),
    ('D', 'x5c='),
    ('C', 42494, 250),
    ('D', 'x5c='),
    ('C', 42746, 30194),
    ('D', '8J4='),
    ('C', 72942, 26),
    ('D', '/J4='),
    ('C', 72970, 26),
    ('D', 'BJ8='),
    ('C', 72998, 26),
    ('D', 'TKY='),
    ('C', 73026, 27),
    ('D', 'ow=='),
    ('C', 73026, 26),
    ('D', 'pKM='),
    ('C', 73082, 26),
    ('D', 'IJ8='),
    ('C', 73110, 26),
    ('D', 'fKY='),
    ('C', 73138, 26),
    ('D', 'jKY='),
    ('C', 73166, 82),
    ('D', '1KY='),
    ('C', 73250, 110),
    ('D', '4KY='),
    ('C', 73362, 1556),
    ('D', 'RKIBCFmHAAgDAUSiAQhZhwAIAwJEogEIWYcACAMDRKIBCFmHAAgDAFCiAQhpjAAIAwFgogEIaYwACAMCcKIBCGmMAAgDA4Ci'),
    ('C', 74990, 700),
    ('D', 'CKABCIWzAAgAARCgAQiFswAIAAIYoAEIhbMACAAEIKABCIWzAAgAA9in'),
    ('C', 75732, 38),
    ('D', 'HKMBCE20AAgGAByjAQhNtAAIBAEkowEITbQACAYBJKMBCE20AAgBDMSeAQjNggAIBg3Eng=='),
    ('C', 75822, 78),
    ('D', 'mKQ='),
    ('C', 75902, 2180),
    ('D', 'AKQBCL25AAgDEhypAQi9uQAIAxM0qQEIvbkACAMQTKkBCL25AAgDEVypAQi9uQAIAxRsqQEIvbkACAMVfKk='),
    ('C', 78144, 18),
    ('D', '8KUBCGFYAAgCBuikAQiFzgAIAgb8pAEIOcwACAEAEKUBCNxvAQgBAPyl'),
    ('C', 78204, 18),
    ('D', 'JKUBCDWHAAgBALigAQiwcAEIAQDIoAEIYHABCAEAEKgBCBhwAQgBAOSgAQjwbwEIAwQwpQEIgYYACAIFQKUBCLnNAAgCBVCl'),
    ('C', 78294, 20),
    ('D', 'jKkBCL25AAgDmKSpAQi9uQAIA5m8qQEIvbkACAOa1KkBCL25AAgDm+SpAQi9uQAIA5z0qQEIvbkACAOdnKY='),
    ('C', 78376, 19),
    ('D', 'owEIvbkACAMFpKMBCL25AAgDB3ymAQi9uQAIAwiMpgEIvbkACAMWnKYBCL25AAgDDfCoAQi9uQAIAw4AqQEIvbkACAMP4KYBCL25AAgBAOym'),
    ('C', 78476, 60),
    ('D', 'eKoBCK2/AAgDFtylAQitvwAIAwWgpAEI/bAACAMHtKQBCP2wAAgDGcikAQitvwAIAxrQpAEIrb8ACAMG2KQBCP2wAAgBAOym'),
    ('C', 78608, 18),
    ('D', 'YKUBCLnNAAgCAHClAQi5zQAIAgF8pQEIuc0ACAIEiKU='),
    ('C', 78658, 20),
    ('D', 'uKABCI1ZAAgDAsigAQiNWQAIAwAQqAEIjVkACAMDmKUBCI1ZAAgDBOSgAQiNWQAIAQCkpQEIjHEBCAIAtKUBCDnOAAgCAbyl'),
    ('C', 78750, 192),
    ('D', 'yKcBCDWKAAgDAPyf'),
    ('C', 78954, 20),
    ('D', '+KYBCAG3AAgDAgSqAQjliAAIAwQkqgEI5YgACAMAMKcBCOWIAAgDAESnAQiJiAAIAxJEqg=='),
    ('C', 79026, 20),
    ('D', 'yKIBCPnHAAgDCByjAQjJvwAIAwokowEIyb8ACAMM1KIBCMm/AAgDDtyiAQjJvwAIAw+UpwEIrb8ACAMR8KIBCK2/AAgDA6SnAQj9sAAIAwS4pw=='),
    ('C', 79128, 18),
    ('D', '8J4BCL25AAgDgfyeAQi9uQAIA4IEnwEIvbkACAODTKYBCL25AAgDhJijAQi9uQAIA4WkowEIvbkACAOHfKYBCL25AAgDiIymAQi9uQAIAQDspg=='),
    ('C', 79228, 18),
    ('D', '8J4BCL25AAgDAfyeAQi9uQAIAwIEnwEIvbkACAMDTKYBCL25AAgDBiCfAQi9uQAIAwloqgEIvbkACAMKMJ8BCL25AAgDC9SmAQi9uQAIAQDspg=='),
    ('C', 79328, 18),
    ('D', 'rKgBCIXOAAgCAPChAQiFzgAIAQDAqAEIvHIBCAIF3KgBCIXOAAgBAByiAQiccgEIAgIoogEIhc4ACAIDNKIBCIXOAAgDADyi'),
    ('C', 79418, 20),
    ('D', 'EKgBCCBzAQgCACCoAQg5zAAIAgEwqAEIOcwACAICWKMBCDnMAAgCBECoAQg5zAAIAwAwoQEI/bAACAMIOKEBCP2wAAgCAFio'),
    ('C', 79510, 20),
    ('D', 'VKE='),
    ('C', 79532, 90),
    ('D', 'Up4BCFRzAQgBAGygAQjsbQEIAwB4oAEI1bEACAMAhKABCIGGAAgDAYygAQiBhgAIAwKYoAEIgYYACAMDpKA='),
    ('C', 79684, 18),
    ('D', 'CKABCK2/AAgDARCgAQitvwAIAwIYoAEIrb8ACAMDIKABCK2/AAgDBNinAQitvwAIAwU0oAEIrb8ACAMGQKABCK2/AAgDB+inAQitvwAIAQD4pw=='),
    ('C', 79784, 18),
    ('D', 'qJ8BCAx0AQgDArSfAQj9sAAIAv+8nwEIEYkACAIByJ8BCBGJAAgBANifAQjQcwEIAwDknw=='),
    ('C', 79854, 20),
    ('D', 'oJ4BCJ25AAgBAJiiAQiMdQEIAQCwogEIKHUBCAMASKMBCCmIAAgBAMSeAQjEdAEIAQDMngEIfHQBCAMA3J4BCK26AAgDGOie'),
    ('C', 79946, 20),
    ('D', 'PJ4BCAB4AQgBAESeAQi4dwEIAQBKngEIVHcBCAEAUp4BCAR3AQgBAF2eAQiodgEIAgBnngEIGbsACAEAcZ4BCEx2AQgBAHqeAQjwdQEIAwCUng=='),
    ('C', 80048, 18),
    ('D', 'RKYBCE27AAgDB2yh'),
    ('C', 80078, 20),
    ('D', 'RKYBCE27AAgDBnyhAQhNuwAIAxJEqg=='),
    ('C', 80120, 30),
    ('D', 'RKYBCE27AAgDBYyh'),
    ('C', 80078, 20),
    ('D', 'RKYBCE27AAgDAmioAQhNuwAIAwOAqAEITbsACAMExKE='),
    ('C', 80214, 28),
    ('D', 'RKYBCE27AAgDAZyo'),
    ('C', 80078, 20),
    ('D', 'RKYBCE27AAgDAZyoAQhNuwAIAwZ8oQEITbsACAMHbKEBCE27AAgDAmioAQhNuwAIAwOAqAEITbsACAMExKEBCE27AAgDBYyh'),
    ('C', 80346, 21),
    ('D', 'og=='),
    ('C', 80368, 2847),
    ('D', 'j5iJkpMAko+WkS4='),
    ('C', 83226, 4902),
    ('C', 70373, 1166),
    ('D', 'AXjMzMz8zMzMzAAB/MDA+MzMzMz4AAH4zMzM+MzMzPgAAfzAwMDAwMDAwAABPGxsbGxsbP7GAAH8wMDA+MDAwPwARfzAwPjAwMD8AAAB1tZ8OHzW1tbWAAF4zAwYOAwMzHgAAczM3Nzs7OzMzAA5UMzM3Nzs7OzMAAHMzMzY8NjMzMwAATxsbGxsbGzMzAAAxsbu7tbW1sbGAAHMzMzM/MzMzMwAAXjMzMzMzMzMeAAB/MzMzMzMzMzM'),
    ('C', 71010, 16),
    ('D', 'wMDA'),
    ('C', 71051, 19),
    ('D', 'eDAwYMDAAAEwfNzc3HwwMDA='),
    ('C', 71098, 17),
    ('D', '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'),
    ('C', 85911, 16),
    ('D', 'ko+QkY+TiYKMhY6JhQAAAI+Qj5GOnIoKg4WOhZGAk4+RAAAAQmF0dDogJWQuJTAyZFYKVHJhbnNsYXRpb24gUnVzc2lhbiBSM0RRQgA='),
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()



def repair_font_table(source: bytes, localized: bytes) -> bytes:
    """Собирает полную таблицу 7x11 и перенаправляет на неё рендерер.

    В первой версии локализации перенесённая таблица начиналась фактически
    с символа 0x16, тогда как LiteVNA64 v1.4.08 индексирует её с 0x0B.
    Поэтому служебные глифы 0x0B..0x15, включая символ сопротивления Ω
    (0x0C), читались из посторонних данных.

    Исправление не перезаписывает существующие данные локализации:
    новая полная таблица добавляется в конец образа, после чего меняются
    только три проверенных указателя на таблицу шрифта.
    """
    if len(localized) != LEGACY_OUTPUT_SIZE:
        raise RuntimeError(
            f"Неверный промежуточный размер: {len(localized)} вместо {LEGACY_OUTPUT_SIZE} байт."
        )

    for site in FONT_PTR_SITES:
        current = struct.unpack_from("<I", localized, site)[0]
        if current != OLD_RU_FONT_ADDR:
            raise RuntimeError(
                f"Неожиданный указатель шрифта по смещению 0x{site:X}: 0x{current:08X}."
            )

    prefix_size = (RU_FONT_FIRST_VALID_CHAR - FONT_FIRST_CHAR) * FONT_GLYPH_SIZE
    font_size = (FONT_LAST_CHAR - FONT_FIRST_CHAR + 1) * FONT_GLYPH_SIZE
    suffix_size = font_size - prefix_size

    prefix = source[ORIG_FONT_BASE:ORIG_FONT_BASE + prefix_size]
    suffix_off = RU_FONT_BASE + prefix_size
    suffix = localized[suffix_off:suffix_off + suffix_size]

    if len(prefix) != prefix_size or len(suffix) != suffix_size:
        raise RuntimeError("Не удалось собрать полную таблицу шрифта.")

    full_font = prefix + suffix

    # Ω — код 0x0C. Сверяем его с исходной штатной таблицей.
    ohm_index = 0x0C - FONT_FIRST_CHAR
    glyph_start = ohm_index * FONT_GLYPH_SIZE
    glyph_end = glyph_start + FONT_GLYPH_SIZE
    source_ohm = source[
        ORIG_FONT_BASE + glyph_start:
        ORIG_FONT_BASE + glyph_end
    ]
    if full_font[glyph_start:glyph_end] != source_ohm:
        raise RuntimeError("Контроль глифа Ω не пройден.")

    out = bytearray(localized)
    while len(out) % 4:
        out.append(0)

    new_font_off = len(out)
    out.extend(full_font)
    new_font_addr = FLASH_BASE + new_font_off

    for site in FONT_PTR_SITES:
        struct.pack_into("<I", out, site, new_font_addr)

    return bytes(out)

def apply_patch(source: bytes) -> bytes:
    if len(source) != BASE_SIZE:
        raise ValueError(f"Неверный размер исходной прошивки: {len(source)} байт; ожидается {BASE_SIZE}.")
    actual = sha256(source)
    if actual != BASE_SHA256:
        raise ValueError(
            "SHA-256 исходной прошивки не совпадает с поддерживаемой версией.\n"
            f"Ожидается: {BASE_SHA256}\n"
            f"Получено:  {actual}\n"
            "Используйте чистый оригинальный LiteVNA64 v1.4.08.bin."
        )

    out = bytearray()
    for op in OPS:
        if op[0] == "C":
            _, offset, length = op
            out.extend(source[offset:offset + length])
        elif op[0] == "D":
            out.extend(base64.b64decode(op[1]))
        else:
            raise RuntimeError(f"Неизвестная операция патча: {op[0]}")

    legacy = bytes(out)
    if len(legacy) != LEGACY_OUTPUT_SIZE:
        raise RuntimeError(
            f"Ошибка промежуточной сборки: размер {len(legacy)} вместо {LEGACY_OUTPUT_SIZE} байт."
        )
    legacy_sha = sha256(legacy)
    if legacy_sha != LEGACY_OUTPUT_SHA256:
        raise RuntimeError(
            "Контрольная сумма промежуточной локализации не совпала.\n"
            f"Ожидается: {LEGACY_OUTPUT_SHA256}\n"
            f"Получено:  {legacy_sha}"
        )

    result = repair_font_table(source, legacy)

    if len(result) != OUTPUT_SIZE:
        raise RuntimeError(f"Ошибка сборки: размер {len(result)} вместо {OUTPUT_SIZE} байт.")
    actual_out = sha256(result)
    if actual_out != OUTPUT_SHA256:
        raise RuntimeError(
            "Контрольная сумма собранной прошивки не совпала.\n"
            f"Ожидается: {OUTPUT_SHA256}\n"
            f"Получено:  {actual_out}"
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Создание русской прошивки LiteVNA64 v1.4.08 из оригинального BIN."
    )
    parser.add_argument("firmware", type=Path, help="Путь к оригинальному LiteVNA64 v1.4.08.bin")
    parser.add_argument("-o", "--output", type=Path, default=Path(DEFAULT_OUTPUT), help="Выходной BIN")
    args = parser.parse_args()

    try:
        source = args.firmware.read_bytes()
        result = apply_patch(source)
        args.output.write_bytes(result)
    except (OSError, ValueError, RuntimeError) as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return 1

    print("Готово.")
    print(f"Файл: {args.output}")
    print(f"Размер: {len(result)} байт")
    print(f"SHA-256: {sha256(result)}")
    print("Адрес прошивки: 0x08004000")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
