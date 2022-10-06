#!/usr/bin/env python

import json
import subprocess
import sys

with open(sys.argv[1], 'r') as fh:
    api = json.load(fh)

new_api = {
    "$schema": api["$schema"],
    "type": "Object",
    "title": "EChartsOption",
    "properties": api["option"]["properties"]
}


def clean(value):
    return value.strip("'").rstrip("'")


def iterate(array):
    for i, value in enumerate(array):
        if isinstance(value, dict):
            walk(value)
        elif isinstance(value, str):
            array[i] = clean(value)
        elif isinstance(value, list):
            iterate(value)


def walk(node):
    for key, value in node.items():
        if isinstance(value, dict):
            walk(value)
        elif isinstance(value, list):
            iterate(value)
        elif isinstance(value, str):
            node[key] = clean(value)


walk(new_api)

tmpfile = sys.argv[1] + '.clean'
with open(tmpfile, 'w') as fh:
    json.dump(new_api, fh, indent=4)

proc = subprocess.run(f"""
    datamodel-codegen
        --class-name EChartsOption
        --base-class ezcharts.plots._base.BaseModel
        --use-schema-description --reuse-model
        --input {tmpfile} --input-file-type jsonschema""".split(),
    capture_output=True)

# make some changes to the models
model = proc.stdout.decode()

laundry_list = dict(
    dataset=dict(
        find="dataset: Optional[Dataset] = Field(",
        replace="dataset: Optional[Union[List[Dataset], Dataset]] = Field("),
    grid=dict(
        find="grid: Optional[Grid] = Field(",
        replace="grid: Optional[Union[List[Grid], Grid]] = Field("),
    xaxis=dict(
        find="xAxis: Optional[XAxis] = Field(",
        replace="xAxis: Optional[Union[List[XAxis], XAxis]] = Field("),
    yaxis=dict(
        find="yAxis: Optional[YAxis] = Field(",
        replace="yAxis: Optional[Union[List[YAxis], YAxis]] = Field("),
    renderitem=dict(
        find="renderItem: Optional[RenderItem] = Field(",
        replace="renderItem: Optional[JSCode] = Field("),
    imports=dict(
        find="from __future__ import annotations",
        replace="""from __future__ import annotations\n
        from ezcharts.plots.util import JSCode"""))

for k, v in laundry_list.items():
    model = model.replace(v['find'], v['replace'])

with open("ezcharts/plots/_model.py", 'w') as fh:
    fh.write("# flake8: noqa\n")
    fh.write(model)
