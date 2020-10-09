from dataclasses import dataclass
from datetime import date
import random


@dataclass
class Developer:
	name: str
	slack_id: str
	projects: list


app_project = "IO - App"
backend_project = "IO - Backend"
# new developers should be added at the END of this list
developers = (Developer("Matteo Boschi", "", [app_project]),
              Developer("Cristiano Tofani", "", [app_project]),
              Developer("Fabrizio Filizola", "", [app_project]),
              Developer("Simone Biffi", "", [app_project]),
              Developer("Giovanni Mancini", "", [app_project]),
              Developer("Danilo Spinelli", "", [backend_project]),
              Developer("Emanuele De Cupis", "", [backend_project]),
              Developer("Pasquale De Vita", "", [backend_project]),
              Developer("Alessio Dore", "", [backend_project]),
              Developer("Francesco Persico", "", [backend_project]),
              Developer("Simone Infante", "", [backend_project]),
              Developer("Daniele Manni", "", [backend_project]))

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
	weekNumber = date.today().isocalendar()[1]
	msg = 'It would be nice if you take about 2 hours a week for <https://martinfowler.com/articles/on-pair-programming.html|pair programming>\n'
	msg += '\n> the best programs and designs are done by pairs, because you can criticise each other, and find each others errors, and use the best ideas\n'
	msg += '\nhere the weekly suggestion (`*r` means randomly picked)'
	msg += '\n'
	for p in developers_for_project.keys():
		if len(developers_for_project[p]) > 1:
			msg += '\n*%s* suggested pairs\n' % p
			devs = developers_for_project[p]
			devs_len = len(devs)
			index = weekNumber % devs_len
			devs_week_list = devs[index:]
			devs_week_list.extend(devs[0:index])
			index = 0
			import math
			couples = math.ceil(float(devs_len / 2.0))
			c = 0
			for x in range(couples):
				pair_1 = devs_week_list[index]
				is_random = False
				# this happens when the team is odd
				if index + 1 >= devs_len:
					# pick it randomly
					is_random = True
					temp_devs = devs_week_list[:]
					# remove the developer pair_1
					del temp_devs[0]
					# from developer list to a list of their index (all except the pair_1)
					temp_devs = list(map(lambda i: i[0], enumerate(temp_devs)))
					# pick an index randomly
					pair_2_index = temp_devs[random.randint(0, len(temp_devs) - 1)]
				else:
					pair_2_index = index + 1
				pair_2 = devs_week_list[pair_2_index]
				msg += '- %s / %s%s\n' % (pair_1.name, pair_2.name, '(*r)' if is_random else '')
				index += 2
				c += 1
	msg += '\n:movie_camera: it would be nice if you record your programming session\n> Share your knowledge. It is a way to achieve immortality.\n'
	return msg
