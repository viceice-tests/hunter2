import rules


@rules.predicate
def is_admin_for_event(user, event):
    admin_team = event.teams.filter(is_admin=True).get()
    return user in admin_team.users

rules.add_perm('ihunt.change_event', is_admin_for_event)
