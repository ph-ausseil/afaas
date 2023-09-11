import ast
import json


def to_numbered_list(
    items: list[str], no_items_response: str = "", **template_args
) -> str:
    if items:
        return "\n".join(
            f"{i+1}. {item.format(**template_args)}" for i, item in enumerate(items)
        )
    else:
        return no_items_response


def json_loads(json_str: str):
    # TODO: this is a hack function for now. Trying to see what errors show up in testing.
    #   Can hopefully just replace with a call to ast.literal_eval (the function api still
    #   sometimes returns json strings with minor issues like trailing commas).

    try:
        return ast.literal_eval(json_str)
    except ValueError as ve:
        print(f"First attempt failed: {ve}. Trying JSON.loads()")
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        try:
            print(f"JSON decode error {e}. trying literal eval")
            return ast.literal_eval(json_str)
        except Exception:
            breakpoint()
