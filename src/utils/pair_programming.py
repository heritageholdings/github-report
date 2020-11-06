from dataclasses import dataclass
import random


@dataclass
class Developer:
	name: str
	slack_id: str
	projects: list


project = "Developers"
# new developers should be added at the END of this list
developers = (Developer("Matteo Boschi", "", [project]),
              Developer("Cristiano Tofani", "", [project]),
              Developer("Fabrizio Filizola", "", [project]),
              Developer("Simone Biffi", "", [project]),
              Developer("Giovanni Mancini", "", [project]),
              # Developer("Danilo Spinelli", "", [project]),
              Developer("Emanuele De Cupis", "", [project]),
              Developer("Pasquale De Vita", "", [project]),
              Developer("Vito Falco", "", [project]),
              Developer("Pasquale Spica", "", [project]),
              Developer("Alessio Dore", "", [project]),
              # Developer("Francesco Persico", "", [project]),
              Developer("Simone Infante", "", [project]),
              Developer("Daniele Manni", "", [project]))

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
					devs_clone = list(filter(lambda d: d.name != pair_1.name, developers_for_project[p][:]))
					random.shuffle(devs_clone)
					pair_2 = devs_clone[0]
				else:
					pair_2 = devs[0]
					del devs[0]
				msg += '- %s / %s%s\n' % (pair_1.name, pair_2.name, '(*r)' if is_random else '')
	msg += '\n:movie_camera: remember to <https://drive.google.com/drive/folders/1D7eYdI01lCV-43GJXFR658Geba16xqTB?usp=sharing|record your programming session>\n> Share your knowledge. It is a way to achieve immortality.\n'
	return msg
