#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Указываем, что скрипт должен запускаться через Python 3 и использует кодировку UTF-8

# Импортируем необходимые модули
import ctypes  # Для работы с Windows API через вызовы C-функций
from ctypes import wintypes  # Импортируем Windows-специфичные типы данных
import sys  # Для системных функций, таких как выход из программы
import os  # Для работы с операционной системой


def get_os_version():
    """
    Определяет версию Windows с помощью RtlGetVersion из ntdll.dll
    Это более надежный способ, чем устаревший GetVersionEx
    """
    # Проверяем, существует ли функция RtlGetVersion в библиотеке ntdll
    if hasattr(ctypes.windll.ntdll, 'RtlGetVersion'):
        # Создаем структуру OSVERSIONINFOEXW, которая соответствует Windows API структуре
        class OSVERSIONINFOEXW(ctypes.Structure):
            # Определяем поля структуры в том же порядке, как в Windows API
            _fields_ = [
                ('dwOSVersionInfoSize', wintypes.DWORD),  # Размер структуры в байтах
                ('dwMajorVersion', wintypes.DWORD),  # Основной номер версии (например, 10 для Windows 10)
                ('dwMinorVersion', wintypes.DWORD),  # Дополнительный номер версии (например, 0 для Windows 10)
                ('dwBuildNumber', wintypes.DWORD),  # Номер сборки ОС
                ('dwPlatformId', wintypes.DWORD),  # Идентификатор платформы
                ('szCSDVersion', wintypes.WCHAR * 128),  # Строка с информацией о сервис-паке
                ('wServicePackMajor', wintypes.WORD),  # Основной номер сервис-пака
                ('wServicePackMinor', wintypes.WORD),  # Дополнительный номер сервис-пака
                ('wSuiteMask', wintypes.WORD),  # Битовые флаги, указывающие набор продуктов
                ('wProductType', wintypes.BYTE),  # Тип продукта (рабочая станция, сервер и т.д.)
                ('wReserved', wintypes.BYTE)  # Зарезервированное поле для выравнивания
            ]

        # Создаем экземпляр структуры OSVERSIONINFOEXW
        os_version = OSVERSIONINFOEXW()
        # Заполняем поле размера структуры - это обязательное требование Windows API
        os_version.dwOSVersionInfoSize = ctypes.sizeof(OSVERSIONINFOEXW)
        # Вызываем функцию RtlGetVersion для получения информации о версии ОС
        # ctypes.byref(os_version) передает указатель на нашу структуру
        ret = ctypes.windll.ntdll.RtlGetVersion(ctypes.byref(os_version))

        # Проверяем код возврата функции (0 означает успех в Windows API)
        if ret != 0:
            # Если функция вернула ошибку, возвращаем сообщение об ошибке
            return "Не удалось определить версию Windows"

        # Создаем карту соответствия версий Windows их читаемым названиям
        # Формат: (основная_версия, дополнительная_версия, читаемое_название)
        version_map = [
            (10, 0, "Windows 11 или Windows Server 2022"),
            # Windows 11 использует те же номера версий, что и Windows 10
            (10, 0, "Windows 10 или Windows Server 2019"),  # Windows 10
            (6, 3, "Windows 8.1 или Windows Server 2012 R2"),  # Windows 8.1
            (6, 2, "Windows 8 или Windows Server 2012"),  # Windows 8
            (6, 1, "Windows 7 или Windows Server 2008 R2"),  # Windows 7
            (6, 0, "Windows Vista или Windows Server 2008"),  # Windows Vista
            (5, 2, "Windows XP Professional x64 или Windows Server 2003"),  # Windows XP x64
            (5, 1, "Windows XP"),  # Windows XP
            (5, 0, "Windows 2000")  # Windows 2000
        ]

        # Проходим по всем элементам карты версий
        for major, minor, name in version_map:
            # Сравниваем полученные версии с картой
            if os_version.dwMajorVersion == major and os_version.dwMinorVersion == minor:
                # Если нашли совпадение, возвращаем название и номер сборки
                return f"{name} (Build {os_version.dwBuildNumber})"

        # Если версия не найдена в карте, возвращаем неизвестную версию с номерами
        return f"Неизвестная версия Windows ({os_version.dwMajorVersion}.{os_version.dwMinorVersion})"

    # Если функция RtlGetVersion не найдена, возвращаем сообщение об ошибке
    return "Не удалось определить версию Windows"


def get_memory_info():
    """
    Получает информацию о физической и виртуальной памяти через GlobalMemoryStatusEx
    Возвращает кортеж: (общая_физическая_память_МБ, доступная_физическая_память_МБ,
                        загрузка_памяти_%, общая_виртуальная_память_МБ)
    """

    # Определяем структуру MEMORYSTATUSEX, которая соответствует Windows API
    class MEMORYSTATUSEX(ctypes.Structure):
        # Поля структуры должны точно соответствовать Windows API
        _fields_ = [
            ('dwLength', wintypes.DWORD),  # Размер структуры в байтах
            ('dwMemoryLoad', wintypes.DWORD),  # Процент использования памяти (0-100)
            ('ullTotalPhys', ctypes.c_ulonglong),  # Общий объем физической памяти в байтах
            ('ullAvailPhys', ctypes.c_ulonglong),  # Доступный объем физической памяти в байтах
            ('ullTotalPageFile', ctypes.c_ulonglong),  # Максимальный размер файла подкачки в байтах
            ('ullAvailPageFile', ctypes.c_ulonglong),  # Доступный размер файла подкачки в байтах
            ('ullTotalVirtual', ctypes.c_ulonglong),  # Общий объем виртуальной памяти в байтах
            ('ullAvailVirtual', ctypes.c_ulonglong),  # Доступный объем виртуальной памяти в байтах
            ('ullAvailExtendedVirtual', ctypes.c_ulonglong)  # Расширенная виртуальная память (обычно 0)
        ]

    # Создаем экземпляр структуры MEMORYSTATUSEX
    memory_status = MEMORYSTATUSEX()
    # Устанавливаем размер структуры - это обязательное поле для Windows API
    memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)

    # Вызываем функцию GlobalMemoryStatusEx из kernel32.dll
    # Функция заполняет нашу структуру данными о памяти
    if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status)):
        # Если вызов успешен, конвертируем байты в мегабайты
        total_phys_mb = memory_status.ullTotalPhys // (1024 * 1024)  # Деление на 1024*1024 для перевода в МБ
        avail_phys_mb = memory_status.ullAvailPhys // (1024 * 1024)  # Доступная физическая память в МБ
        memory_load = memory_status.dwMemoryLoad  # Процент использования памяти (0-100)
        total_virtual_mb = memory_status.ullTotalVirtual // (1024 * 1024)  # Виртуальная память в МБ

        # Возвращаем кортеж с полученными значениями
        return total_phys_mb, avail_phys_mb, memory_load, total_virtual_mb
    else:
        # Если вызов функции не удался, возвращаем None
        return None


def get_processor_info():
    """
    Получает информацию о процессоре через GetSystemInfo
    Возвращает кортеж: (количество_процессоров, архитектура_процессора)
    """

    # Определяем структуру SYSTEM_INFO, соответствующую Windows API
    class SYSTEM_INFO(ctypes.Structure):
        _fields_ = [
            ('wProcessorArchitecture', wintypes.WORD),  # Архитектура процессора (код)
            ('wReserved', wintypes.WORD),  # Зарезервированное поле
            ('dwPageSize', wintypes.DWORD),  # Размер страницы памяти в байтах
            ('lpMinimumApplicationAddress', ctypes.c_void_p),  # Минимальный адрес, доступный приложению
            ('lpMaximumApplicationAddress', ctypes.c_void_p),  # Максимальный адрес, доступный приложению
            ('dwActiveProcessorMask', ctypes.c_void_p),  # Битовая маска активных процессоров
            ('dwNumberOfProcessors', wintypes.DWORD),  # Количество процессоров в системе
            ('dwProcessorType', wintypes.DWORD),  # Тип процессора (устаревшее)
            ('dwAllocationGranularity', wintypes.DWORD),  # Гранулярность выделения памяти
            ('wProcessorLevel', wintypes.WORD),  # Уровень процессора
            ('wProcessorRevision', wintypes.WORD)  # Ревизия процессора
        ]

    # Создаем экземпляр структуры SYSTEM_INFO
    system_info = SYSTEM_INFO()
    # Вызываем GetSystemInfo для заполнения структуры данными о системе
    ctypes.windll.kernel32.GetSystemInfo(ctypes.byref(system_info))

    # Создаем словарь для преобразования кодов архитектуры в читаемые названия
    arch_map = {
        0: "x86",  # Intel x86 32-битная архитектура
        6: "IA-64",  # Intel Itanium 64-битная архитектура
        9: "x64 (AMD64)",  # AMD64 или Intel 64 64-битная архитектура
        12: "ARM"  # ARM архитектура
    }
    # Получаем читаемое название архитектуры по коду, или "Неизвестно" если код не найден
    architecture = arch_map.get(system_info.wProcessorArchitecture, "Неизвестно")

    # Возвращаем количество процессоров и архитектуру
    return system_info.dwNumberOfProcessors, architecture


def get_performance_info():
    """
    Получает информацию о производительности через GetPerformanceInfo
    Включает информацию о файле подкачки (commit memory)
    Возвращает кортеж: (текущий_размер_коммита_МБ, лимит_коммита_МБ)
    """

    # Определяем структуру PERFORMANCE_INFORMATION из psapi.dll
    class PERFORMANCE_INFORMATION(ctypes.Structure):
        _fields_ = [
            ('cb', wintypes.DWORD),  # Размер структуры в байтах
            ('CommitTotal', ctypes.c_size_t),  # Текущий объем закоммитованной памяти в страницах
            ('CommitLimit', ctypes.c_size_t),  # Максимальный объем памяти, который можно закоммитить в страницах
            ('CommitPeak', ctypes.c_size_t),  # Пиковый объем закоммитованной памяти в страницах
            ('PhysicalTotal', ctypes.c_size_t),  # Общая физическая память в страницах
            ('PhysicalAvailable', ctypes.c_size_t),  # Доступная физическая память в страницах
            ('SystemCache', ctypes.c_size_t),  # Размер системного кэша в страницах
            ('KernelTotal', ctypes.c_size_t),  # Общая память ядра в страницах
            ('KernelPaged', ctypes.c_size_t),  # Пейджируемая память ядра в страницах
            ('KernelNonpaged', ctypes.c_size_t),  # Непейджируемая память ядра в страницах
            ('PageSize', ctypes.c_size_t),  # Размер страницы памяти в байтах
            ('HandleCount', wintypes.DWORD),  # Количество открытых handles в системе
            ('ProcessCount', wintypes.DWORD),  # Количество активных процессов
            ('ThreadCount', wintypes.DWORD)  # Количество активных потоков
        ]

    # Создаем экземпляр структуры PERFORMANCE_INFORMATION
    perf_info = PERFORMANCE_INFORMATION()
    # Устанавливаем размер структуры
    perf_info.cb = ctypes.sizeof(PERFORMANCE_INFORMATION)

    # Вызываем GetPerformanceInfo из psapi.dll
    if ctypes.windll.psapi.GetPerformanceInfo(ctypes.byref(perf_info), perf_info.cb):
        # Получаем размер страницы памяти в байтах
        page_size = perf_info.PageSize
        # Вычисляем текущий коммит в мегабайтах: страницы * размер_страницы / (1024*1024)
        commit_total = perf_info.CommitTotal * page_size // (1024 * 1024)
        # Вычисляем лимит коммита в мегабайтах
        commit_limit = perf_info.CommitLimit * page_size // (1024 * 1024)
        # Возвращаем кортеж с результатами
        return commit_total, commit_limit
    else:
        # Если вызов не удался, возвращаем None
        return None


def get_drives_info():
    """
    Получает информацию о логических дисках системы
    Использует GetLogicalDrives, GetVolumeInformation и GetDiskFreeSpaceEx
    Возвращает список кортежей: [(буква_диска, тип_ФС, свободно_ГБ, всего_ГБ), ...]
    """
    drives = []  # Создаем пустой список для хранения букв дисков
    # Вызываем GetLogicalDrives, который возвращает битовую маску дисков
    # Каждый бит соответствует наличию диска (A-Z)
    drive_bits = ctypes.windll.kernel32.GetLogicalDrives()

    # Проходим по всем возможным буквам дисков от A до Z (ASCII коды 65-90)
    for letter in range(65, 91):
        # Проверяем, установлен ли бит для текущей буквы диска
        # (letter - 65) вычисляет позицию бита (0 для A, 1 для B, и т.д.)
        # 1 << (letter - 65) создает битовую маску для текущей буквы
        # drive_bits & mask проверяет, установлен ли этот бит
        if drive_bits & (1 << (letter - 65)):
            # Если диск существует, добавляем его букву в список
            drive_name = f"{chr(letter)}:\\"  # Форматируем букву диска (например, "C:\")
            drives.append(drive_name)

    drive_info = []  # Создаем список для хранения информации о дисках
    # Проходим по всем найденным дискам
    for drive in drives:
        try:
            # Создаем буфер для хранения имени файловой системы (32 символа Unicode)
            fs_name = ctypes.create_unicode_buffer(32)
            # Вызываем GetVolumeInformationW для получения информации о томе
            if ctypes.windll.kernel32.GetVolumeInformationW(
                    drive,  # Имя корневого каталога диска
                    None, 0,  # Буфер для метки тома (не используем)
                    None, None,  # Указатели на серийный номер и максимальную длину имени файла
                    None,  # Указатель на флаги файловой системы
                    fs_name,  # Буфер для имени файловой системы (NTFS, FAT32 и т.д.)
                    ctypes.sizeof(fs_name)):  # Размер буфера
                # Если вызов успешен, получаем значение из буфера
                fs_type = fs_name.value
            else:
                # Если вызов не удался, устанавливаем неизвестный тип ФС
                fs_type = "Неизвестно"

            # Создаем переменные для хранения информации о свободном месте
            free_bytes = ctypes.c_ulonglong()  # Для свободного места в байтах
            total_bytes = ctypes.c_ulonglong()  # Для общего места в байтах

            # Вызываем GetDiskFreeSpaceExW для получения информации о свободном месте
            if ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    drive,  # Имя директории
                    ctypes.byref(free_bytes),  # Указатель на переменную для свободного места
                    ctypes.byref(total_bytes),  # Указатель на переменную для общего места
                    None):  # Указатель на доступное место (не используем)

                # Конвертируем байты в гигабайты (деление на 1024^3)
                free_gb = free_bytes.value // (1024 * 1024 * 1024)
                total_gb = total_bytes.value // (1024 * 1024 * 1024)

                # Добавляем информацию о диске в список
                drive_info.append((drive, fs_type, free_gb, total_gb))

        except Exception as e:
            # Если произошла ошибка при получении информации о диске, пропускаем его
            # Это может произойти, если диск недоступен (например, CD-ROM без диска)
            continue

    # Возвращаем список с информацией о всех доступных дисках
    return drive_info


def get_computer_and_user_name():
    """
    Получает имя компьютера и имя текущего пользователя
    Использует GetComputerNameW и GetUserNameW
    Возвращает кортеж: (имя_компьютера, имя_пользователя)
    """
    # Получаем имя компьютера
    computer_name = ctypes.create_unicode_buffer(256)  # Создаем буфер для имени компьютера
    size = wintypes.DWORD(256)  # Создаем переменную для размера буфера
    # Вызываем GetComputerNameW для получения имени компьютера
    if ctypes.windll.kernel32.GetComputerNameW(computer_name, ctypes.byref(size)):
        # Если вызов успешен, получаем значение из буфера
        computer = computer_name.value
    else:
        # Если вызов не удался, устанавливаем значение по умолчанию
        computer = "Неизвестно"

    # Получаем имя пользователя
    user_name = ctypes.create_unicode_buffer(256)  # Создаем буфер для имени пользователя
    size = wintypes.DWORD(256)  # Создаем переменную для размера буфера
    # Вызываем GetUserNameW из advapi32.dll для получения имени пользователя
    if ctypes.windll.advapi32.GetUserNameW(user_name, ctypes.byref(size)):
        # Если вызов успешен, получаем значение из буфера
        user = user_name.value
    else:
        # Если вызов не удался, устанавливаем значение по умолчанию
        user = "Неизвестно"

    # Возвращаем кортеж с именем компьютера и пользователя
    return computer, user


def main():
    """
    Основная функция программы
    Организует сбор и отображение всей системной информации
    """
    # Выводим заголовок программы
    print("=" * 50)  # Печатаем строку из 50 знаков "="
    print("СИСТЕМНАЯ ИНФОРМАЦИЯ - WINDOWS")
    print("=" * 50)

    # 1. Получаем и выводим версию операционной системы
    os_version = get_os_version()  # Вызываем функцию получения версии ОС
    print(f"ОС: {os_version}")  # Форматируем строку с помощью f-строки

    # 2. Получаем и выводим имя компьютера и пользователя
    computer_name, user_name = get_computer_and_user_name()  # Получаем оба значения
    print(f"Имя компьютера: {computer_name}")  # Выводим имя компьютера
    print(f"Пользователь: {user_name}")  # Выводим имя пользователя

    # 3. Получаем и выводим информацию о процессоре
    processor_count, architecture = get_processor_info()  # Получаем информацию о процессоре
    print(f"Архитектура: {architecture}")  # Выводим архитектуру процессора
    print(f"Процессоры: {processor_count}")  # Выводим количество процессоров

    # 4. Получаем и выводим информацию о памяти
    memory_info = get_memory_info()  # Вызываем функцию получения информации о памяти
    if memory_info:  # Проверяем, что данные получены успешно
        # Распаковываем кортеж с информацией о памяти
        total_phys_mb, avail_phys_mb, memory_load, total_virtual_mb = memory_info
        # Вычисляем использованную память (общая - доступная)
        used_phys_mb = total_phys_mb - avail_phys_mb
        # Выводим информацию об оперативной памяти
        print(f"Оперативная память: {used_phys_mb} МБ / {total_phys_mb} МБ")
        # Выводим информацию о виртуальной памяти
        print(f"Виртуальная память: {total_virtual_mb} МБ")
        # Выводим процент загрузки памяти
        print(f"Загрузка памяти: {memory_load}%")

    # 5. Получаем и выводим информацию о файле подкачки
    perf_info = get_performance_info()  # Вызываем функцию получения информации о производительности
    if perf_info:  # Проверяем, что данные получены успешно
        # Распаковываем кортеж с информацией о файле подкачки
        commit_total, commit_limit = perf_info
        # Выводим информацию о файле подкачки
        print(f"Файл подкачки: {commit_total} МБ / {commit_limit} МБ")

    # 6. Получаем и выводим информацию о дисках
    print("\nДиски:")  # Печатаем заголовок для раздела дисков (\n - новая строка)
    drives_info = get_drives_info()  # Получаем информацию о всех дисках
    # Проходим по всем дискам в цикле
    for drive, fs_type, free_gb, total_gb in drives_info:
        # Для каждого диска выводим информацию в формате:
        # - C:\ (NTFS): свободно 114 ГБ / всего 237 ГБ
        print(f" - {drive} ({fs_type}): свободно {free_gb} ГБ / всего {total_gb} ГБ")


# Стандартная конструкция для Python: код выполняется только если скрипт запущен напрямую
if __name__ == "__main__":
    try:
        main()  # Вызываем основную функцию
    except Exception as e:
        # Если произошла непредвиденная ошибка, выводим сообщение и завершаем программу с кодом ошибки 1
        print(f"Произошла ошибка: {e}")
        sys.exit(1)  # Завершаем программу с кодом возврата 1 (ошибка)