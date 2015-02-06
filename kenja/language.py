extension_dict = {'java': ['.java'], 'python': ['.py']}


def is_target_blob(blob):
    if not blob:
        return False

    for exts in extension_dict.values():
        for ext in exts:
            if blob.name.endswith(ext):
                return True
    return False
