import os
import sys
import platform
import subprocess
import re


def get_os_info():
    """
    Получает информацию о дистрибутиве Linux и версии ядра
    Использует несколько методов для максимальной совместимости
    """
    # Получаем версию ядра через встроенный модуль platform
    kernel_version = platform.release()  # Например: "5.15.0-86-generic"

    # Инициализируем переменную для хранения информации о дистрибутиве
    distro_info = "Неизвестно"

    try:
        # Метод 1: Чтение файла /etc/os-release (стандартный способ в современных дистрибутивах)
        # Файл /etc/os-release содержит информацию о дистрибутиве в формате ключ=значение
        with open('/etc/os-release', 'r') as f:  # Открываем файл для чтения
            content = f.read()  # Читаем все содержимое файла в строку

        # Используем регулярное выражение для поиска строки PRETTY_NAME
        # Шаблон r'PRETTY_NAME="([^"]+)"' ищет PRETTY_NAME="значение" и захватывает значение в группу 1
        match = re.search(r'PRETTY_NAME="([^"]+)"', content)
        if match:  # Если нашли совпадение
            distro_info = match.group(1)  # Извлекаем значение из первой группы захвата
        else:
            # Метод 2: Используем команду lsb_release (устаревший, но широко поддерживаемый способ)
            # Запускаем команду lsb_release -d которая выводит описание дистрибутива
            result = subprocess.run(['lsb_release', '-d'], capture_output=True, text=True)
            # Проверяем, что команда выполнилась успешно (код возврата 0)
            if result.returncode == 0:
                # Команда выводит "Description: Ubuntu 22.04.1 LTS"
                # Разделяем вывод по первому двоеточию и берем вторую часть, удаляя пробелы
                distro_info = result.stdout.split(':', 1)[1].strip()
    except:
        # Метод 3: Запасной вариант через модуль platform
        distro_info = platform.system()  # Возвращает например "Linux"

    # Возвращаем кортеж с информацией о дистрибутиве и версии ядра
    return distro_info, kernel_version


def get_memory_info():
    """
    Получает информацию об оперативной памяти и разделе подкачки из /proc/meminfo
    /proc/meminfo - виртуальный файл, предоставляемый ядром Linux с информацией о памяти
    """
    try:
        # Открываем виртуальный файл /proc/meminfo который предоставляет ядро Linux
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()  # Читаем все содержимое файла

        # Используем регулярные выражения для извлечения числовых значений
        # Шаблон r'MemTotal:\s+(\d+)' ищет "MemTotal:", затем пробелы и захватывает число
        mem_total = int(re.search(r'MemTotal:\s+(\d+)', meminfo).group(1))  # Общая память в КБ
        mem_free = int(re.search(r'MemFree:\s+(\d+)', meminfo).group(1))  # Свободная память в КБ
        mem_available = int(re.search(r'MemAvailable:\s+(\d+)', meminfo).group(1))  # Доступная память в КБ
        swap_total = int(re.search(r'SwapTotal:\s+(\d+)', meminfo).group(1))  # Общий своп в КБ
        swap_free = int(re.search(r'SwapFree:\s+(\d+)', meminfo).group(1))  # Свободный своп в КБ

        # Конвертируем из килобайт в мегабайты (деление на 1024)
        mem_total_mb = mem_total // 1024  # Общая память в МБ
        mem_available_mb = mem_available // 1024  # Доступная память в МБ
        swap_total_mb = swap_total // 1024  # Общий своп в МБ
        swap_free_mb = swap_free // 1024  # Свободный своп в МБ

        # Пытаемся получить информацию о виртуальной памяти (не во всех системах доступно)
        vmalloc_match = re.search(r'VmallocTotal:\s+(\d+)', meminfo)  # Ищем VmallocTotal
        # Если нашли, конвертируем из килобайт в мегабайты (двойное деление на 1024)
        vmalloc_total_mb = int(vmalloc_match.group(1)) // 1024 // 1024 if vmalloc_match else 0

        # Возвращаем кортеж со всей информацией о памяти
        return mem_total_mb, mem_available_mb, swap_total_mb, swap_free_mb, vmalloc_total_mb
    except Exception as e:
        # Если произошла ошибка при чтении или парсинге, возвращаем None
        return None


def get_processor_info():
    """
    Получает информацию о процессоре: количество ядер, архитектура и загрузка
    """
    try:
        # Получаем количество логических процессоров (ядер)
        # os.cpu_count() возвращает количество логических процессоров в системе
        processor_count = os.cpu_count()

        # Получаем архитектуру процессора через platform.machine()
        # Возвращает например "x86_64", "aarch64", "i386" и т.д.
        architecture = platform.machine()

        # Получаем информацию о загрузке системы из /proc/loadavg
        # Формат файла: "1.23 0.45 0.67 1/123 12345" - средняя загрузка за 1, 5, 15 минут
        with open('/proc/loadavg', 'r') as f:
            # Читаем файл, разбиваем на части и берем первые 3 значения (загрузка за 1,5,15 мин)
            load_avg = f.read().strip().split()[:3]

        # Возвращаем кортеж с информацией о процессоре
        return processor_count, architecture, load_avg
    except Exception as e:
        # Если произошла ошибка, возвращаем None
        return None


def get_mounts_info():
    """
    Получает информацию о смонтированных файловых системах
    Читает /proc/mounts и использует statvfs для получения статистики использования
    """
    mounts = []  # Создаем пустой список для хранения информации о точках монтирования

    try:
        # Читаем файл /proc/mounts который содержит информацию о всех смонтированных ФС
        with open('/proc/mounts', 'r') as f:
            # Читаем файл построчно
            for line in f:
                parts = line.split()  # Разбиваем строку по пробелам
                if len(parts) >= 4:  # Проверяем, что строка содержит достаточно полей
                    # Извлекаем информацию из полей: устройство, точка_монтирования, тип_ФС
                    device, mount_point, fs_type = parts[0], parts[1], parts[2]

                    # Пропускаем специальные файловые системы которые не представляют интереса
                    special_fs = ['/proc', '/sys', '/dev', '/run', '/tmp']
                    # Проверяем, начинается ли точка монтирования с любого из специальных префиксов
                    if any(mount_point.startswith(fs) for fs in special_fs):
                        continue  # Пропускаем эту файловую систему

                    try:
                        # Используем os.statvfs для получения статистики файловой системы
                        # statvfs возвращает информацию о свободном/общем месте на ФС
                        stat = os.statvfs(mount_point)
                        # Вычисляем общий объем: количество блоков * размер блока
                        total_bytes = stat.f_blocks * stat.f_frsize
                        # Вычисляем свободный объем: количество свободных блоков * размер блока
                        free_bytes = stat.f_bfree * stat.f_frsize

                        # Конвертируем байты в гигабайты (деление на 1024^3)
                        total_gb = total_bytes // (1024 * 1024 * 1024)
                        free_gb = free_bytes // (1024 * 1024 * 1024)

                        # Добавляем информацию о точке монтирования в список
                        mounts.append((mount_point, fs_type, free_gb, total_gb))
                    except:
                        # Если не удалось получить статистику (нет прав доступа и т.д.), пропускаем
                        continue
    except Exception as e:
        # Если произошла ошибка при чтении /proc/mounts, просто продолжаем
        pass

    # Возвращаем список с информацией о всех точках монтирования
    return mounts


def get_user_and_host_info():
    """
    Получает информацию о текущем пользователе и имени хоста
    """
    try:
        # Получаем имя текущего пользователя
        # os.getlogin() возвращает имя пользователя, вошедшего в систему
        user_name = os.getlogin()
    except:
        # Если не удалось получить имя пользователя, используем значение по умолчанию
        user_name = "Неизвестно"

    try:
        # Получаем имя хоста (компьютера)
        # platform.node() возвращает сетевое имя хоста
        host_name = platform.node()
    except:
        # Если не удалось получить имя хоста, используем значение по умолчанию
        host_name = "Неизвестно"

    # Возвращаем кортеж с именем пользователя и хоста
    return user_name, host_name


def main():
    """
    Основная функция программы для Linux
    Организует сбор и отображение всей системной информации
    """
    # Выводим заголовок программы
    print("=" * 50)  # Печатаем разделительную строку
    print("СИСТЕМНАЯ ИНФОРМАЦИЯ - LINUX")
    print("=" * 50)

    # 1. Получаем и выводим информацию об операционной системе и ядре
    distro_info, kernel_version = get_os_info()  # Получаем информацию об ОС
    print(f"ОС: {distro_info}")  # Выводим название дистрибутива
    print(f"Ядро: Linux {kernel_version}")  # Выводим версию ядра

    # 2. Получаем и выводим информацию о пользователе и хосте
    user_name, host_name = get_user_and_host_info()  # Получаем информацию о пользователе и хосте
    print(f"Имя хоста: {host_name}")  # Выводим имя хоста (компьютера)
    print(f"Пользователь: {user_name}")  # Выводим имя пользователя

    # 3. Получаем и выводим информацию о процессоре
    processor_info = get_processor_info()  # Получаем информацию о процессоре
    if processor_info:  # Проверяем, что данные получены успешно
        # Распаковываем кортеж с информацией о процессоре
        processor_count, architecture, load_avg = processor_info
        print(f"Архитектура: {architecture}")  # Выводим архитектуру процессора
        print(f"Процессоры: {processor_count}")  # Выводим количество процессоров
        # Выводим среднюю загрузку за 1, 5 и 15 минут, объединяя значения через запятую
        print(f"Средняя нагрузка: {', '.join(load_avg)}")

    # 4. Получаем и выводим информацию о памяти
    memory_info = get_memory_info()  # Получаем информацию о памяти
    if memory_info:  # Проверяем, что данные получены успешно
        # Распаковываем кортеж с информацией о памяти
        mem_total_mb, mem_available_mb, swap_total_mb, swap_free_mb, vmalloc_total_mb = memory_info
        # Выводим информацию об оперативной памяти
        print(f"Оперативная память: {mem_available_mb} МБ свободно / {mem_total_mb} МБ всего")
        # Выводим информацию о разделе подкачки (swap)
        print(f"Раздел подкачки: {swap_total_mb} МБ всего / {swap_free_mb} МБ свободно")
        # Если доступна информация о виртуальной памяти, выводим ее
        if vmalloc_total_mb > 0:
            print(f"Виртуальная память: {vmalloc_total_mb} МБ")

    # 5. Получаем и выводим информацию о дисках
    print("\nДиски:")  # Печатаем заголовок для раздела дисков
    mounts_info = get_mounts_info()  # Получаем информацию о смонтированных файловых системах
    # Проходим по всем точкам монтирования в цикле
    for mount_point, fs_type, free_gb, total_gb in mounts_info:
        # Для каждой точки монтирования выводим информацию в формате:
        # /home ext4 40 ГБ свободно / всего 100 ГБ
        print(f" {mount_point} {fs_type} {free_gb} ГБ свободно / всего {total_gb} ГБ")


# Стандартная конструкция для Python: код выполняется только если скрипт запущен напрямую
if __name__ == "__main__":
    try:
        main()  # Вызываем основную функцию
    except Exception as e:
        # Если произошла непредвиденная ошибка, выводим сообщение и завершаем программу
        print(f"Произошла ошибка: {e}")
        sys.exit(1)  # Завершаем программу с кодом возврата 1 (ошибка)