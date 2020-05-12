def print_me(me):
    """
    get a printable version of me
    :param me object
    :return: a printable version of me
    """
    to_print = f'''
name: {me["name"]}
username: {me["username"]}
initials: {me["initials"]}
email: {me["email"]}
projects: {len(me["projects"])}
'''
    for p in me["projects"]:
        to_print += "\t* %s (%s - %d)\n" % (p["project_name"],
                                            p["role"], p["project_id"])
    return to_print


stories_icon = {"feature": "⭐️",
                "bug": "🐞",
                "chore": "⚙️",
                "release": "🏁"}


def get_stories_count_recap(stories):
    """
    stories is a dict where the key is the story type and the value is a number
    :param stories:
    :return: a string
    """
    to_return = []
    print_order = ["release", "feature", "bug", "chore"]
    for story in print_order:
        if story not in stories:
            continue
        total = stories[story]
        to_return.append("%s %d" % (stories_icon.get(story, "❓"), total))
    return ", ".join(to_return)


def get_printable_stories(stories, members):
    """
    :param stories: a list of stories
    :param members: all members involved in stories
    :return: a list of string each one representing a story
    """
    members_cache = {}

    def get_owners(owners_ids):
        ows = []
        for owner in owners_ids[:]:
            if owner in members_cache:
                ows.append(members_cache[owner])
                owners_ids.remove(owner)
        for owner_id in owners_ids:
            owner = list(
                filter(lambda x: x["person"]["id"] == owner_id, members))
            if len(owner) == 0:
                owner = "n/a"
            else:
                owner = owner[0]["person"]["name"]
            members_cache[owner_id] = owner
            ows.append(owner)
        return ows

    printable_stories = []
    # sort by story state
    stories.sort(key=lambda r: r["story_type"])
    for t in stories:
        story_type = t.get("story_type", "")
        owners = get_owners(t["owner_ids"])
        estimate = int(t.get("estimate", "1"))
        story_type_icon = stories_icon.get(story_type, "❓") * max(estimate, 1)
        story = "<https://www.pivotaltracker.com/n/projects/%d/stories/%d|%s> %s %s" % (
            t['project_id'],
            t['id'],
            story_type_icon,
            t.get('name', ""),
            "" if len(owners) == 0 else ("_(%s)_" % " & ".join(owners)),)
        printable_stories.append(story)
    return printable_stories
