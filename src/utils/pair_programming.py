from datetime import datetime

scheduling = ((("Matteo", "Simone"), ("Diego", "Fabrizio"), ("Federico", "Rocco")),  # 6 -> 21 -> 0
			  (("Federico", "Diego"), ("Rocco", "Matteo"), ("Simone", "Fabrizio")),  # 9 -> +3 -> 3
			  (("Diego", "Simone"), ("Matteo", "Federico"), ("Rocco", "Fabrizio")),  # 13 -> +7 -> 7
			  (("Rocco", "Diego"), ("Fabrizio", "Matteo"), ("Simone", "Federico")),  # 16 -> +11 -> 11
			  (("Diego", "Matteo"), ("Federico", "Fabrizio"), ("Rocco", "Simone")))  # 20 -> +15 -> 15

starting_date = datetime(2023, 2, 6)
round_indexes = (0, 3, 7, 10, 14)
scheduling_days = (0, 3)  # monday and thursday

dev_emoji_map = {"Matteo": ":boschi:",
				 "Simone": ":biffi:",
				 "Diego": ":pasquali:",
				 "Rocco": ":lucia:",
				 "Federico": ":feroldi:",
				 "Fabrizio": ":filizola:"}


def get_today_programming_pairs():
	'''
	:return: a tuple of tuple containing the pairs of the day. if the day is not a pairing day, it returns None
	'''
	today = datetime.today()
	days_diff_origin = (today - starting_date).days
	week_diff = int(days_diff_origin / 7)
	days_diff = days_diff_origin - week_diff * 7
	# we jump the session when a round has been completed
	is_jumping_day = days_diff_origin - week_diff * 7 == 3 and week_diff % 3 == 2
	is_pairing_day = (not is_jumping_day) and days_diff in scheduling_days
	if is_pairing_day:
		return scheduling[round_indexes.index(days_diff_origin % 21)]
