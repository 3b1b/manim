# from active_projects.clacks import question
# from active_projects.clacks import solution1
from active_projects.clacks.solution2 import block_collision_scenes
from active_projects.clacks.solution2 import simple_scenes
from active_projects.clacks.solution2 import wordy_scenes
from active_projects.clacks.solution2 import pi_creature_scenes
from active_projects.clacks.solution2 import position_phase_space

OUTPUT_DIRECTORY = "clacks_solution2"
ALL_SCENE_CLASSES = [
    # question.Thumbnail,
    # solution1.SolutionThumbnail,
    # question.BlocksAndWallExampleMass1e2,
    # question.BlocksAndWallExampleMass1e4,
    block_collision_scenes.IntroducePreviousTwoVideos,
    block_collision_scenes.PreviousTwoVideos,
    simple_scenes.TwoSolutionsWrapper,
    wordy_scenes.ConnectionToOptics,
    pi_creature_scenes.OnAnsweringTwice,
    position_phase_space.IntroducePositionPhaseSpace,
]
