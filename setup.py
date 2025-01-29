from setuptools import setup, find_packages

setup(
    name='supershell',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'Click',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'supershell=supershell.cli:cli',
        ],
    },
    package_data={
        'supershell.agent': ['prompts/*.md'],
    },
    author='justdark',
    author_email='justdark@example.com',
    description='智能 Shell 命令行工具',
)