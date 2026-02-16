def transform_command(command_list): #Converts a multi-line command into a single-line command
    if len(command_list) >= 3 and command_list[0] == "sh" and command_list[1] == "-c":
        script_lines = command_list[2].split("\n")
        cleaned_script = " ".join(line.strip() for line in script_lines if line.strip())
        return ["sh", "-c", cleaned_script]
    return command_list


def lowercase_keys(data):
    """Recursively converts the first letter of each dictionary key to lowercase."""
    if isinstance(data, dict):
        return {k[:1].lower() + k[1:]: lowercase_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [lowercase_keys(item) for item in data]
    else:
        return data  # Return unchanged if not a dict or list