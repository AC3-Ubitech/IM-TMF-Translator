import yaml

def load_yaml(file_path): # load yaml file
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def save_yaml(data, file_path): #save yaml file
    with open(file_path, 'w') as file:
        yaml.dump(data, file, default_flow_style=False, sort_keys=False)


# def save_yaml(data, file_path):
#     """Save data to a YAML file, post-process to quote strings."""
#     with open(file_path, 'w') as file:
#         yaml.dump(data, file, default_flow_style=False, sort_keys=False)
#
#     # Post-process the YAML file to add quotes around all strings
#     with open(file_path, 'r') as file:
#         yaml_content = file.read()
#
#     # Replace unquoted strings with quoted strings
#     yaml_content = re.sub(r'(\w+):', r'"\1":', yaml_content)
#
#     # Write the corrected YAML back to the file
#     with open(file_path, 'w') as file:
#         file.write(yaml_content)
