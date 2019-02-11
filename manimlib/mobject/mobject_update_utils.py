def always(method, *args, **kwargs):
    mobject = method.__self__
    func = method.__func__
    mobject.add_updater(lambda m: func(m, *args, **kwargs))


def always_redraw(func):
    mob = func()
    mob.add_updater(lambda m: mob.become(func()))
    return mob
