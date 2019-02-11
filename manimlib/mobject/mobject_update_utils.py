def always_redraw(func):
    mob = func()
    mob.add_updater(lambda m: mob.become(func()))
    return mob
