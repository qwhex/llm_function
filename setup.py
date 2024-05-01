from setuptools import setup, find_packages


def load_requirements(req_name):
    path = f'requirements/{req_name}.txt'
    with open(path) as f:
        reqs = f.read().splitlines()
    reqs = [req.strip() for req in reqs]
    reqs = [req for req in reqs if req]
    return reqs


extra_requires = {
    'mistral': load_requirements('mistral'),
    'openai': load_requirements('openai'),
    'local_api': load_requirements('local_llm'),
}

setup(
        name="llm_function",
        version="0.1",
        packages=find_packages(),
        install_requires=load_requirements('common'),
        tests_require=load_requirements('dev'),
        extras_require=extra_requires,
        # Metadata
        author="Mice Pápai",
        author_email="hello@micepapai.com",
        description="Package LLM prompts, IO schemas, validators and fitness fns into reusable Python functions",
        long_description=open('README.md').read(),
        long_description_content_type='text/markdown',
        url="https://github.com/yourgithub/mylib",
)
