UNIT_TO_ML = {
    'ml': 1,
    'oz': 29.5735,
    'tbsp': 14.7868,
    'tsp': 4.92892,
    'dash': 0.616115,
}


def to_ml(quantity, unit='ml'):
    if unit not in UNIT_TO_ML:
        raise ValueError(f"Unknown unit: {unit}")
    return quantity * UNIT_TO_ML[unit]


FRACTIONAL_UNITS = {
    '⅛': 0.125,
    '¼': 0.25,
    '⅓': 0.333333,
    '½': 0.5,
    '⅔': 0.666667,
    '¾': 0.75,
    '1/8': 0.125,
    '1/4': 0.25,
    '1/3': 0.333333,
    '1/2': 0.5,
    '2/3': 0.666667,
    '3/4': 0.75,
}


UNIT_ALIAS = {
    'ml': 'ml',
    'milliliter': 'ml',
    'milliliters': 'ml',
    'oz': 'oz',
    'ounce': 'oz',
    'ounces': 'oz',
    'tbsp': 'tbsp',
    'tablespoon': 'tbsp',
    'tablespoons': 'tbsp',
    'tsp': 'tsp',
    'teaspoon': 'tsp',
    'teaspoons': 'tsp',
    'dash': 'dash',
    'dashes': 'dash',
    'piece': 'piece',
    'pieces': 'piece',
    'whole': 'piece',
    'slice': 'piece',
    'slices': 'piece',
    'twist': 'piece',
    'cube': 'piece',
    'sprig': 'piece',
    'part': 'piece',
    'parts': 'piece',
    'drop': 'piece',
    'pinch': 'piece',
}  


def normalize_unit(text):

    if not text or not str(text).strip():
        raise ValueError("Unit cannot be empty or None")
    cleaned_text = str(text).strip().lower()
    for char, value in FRACTIONAL_UNITS.items():
        if char in cleaned_text:
            cleaned_text = cleaned_text.replace(char, str(value))
    quantity = 0.0
    found_number = False
    unit_words = []
    for token in cleaned_text.split():
        if '/' in token:
            numerator, denominator = token.split('/')
            quantity += float(numerator) / float(denominator)
            found_number = True
            continue
        try:
            quantity += float(token)
            found_number = True
        except ValueError:
            unit_words.append(token)
    if not found_number:
        quantity = 1.0
    if not unit_words:
        return quantity, 'piece'
    unit = ' '.join(unit_words)
    if unit not in UNIT_ALIAS:
        raise ValueError(f"Unknown unit: {unit}")
    return quantity, UNIT_ALIAS[unit]


    