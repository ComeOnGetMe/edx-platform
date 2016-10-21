from setuptools import setup

setup(
    name="sandbox-packages",
    version="0.2.85",
    packages=[
        "loncapa",
        "verifiers",
        "hint",
        "hint.hint_class_helpers",
        "hint.hint_class_helpers.expr_parser",
        "hint.hint_class",
        "hint.hint_class.first_Universal",
        "hint.hint_class.last_Universal",
        "hint.hint_class.Week2",
        "hint.hint_class.Week3",
        "hint.hint_class.Week4",
        "hint.hint_class.Week5",
        "hint.hint_class.Week6",
        "hint.hint_class.Week7",
        "hint.hint_class.Week8",
        "hint.hint_class.Week9"
    ],
    py_modules=[
        "eia",
    ],
    install_requires=[
    "MySQL-python",
    ],
)
