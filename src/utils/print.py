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
        to_print += "\t* %s (%s - %d)\n" % (p["project_name"], p["role"], p["project_id"])
    return to_print


stories_icon = {"feature": "🌟",
                "bug": "🐞",
                "chore": "⚙️",
                "release": "🏁"}


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
            owner = list(filter(lambda x: x["person"]["id"] in owners_ids, members))
            if len(owner) == 0:
                owner = "n/a"
            else:
                owner = owner[0]["person"]["name"]
            members_cache[owner_id] = owner
            ows.append(owner)
        return ows

    printable_stories = []
    # sort by story state
    stories.sort(key=lambda r: r["current_state"])
    for t in stories:
        story_type = t.get("story_type", "")
        owners = get_owners(t["owner_ids"])
        story_type_icon = stories_icon.get(story_type, "❓")
        story = "<https://www.pivotaltracker.com/n/projects/%d/stories/%d|%s> - _%s_ %s" % (
            t['project_id'],
            t['id'],
            story_type_icon,
            t.get('name', ""),
            "" if len(owners) == 0 else ("(%s)" % " & ".join(owners)),)
        printable_stories.append(story)
    return printable_stories
