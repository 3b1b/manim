def updating_mobject_from_func(func):
    mob = func()
    mob.add_updater(lambda m: mob.become(func()))
    return mob
