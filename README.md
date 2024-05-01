# llm_function

The `llm_function` library streamlines the creation of LLM prompt templates, schemas, validators, and fitness functions, making them reusable across various projects.

> Experimental! Work in progress.

## Usage

Define the prompt template (jinja2 + markdown)

```markdown
Answer the following question as concisely as possible, while still including every important piece of information.
Include the source of the information if possible.
The answer shouldn't be longer than a few sentences.

Question:
"[[question]]"
```

Define the function (schema)

```python
schema = {
    "args": {
        "question": v.str,
    },
    "response": {
        # you can define custom validators, e.g. "validate bash syntax"
        "validate": v.str
    }
}

# define the llm function
answer_concisely = create_llm_fn(
        template_path='answer_concisely.md',
        schema=schema,
        fitness=lambda resp: -1 * len(resp),  # the shorter, the better
)

# define the provider
provider = LlamaCppProvider(model_path='models/Phi-3-mini-4k-instruct-q4.gguf')

# use the function
questions = [
    "1+1=2. Why not 3?",
    "Why can't we tell whether someone has a consciousness?",
]
for question in questions:
    # print all generated answers, starting with the best one
    for response in answer_concisely({'question': question}, provider=provider, k=3):
        print(response)
```

### JSON Schema Example

Create an appropriate prompt template. We recommend specifying a Typescript type for the expected response.

```markdown
Generate a user profile for a fictional person.
Description: [[description]]

Follow the Typescript type below.

type UserProfile = {
id: string;
username: string;
age: number;
gender: "male" | "female" | "other";
interests: string[];
};

Answer with only JSON.
```

Define the JSON Schema under `schema.response.json_schema` 
When using the llama.cpp provider, the generation will be constrained to this schema.
For all providers the response will be validated.
You can define a custom validator which will be ran on the parsed, schema-validated response object.

```python
schema = {
    "args": {
        "description": v.str
    },
    "response": {
        "json_schema": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "format": "uuid"
                },
                "username": {
                    "type": "string",
                    "minLength": 3,
                    "maxLength": 20,
                    "pattern": "^[a-zA-Z0-9_]*$"
                },
                "age": {
                    "type": "integer",
                    "minimum": 18,
                    "maximum": 120
                },
                "gender": {
                    "type": "string",
                    "enum": ["male", "female", "other"]
                },
                "interests": {
                    "type": "array",
                    "items": {"type": "string"}
                },
            },
            "required": ["id", "username", "age", "gender"]
        },
        # you can define a custom validator for the parsed JSON below:
        "validator": some_custom_validator
    }
}

# define the llm function
generate_user_profile = create_llm_fn(
        template_path='user_profile.md',
        schema=schema,
)
```

## Authors

```
All Rights Reserved
Copyright (c) 2024 Mice Pápai
```
