# Orbit scene

```python
class OrbitScene(Scene):
    def construct(self):
        self.t_offset=0
        orbit=Ellipse(color=GREEN).scale(2.5)
        planet=Dot()
        text=TextMobject("Orbit scene")

        planet.move_to(orbit.point_from_proportion(0))

        def update_planet(mob,dt):
            rate=dt*0.3
            mob.move_to(orbit.point_from_proportion(((self.t_offset + rate))%1))
            self.t_offset += rate

        planet.add_updater(update_planet)
        self.add(orbit,planet)
        self.wait(3)
        self.play(Write(text))
        self.wait(3)
```

Result:

<p align="center"><img src ="/community_examples/new_mobjects/screen_grid/CoordScreen.png" /></p>