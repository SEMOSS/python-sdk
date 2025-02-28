# DEV INSTRUCTIONS

## Installation
When working with the project, you should create a **virtual environment** to install the dependencies in the `ai-server` directory. 

### PYTHON

```
python -m venv venv
venv\Scripts\activate
```

### Install the dependencies:

Navigate to the src directory and run the following command:
```
pip install -r requirements-dev.txt
```
If you have a problem with the installation, you can try to install the dependencies one by one.

### Install the package in editable mode:

Navigate to the src directory and run the following command:
```
pip install -e .
```
This will allow you to make changes to the package and have them reflected in your environment without having to reinstall the package.

## VSCode Setup

1. Install the Python extension for VSCode.
2. Install the Python Debugger Extension for VSCode.
3. Install Pylance for VSCode.
4. Install Ruff for VSCode.
5. Set your Python interpreter to the virtual environment you created.
6. To run notebooks inside of VSCode you can install the Jupyter extension. (Optional)

## Running Scripts

The .vscode/settings.json file allows you to execute scripts directly inside of VSCode. Make sure to set your Python interpreter to the virtual environment you created. Then, with a file open, you can use the play button to run the script.

## Best Practices
- Create a new branch for each feature or bug fix.
- Use absolute imports when importing from the `ai_server` package.
- Turn Ruff extension on and fix warnings before making a pull request.
- Run unit tests before making a pull request. (See TESTING.md for instructions)
- Update requirements-dev.txt, pyproject.toml, and setup.py if you add new dependencies.



