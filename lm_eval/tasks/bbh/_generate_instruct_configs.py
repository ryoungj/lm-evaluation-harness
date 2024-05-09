import os
import yaml
import shutil

# def custom_constructor(loader, node):
#     value = loader.construct_scalar(node)
#     return value

# # Register the custom constructor for tags that start with '!function'
# yaml.SafeLoader.add_constructor(u'!function', custom_constructor)


# # Step 1: Define a constructor function for the '!function' tag
# def my_custom_function_constructor(loader, node):
#     if isinstance(node, yaml.MappingNode):
#         # Handle mapping nodes
#         value = loader.construct_mapping(node)
#     elif isinstance(node, yaml.ScalarNode):
#         # Handle scalar nodes
#         value = loader.construct_scalar(node)
#     else:
#         # Handle other types as needed, or raise an error
#         raise ValueError("Unsupported YAML node type")
#     return CustomFunction(value)

# # Step 2: Register the constructor with the '!function' tag
# yaml.add_constructor('!function', my_custom_function_constructor, yaml.SafeLoader)

# # Step 1: Define a custom data structure (optional if you use a basic type like dict)
# class CustomFunction:
#     def __init__(self, data):
#         self.data = data

# # Step 2: Create a custom representer function
# def custom_function_representer(dumper, data):
#     # Convert the object back to the original dictionary representation for dumping
#     node = dumper.represent_mapping('!function', data.data)
#     return node

# # Step 3: Register the custom representer with the dumper
# yaml.add_representer(CustomFunction, custom_function_representer, Dumper=yaml.SafeDumper)


# def function_constructor(loader, node):
#     if isinstance(node, yaml.MappingNode):
#         # If the node is a mapping, we construct a mapping.
#         value = loader.construct_mapping(node)
#     elif isinstance(node, yaml.ScalarNode):
#         # If the node is a scalar, we just return its value.
#         value = loader.construct_scalar(node)
#     elif isinstance(node, yaml.SequenceNode):
#         # If the node is a sequence, we construct a list.
#         value = loader.construct_sequence(node)
#     else:
#         value = None  # Or handle other types as needed.
#     return {'function': value}

# # Register the custom constructor
# yaml.add_constructor('!function', function_constructor, yaml.SafeLoader)

# def universal_representer(dumper, data):
#     # Check if the data is the specific type we're interested in
#     if isinstance(data, dict) and 'function' in data:
#         # Handle the special case with '!function' tag
#         return dumper.represent_mapping('!function', data['function'], flow_style=False)
#     else:
#         # Fallback for any other type of data
#         return dumper.represent_data(data)

# # Apply the universal representer to all objects
# yaml.add_representer(object, universal_representer, Dumper=yaml.SafeDumper)


class FunctionTag:
    def __init__(self, value):
        self.value = value

# Custom Loader for '!function'
def function_constructor(loader, node):
    # Directly return a FunctionTag object with the scalar value
    return FunctionTag(loader.construct_scalar(node))

yaml.add_constructor('!function', function_constructor, Loader=yaml.SafeLoader)

# Custom Dumper for FunctionTag objects
def function_representer(dumper, obj):
    # Represent the FunctionTag object using the '!function' tag and its scalar value
    return dumper.represent_scalar('!function', obj.value)

yaml.add_representer(FunctionTag, function_representer, Dumper=yaml.SafeDumper)

dir_map = {
    "cot_fewshot": "cot_fewshot_instruct",
    "fewshot": "fewshot_instruct",
}

new_suffix = "instruct"

for orig_dir, new_dir in dir_map.items():
    os.makedirs(new_dir, exist_ok=True)

    # iterate over files in the original directory
    for file in os.listdir(orig_dir):
        if not os.path.isfile(f"{orig_dir}/{file}"):
            continue

        if file.endswith(".py"):
            shutil.copy(f"{orig_dir}/{file}", new_dir)
            continue
            

        with open(f"{orig_dir}/{file}", "r") as f:
            content = yaml.safe_load(f)
        
        if "group" in content:
            if not isinstance(content["group"], list):
                content["group"] = [content["group"]]
            content["group"] = [f"{g}_{new_suffix}" for g in content["group"]]

        if "task" in content:
            content["task"] = f"{content['task']}_{new_suffix}"

        if "include" in content:
            content["include"] = content["include"].replace("_template", f"_{new_suffix}_template")

        if "description" in content:
            if orig_dir == "fewshot":
                content["description"] = content["description"].strip() + "\nAnswer the final question and format your answer as the following examples. Directly answer the question, do not output any additional reasoning.\n\n"
            elif orig_dir == "cot_fewshot":
                content["description"] = content["description"].strip() + "\nAnswer the final question and format your answer as the following examples.\n\n"
            else:
                raise ValueError(f"Unknown directory: {orig_dir}")

        if not file.endswith(".yaml"):
            assert "_template" in file
            file = file.replace("_template", f"_{new_suffix}_template")

        with open(f"{new_dir}/{file}", "w", encoding="utf-8") as f:
            yaml.safe_dump(
                content, f, sort_keys=False, 
                width=float("inf"),
                default_flow_style=False,
                allow_unicode=True,
                default_style='"'
            )