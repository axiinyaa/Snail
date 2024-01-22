def dict_to_dataclass(data_class, data_dict):
    field_types = {f.name: f.type for f in data_class.__dataclass_fields__.values()}
    data_instance = data_class()

    for key, value in data_dict.items():
        if key in field_types:
            field_type = field_types[key]
            if hasattr(field_type, '__origin__') and field_type.__origin__ is list:
                # Handle nested lists
                inner_type = field_type.__args__[0]
                setattr(data_instance, key, [dict_to_dataclass(inner_type, item) for item in value])
            elif hasattr(field_type, '__dataclass_fields__'):
                # Handle nested data classes
                setattr(data_instance, key, dict_to_dataclass(field_type, value))
            else:
                setattr(data_instance, key, value)

    return data_instance