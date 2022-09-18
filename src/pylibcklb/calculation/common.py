def get_size(bytes_in, suffix="B") -> str:
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T"]:
        if bytes_in < factor:
            return f"{bytes_in:.2f}{unit}{suffix}"
        bytes_in /= factor
