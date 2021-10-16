
import functools
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from conda.models import version as cv
import json

@dataclass
class Constraint:
    dependency: Optional[
        str
    ]  # Name of dependency that requires the conflicting package
    versions: cv.VersionSpec  # List of versions for the conflicting package


@dataclass
class ConstraintGroup:
    name: str  # Name of conflicting package
    constraints: List[Constraint]

    def merge(self) -> cv.VersionSpec:
        return functools.reduce(
            lambda v1, v2: v1.merge(v2), (c.versions for c in self.constraints)
        )


def parse_conflicts(conflicts: str) -> List[ConstraintGroup]:
    # groups separated by blank line
    return [_parse_group(group) for group in conflicts.split("\n\n")]


def _parse_group(group: str) -> ConstraintGroup:
    groupname = re.compile(r"Package (\S+) conflicts for:")
    lines = group.split("\n")
    # first line gives name
    match = groupname.match(lines[0])
    name = match and match.group(1)
    # look for versions in subsequent lines
    return ConstraintGroup(
        name, [c for c in (_parse_line(name, line) for line in lines[1:] if line) if c]
    )


def _parse_line(name: str, line: str) -> Constraint:
    versionre = re.compile(r"(?:(\S+) .*)?" + name + r"(?:\[version='([^']+)'[],])?")
    match = versionre.match(line)
    if match:
        dep = match.group(1)
        spec = match.group(2)
        if spec is None:
            return None
        versions = cv.VersionSpec(spec)
        return Constraint(dep, versions)
    else:
        logging.warning(f"Unable to parse {name} version in: {line!r}")
        return None


class result:

    def __init__(self,conflicts):
        self.conflicts=conflicts

    def manual_solver(self):
        
        self.result={}
        """
        i - iterator of parsed lists
        """

        for i in range(len(self.conflicts)):
            # print(i)
            if self.conflicts[i].name is not None:
                self.result[self.conflicts[i].name]={}
                
                print("########")
                print(f"{i} - {self.conflicts[i].name}")
                print("-----------")
                print("")

                if self.conflicts[i].constraints:
                    valid=False
                    while valid is False:
                        for constraint in self.conflicts[i].constraints:
                            print(constraint.dependency)
                            print(constraint.versions)
                        print("-")
                        print("merged: ")
                        print(self.conflicts[i].merge())
                        value=input(f"Enter value for {self.conflicts[i].name}: ")
                        if self.conflicts[i].merge().match(value):
                            print()
                            print(f"Solution: {value}")
                            print("")
                            print("")
                            valid=True
                        else:
                            print("Wrong value")
                
                else:
                    print("Empty")
                    value = "NA"
                
                self.result[self.conflicts[i].name]["value"]=value
                self.result[self.conflicts[i].name]["conflicting libs"]=[
                    self.conflicts[i].constraints[ii].dependency for ii in range(len(self.conflicts[i].constraints))]


with open("conflicts.txt","r") as f:
    conflictstr = f.read()
conflicts = parse_conflicts(conflictstr)


r=result(conflicts)
r.manual_solver()
r.result
with open("result.json","wb") as f:
    json.dump(r.result,f)





