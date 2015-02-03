supported_languages = ['java']

extension_dict = {'java': ['.java']}

def is_target_blob(blob):
    if not blob:
        return False

    for language in supported_languages:
        if language in extension_dict:
            for ext in extension_dict[language]:
                if blob.name.endswith(ext):
                    return True
    return False
