def is_valid_ip(parser_ref, x: str):
    if x.__contains__(":"):
        ip, port = x.split(":")
    else:
        ip = x
        port = None
    ip_partials = ip.split(".")
    if len(ip_partials) != 4:
        parser_ref.error("IP must have 4 parts")
    for y in ip_partials:
        if not (0 <= int(y) <= 255):
            parser_ref.error("IP parts must be between 0 and 255")
    if port and not 0 <= int(port) <= 65535:
        parser_ref.error("Port must be between 0 and 65535")
    return x