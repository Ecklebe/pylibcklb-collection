# pylibcklb-collection

This repo allows me to play with the newer ways to package and distribute a python package.
Maybe this repo will integrate and replace the repository pylibcklb.

## How I started here
Basic requirement is a python installation. In my case Python 3.10. From there I installed PipX (1) 
with ``py -3 -m pip install --user pipx`` and adapt my PATH with ``py -3 -m pipx ensurepath``. After that I installed
Poetry
with ``py -3 -m pipx install poetry``.

## How the basic structure is created

To create the basic structure of this repository I used poetry (1) as I will use poetry also to replace
pipenv that I normally use.

## How to prepare the new structure for testing

- ``poetry add -D pytest``
- ``poetry add -D coverage[toml]``

## How to run the testing

- ``poetry install --all-extras``
- ``poetry run pytest``
- ``poetry run coverage run -m pytest && poetry run coverage combine && poetry run coverage report -m``
- ``poetry run coverage xml``
- ``poetry run coverage html``

## Linked references

(1) [pipx](https://github.com/pypa/pipx)

(2) [Poetry Basic Usage](https://python-poetry.org/docs/basic-usage/)
