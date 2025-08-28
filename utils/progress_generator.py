def generate_progress_bar(length: int, max_value: float, current_value: float) -> str:

    emojis = {
        'empty': {
            'a': '<:progress_left_empty:1410773890757820426>',
            'b': '<:progress_middle_empty:1410773880045309952>',
            'c': '<:progress_right_empty:1410773870042022010>'
        },
        'filled': {
            'a': '<:progress_left_filled:1410773849338810540>',
            'b': '<:progress_middle_filled:1410773837091700806>',
            'c': '<:progress_right_filled:1410773859145355336>'
        }
    }

    filled = round((current_value / max_value) * length)

    progress_bar = ''

    for i in range(length):

        part = '?'

        if i == 0:
            part = 'a'
        elif i == length - 1:
            part = 'c'
        else:
            part = 'b'

        if i < filled:
            progress_bar += emojis['filled'][part]
        else:
            progress_bar += emojis['empty'][part]

    return progress_bar