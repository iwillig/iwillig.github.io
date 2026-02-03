from setuptools import setup

setup(
    name="lektor-plantuml",
    version="0.1.0",
    author="Ivan Willig",
    description="Lektor plugin to render PlantUML diagrams in markdown",
    py_modules=["lektor_plantuml"],
    install_requires=["requests"],
    entry_points={
        "lektor.plugins": [
            "plantuml = lektor_plantuml:PlantUMLPlugin",
        ]
    },
)
