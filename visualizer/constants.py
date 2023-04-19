normal = "#33691e"
unbalance = "#AA148c"
faulty = "#b71c1c"
rubbing = "#1a237e"
misalignment = "#fdd835"

num5 = "#546e7a"
num6 = "#827717"
num7 = "#f57f17"
num8 = "#01579b"
num9 = "#4e342e"

tint = {"normal": 1.0, "test": 0.8, "train": 0.5, "other": 0.2}

number_to_color_dict = {
    0: normal,
    1: rubbing,
    2: faulty,
    3: misalignment,
    4: unbalance,
}  # , 5: num5, 6: num6, 7: num7, 8: num8, 9: num9}
color_to_number_dict = {v: k for k, v in number_to_color_dict.items()}

color_to_name_dict = {
    normal: "Normal",
    unbalance: "Unbalance",
    faulty: "Faulty sensor",
    rubbing: "Rubbing",
    misalignment: "Misalignment",
}
name_to_color_dict = {v: k for k, v in color_to_name_dict.items()}

# esp
markers = ["o", "v", "D", "^", "<", "P", "*", ">", "X", "d", "s", "h"]
marker_dict = {str(i + 1): markers[i] for i in range(len(markers))}
