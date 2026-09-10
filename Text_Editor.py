def Normalize_Persian(text):
    """
    Normalize Persian text by replacing Arabic characters with their Persian equivalents,
    converting zero-width non-joiners to spaces, and removing extra whitespaces.
    """
    
    # Replace Arabic Yeh (ي) with Persian Yeh (ی)
    text = text.replace("ي", "ی")

    # Replace Arabic Kaf (ك) with Persian Kaf (ک)
    text = text.replace("ك", "ک")

    # Replace zero-width non-joiner ( نیم‌فاصله ) with a standard space
    text = text.replace("\u200c", " ")

    # Remove leading and trailing whitespaces
    return text.strip()