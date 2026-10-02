# Драйвер AT32 Bootloader DFU для Windows

Для работы WebUSB DFU Flasher в Windows устройство **AT32 Bootloader DFU** должно иметь корректный USB-драйвер.

## Рекомендуемый вариант: официальный Artery DFU Driver

Artery поставляет программу:

`Artery_DFU_DriverInstall.exe`

Она входит в официальный комплект **ISP Programmer**.

Официальная страница Artery:

https://arterytek.com/en/support/tools.jsp?index=3

На странице выберите **ISP Programmer** и распакуйте архив. Установщик находится в каталоге с DFU-драйвером.

### Установка

1. Переведите LiteVNA64 в DFU.
2. Запустите `Artery_DFU_DriverInstall.exe` от имени администратора.
3. Убедитесь, что программа видит `AT32 Bootloader DFU`.
4. Нажмите **Install driver**.
5. Если автоматическая установка не проходит, нажмите **Extract driver**, затем установите полученный каталог через «Обновить драйвер» в Диспетчере устройств.

## Контрольная сумма экземпляра, использованного при тестировании

```text
Имя: Artery_DFU_DriverInstall.exe
Размер: 9 735 168 байт
SHA-256: 9d3001bb2abe1228cdfa23a10b2b37a0196cf5d781b0075a63d9019c38a56e59
```

Проверка в PowerShell:

```powershell
Get-FileHash .\Artery_DFU_DriverInstall.exe -Algorithm SHA256
```

## Альтернатива: Zadig / WinUSB

README проекта WebUSB DFU Flasher рекомендует для Windows драйвер **WinUSB**. Если Artery-драйвер установлен, но браузер выдаёт `Access denied`, можно использовать Zadig:

https://zadig.akeo.ie/

1. Запустите Zadig от имени администратора.
2. **Options → List All Devices**.
3. Выберите **AT32 Bootloader DFU**.
4. В качестве драйвера выберите **WinUSB**.
5. Нажмите **Install Driver** или **Replace Driver**.

> Будьте внимательны: в Zadig выбирайте только устройство AT32 Bootloader DFU, а не клавиатуру, мышь, USB-хаб и т. п.

## Почему здесь нет COM-порта

AT32 Bootloader DFU — USB DFU-устройство. Для прошивки через WebUSB ему **не требуется появляться как COM-порт**.
