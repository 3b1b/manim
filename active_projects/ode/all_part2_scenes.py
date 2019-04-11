from active_projects.ode.part2.staging import *
from active_projects.ode.part2.fourier_series import *
from active_projects.ode.part2.heat_equation import *
from active_projects.ode.part2.pi_scenes import *
from active_projects.ode.part2.wordy_scenes import *

OUTPUT_DIRECTORY = "ode/part2"
ALL_SCENE_CLASSES = [
    # Tests
    FourierOfPiSymbol,
    FourierOfPiSymbol5,
    FourierOfTrebleClef,
    FourierOfEighthNote,
    FourierOfN,
    FourierNailAndGear,
    FourierNDQ,
    FourierBatman,
    FourierGoogleG,
    FourierHeart,
    # CirclesDrawingWave,
    # Scenes for video
    ExplainCircleAnimations,
    FourierSeriesIntroBackground4,
    FourierSeriesIntroBackground8,
    FourierSeriesIntroBackground12,
    FourierSeriesIntroBackground20,
    FourierSeriesIntro,
    PartTwoOfTour,
    TwoDBodyWithManyTemperatures,
    TwoDBodyWithManyTemperaturesGraph,
    TwoDBodyWithManyTemperaturesContour,
    BringTwoRodsTogether,
    ShowEvolvingTempGraphWithArrows,
    TodaysTargetWrapper,
    WriteHeatEquation,
    ReactionsToInitialHeatEquation,
    TalkThrough1DHeatGraph,
    ShowCubeFormation,
    CompareInputsOfGeneralCaseTo1D,
    TransitionToTempVsTime,
    ShowNewton,
    ShowCupOfWater,
    ShowNewtonsLawGraph,
]
