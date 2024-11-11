#!/usr/bin/env bash

echo "Installing development dependency"
pip install -U tox tox-pip-version tox-pyenv-redux
pip install -U sphinx myst-parser sphinx-rtd-theme twine


# This python versions is used for testing
PYTHON_VERSIONS=("3.7" "3.8" "3.9" "3.10")
for version in "${PYTHON_VERSIONS[@]}"; do
  if ! pyenv versions --bare | grep -q "^${version}"; then
    echo "Python ${version} is not installed. Installing now..."
    pyenv install "${version}"
  else
    echo "Python ${version} is already installed."
  fi
done

echo "Python installation check completed."

echo "Installing development dependencies"
tox --devenv .venv
echo "Finished installing development dependencies."


source .venv/bin/activate

