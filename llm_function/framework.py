import json
import logging
from typing import Callable, Dict, Any

import jsonschema
from jinja2 import Environment, BaseLoader, Template

from llm_function.common.util import spread, deep, json_print, extract_json
from llm_function.providers import Provider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Jinja2 Environment
JINJA_ENV = Environment(loader=BaseLoader(), block_start_string='[%', block_end_string='%]',
                        variable_start_string='[[', variable_end_string=']]')


def load_template(template_path: str) -> Callable[[Dict[str, Any]], str]:
    """
    Loads a Jinja2 template from the specified directory.

    :param template_path: The path to the markdown template.
    :return: A function that takes a dictionary of arguments and returns the rendered template.
    """
    try:
        with open(template_path, encoding='utf-8') as file:
            content = file.read()
            jinja_template: Template = JINJA_ENV.from_string(content)
    except FileNotFoundError:
        logger.error(f"Template file not found: {template_path}")
        raise

    def template_fn(kwargs: Dict[str, Any]) -> str:
        return jinja_template.render(**kwargs)

    return template_fn


def validate_args(args, schema):
    """
    Validates the given arguments against the schema. Raises ValueError if validation fails.

    :param args: The raw value to validate.
    :param schema: The schema to validate against.
    :return: The validated / extracted value.
    """
    if isinstance(schema, dict):
        validated_data = {}
        for key, sub_schema in schema.items():
            validated_data[key] = validate_args(args.get(key), sub_schema)
        return validated_data
    else:
        return schema(args)


def validate_response(response, schema):
    json_schema, validate = spread(schema, ['json_schema', 'validate'])

    if json_schema:
        response = extract_json(response)
        try:
            jsonschema.validate(response, json_schema)
        except jsonschema.exceptions.ValidationError as e:
            raise ValueError(e.message)

    if validate:
        response = validate(response)

    return response


def create_llm_fn(
        template_path: str,
        schema: dict,
        fitness=None,
        provider_config: dict = None
):
    if not provider_config:
        provider_config = {}

    provider_config['json_schema'] = deep(schema, 'response.json_schema')
    json_print(provider_config)

    template_fn = load_template(template_path)

    def llm_fn(args: dict, provider: Provider, k: int = 3):
        validated_args = validate_args(args, schema["args"])
        filled_template = template_fn(validated_args)
        logger.debug(filled_template)

        # FIXME:
        responses = provider.sync_generate_responses(filled_template, k, provider_config)

        validated_responses = []
        for response in responses:
            logger.debug(f"Raw response:\n{response}\n")
            try:
                validated_responses.append(validate_response(response, schema["response"]))
                # yield validated_response
            except ValueError as e:
                logger.error(f"Invalid response skipped: {e}")
                continue

        if fitness:
            validated_responses = sorted(validated_responses, key=fitness, reverse=True)

        yield from validated_responses

    return llm_fn
