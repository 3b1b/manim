from active_projects.ode.part1.pendulum import *
from active_projects.ode.part1.staging import *
from active_projects.ode.part1.pi_scenes import *

OUTPUT_DIRECTORY = "ode/part1"
ALL_SCENE_CLASSES = [
    IntroducePendulum,
    MultiplePendulumsOverlayed,
    FormulasAreLies,
    MediumAnglePendulum,
    MediumHighAnglePendulum,
    HighAnglePendulum,
    LowAnglePendulum,
    SomeOfYouWatching,
    SmallAngleApproximationTex,
    VeryLowAnglePendulum,
    FollowThisThread,
    StrogatzQuote,
    # Something...
    ShowGravityAcceleration,
    AnalyzePendulumForce,
    BuildUpEquation,
]
