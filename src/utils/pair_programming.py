import csv
from dataclasses import dataclass
import random


@dataclass
class Developer:
    name: str
    slack_id: str
    projects: list

def read_developers():
    l = list()
    with open('./data/developers.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count != 0:  # skip cvs head
                l.append(Developer(row[0], row[1], [row[2]]))
            line_count += 1
    return tuple(l)


developers = read_developers()

# mapping project / developer
developers_for_project = {}
for d in developers:
    for p in d.projects:
        if p not in developers_for_project:
            developers_for_project[p] = []
        if d not in developers_for_project[p]:
            developers_for_project[p].append(d)


def get_pair_programming_message():
    # make pairs using the number of week in the current year
    msg = 'It would be nice if you take about 2 hours a week for <https://martinfowler.com/articles/on-pair-programming.html|pair programming>\n'
    msg += '\n> the best programs and designs are done by pairs, because you can criticise each other, and find each others errors, and use the best ideas\n'
    msg += '\nhere the weekly advice (`*r` means randomly picked)'
    msg += '\n'
    for p in developers_for_project.keys():
        if len(developers_for_project[p]) > 1:
            msg += '\n*%s* pairs\n' % p
            devs = developers_for_project[p][:]
            random.shuffle(devs)
            while len(devs) > 0:
                pair_1 = devs[0]
                del devs[0]
                is_random = False
                # this happens when the team is odd
                if len(devs) == 0:
                    is_random = True
                    # pick it randomly
                    devs_clone = list(
                        filter(lambda d: d.name != pair_1.name, developers_for_project[p][:]))
                    random.shuffle(devs_clone)
                    pair_2 = devs_clone[0]
                else:
                    pair_2 = devs[0]
                    del devs[0]
                msg += '- %s / %s%s\n' % (pair_1.name,
                                          pair_2.name, '(*r)' if is_random else '')
    msg += '\n:movie_camera: remember to <https://drive.google.com/drive/folders/1D7eYdI01lCV-43GJXFR658Geba16xqTB?usp=sharing|record your programming session>\n> Share your knowledge. It is a way to achieve immortality.\n'
    return msg
