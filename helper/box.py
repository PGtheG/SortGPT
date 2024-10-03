def get_box_by_color(color):
    if color is not None:
        color = str.lower(color)

    if color == 'red':
        print(f"Search for box nr: 1")
        return 1
    if color == 'yellow':
        print(f"Search for box nr: 2")
        return 2
    if color == 'green':
        print(f"Search for box nr: 3")
        return 3
    if color == 'blue':
        print(f"Search for box nr: 4")
        return 4
    else:
        print(f"Search for box nr: 0")
        return 0