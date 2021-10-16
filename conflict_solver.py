import functools
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from conda.models import version as cv

@dataclass
class Constraint:
    def __init__(self):
        self.dependency: Optional[
            str
        ]  # Name of dependency that requires the conflicting package
        self.versions: cv.VersionSpec  # List of versions for the conflicting package


@dataclass
class ConstraintGroup:
    def __init__(self):
        self.name: str  # Name of conflicting package
        self.constraints: List[Constraint]
        return self.constraints

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

        for i in range(len(self.conflicts)):
            # print(i)
            if self.conflicts[i].name is not None:
                self.result[self.conflicts[i].name]={}
                
                print("########")
                print(f"{self.conflicts[i].name}")
                print("-----------")
                print("")

                # if self.conflicts[i].merge is not None:
                #     print(self.conflicts[i].merge())
                # else:
                #     print("No results from merge")
                


if __name__=="__main__":
    with open("conflicts.txt","r") as f:
        conflictstr = f.read()
    conflicts = parse_conflicts(conflictstr)
    print(conflicts)
    # r=result(conflicts)
    # r.manual_solver()


