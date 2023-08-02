#!/usr/bin/env python
import yaml


# Get packages in requirements.txt
packages = {}
for package in open('requirements.txt'):
    # Skip header
    if package[0] == '#':
        continue
    # Split package information and populate package dict.
    packages[package.strip()] = {
        'requirements': True,
        'yaml': False
        }

# Fix the absence of double quotes to allow importing in yaml module.
indata = [
    line.replace(' {{ ', ' "{{ ').replace(' }}\n', ' }}"\n')
    for line in open('conda/meta.yaml').readlines()
    ]
indata = ''.join(indata)
# Now load the meta.yaml
yaml_data = yaml.safe_load(indata)

# Compare the yaml packages with the packages in requirements.txt
for package in yaml_data['requirements']['run']:
    # Split package information.
    if package in packages:
        packages[package]['yaml'] = True
    else:
        packages[package] = {'requirements': False, 'yaml': True}

# Check missing packages.
missing = 0
for package, entries in packages.items():
    if not entries['yaml']:
        print(
            f'ERROR: {package} is in requirements.txt but not in conda/meta.yaml'
            )
        missing = True
    if not entries['requirements']:
        print(
            f'ERROR: {package} is in conda/meta.yaml but not in requirements.txt'
            )
        missing = True

# Print message and with code 1 if missing/mismatching packages
if missing == 0:
    print('No mismatching packages found.')
exit(int(missing))
