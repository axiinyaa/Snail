def generate_progress_bar(length: int, max_value: float, current_value: float) -> str:

    emojis = {
        'empty': {
            'a': '<:progress_left_empty:1410756998626152580>',
            'b': '<:progress_middle_empty:1410756985305038888>',
            'c': '<:progress_right_empty:1410756975326662676>'
        },
        'filled': {
            'a': '<:progress_left_filled:1410756954393149490>',
            'b': '<:progress_middle_filled:1410756941990330388>',
            'c': '<:progress_right_filled:1410756964849549373>'
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