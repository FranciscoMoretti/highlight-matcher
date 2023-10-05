def find_substrings_sequence(long_string, substrings):
    start = 0
    for substring in substrings:
        start_pos = long_string.find(substring, start)
        if start_pos == -1:
            # If the substring is not found, stop the generator
            break
        end_pos = start_pos + len(substring)
        yield start_pos, end_pos
        start = end_pos + 1
