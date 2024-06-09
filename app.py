'''
Created by: Pranay Rishi Nalem
Date: June 8th, 2024 Time: 10:25 PST
Program Name: MathQuest Animations
Purpose: KTHack 2024
'''

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.videoplayer import VideoPlayer

# Function that Creates the Animation
# Decide whether to put in different files

class VideoPlayer(VideoPlayer):
    def build(self):
        #Create the video player
        player = VideoPlayer(source = "manim/media/videos/app/2852726489_784179552_1096191273.mp4") # make this more adaptive based on the picture inputed
        # VideoPlayer State
        player.state = 'play'
        player.options = {'eos' : 'stop'} # End of Stream, change to 'loop' for continuous video

'''
First Page Class which generates the main page for the users:
1. Title
2. Description
3. File Uploader
4. Button: Verifies the file upload and redirects to next page
'''
class EnteringPage(FloatLayout):
    def __init__ (self):
        super().__init__()
        # First Page Title
        self.startPageTitle = Label(text='MathQuest Animations',
                                    size_hint=(1, 1),
                                    pos_hint={'center_x':0.5, 'center_y':0.9}
                                    )
        self.add_widget(self.startPageTitle)
        
        # First Page Description
        self.appDescription = Label(text='Hello, welcome to this program. Ready to learn in-depth math concepts using animated videos? Upload an image and get started',
                                    size_hint=(0.5, 0.7),
                                    pos_hint={'center_x':0.2, 'center_y':0.7},
                                    #text_size=(self.width*0.8, None),
                                    #halign='left',
                                    #valign='middle'
                                    )
        self.add_widget(self.appDescription)

        # First Page File Chooser
        self.filechooser = FileChooserListView(
            size_hint=(0.8, 0.4), 
            pos_hint={'center_x': 0.5, 'center_y': 0.4}
        )
        self.filechooser.bind(on_selection=self.select)
        self.add_widget(self.filechooser)

        # The Button to Switch to Tutorial Page
        self.switch_button = Button(
            text='Upload',
            size_hint= (0.2, 0.1),
            pos_hint= {'center_x': 0.5, 'center_y':0.1}
        )
        self.switch_button.bind(on_press=self.switch)
        self.add_widget(self.switch_button)

        #The Label to Ensure the File has been Uploaded
        self.label = Label(
            text='No file selected',
            size_hint=(0.8, 0.1),
            pos_hint={'center_x': 0.5, 'center_y':0.2}
        )
        self.add_widget(self.label)

    def select(self, fileChooser, selection):
        if selection: self.label.text = selection[0]

    def switch(self, item):
        myapp.screen_manager.transition = SlideTransition(direction='left')
        myapp.screen_manager.current = 'Second'

# Second Page of the Program which displays the Animated Video
class TutorialPage(FloatLayout):
    def __init__ (self):
        super().__init__()
        #self.bind(on_press=self.switch)

        # Button Used to Go Back to the Main Screen to Reupload a New Image
        self.switchBackButton = Button(
            text='Go Back',
            size_hint= (0.2, 0.1),
            pos_hint= {'center_x': 0.25, 'center_y':0.1}
        )
        self.switchBackButton.bind(on_press=self.switchBack)
        self.add_widget(self.switchBackButton)

        # Button Used to Go Back to the Curriculum Screen to Explore More Animated Courses
        self.switchToCurriculumButton = Button(
            text='Explore More',
            size_hint= (0.2, 0.1),
            pos_hint= {'center_x': 0.75, 'center_y':0.1}
        )
        self.switchToCurriculumButton.bind(on_press=self.switchCourses)
        self.add_widget(self.switchToCurriculumButton)

    # Function Used to Switch Back to the Main Screen
    def switchBack(self, item):
        myapp.screen_manager.transition = SlideTransition(direction='right')
        myapp.screen_manager.current = 'First'

    #Function Used to Switch To the Curriculum/Courses Screen
    def switchCourses(self,item):
        myapp.screen_manager.transition = SlideTransition(direction='left')
        myapp.screen_manager.current = 'Third'


'''
Course Page of the Program: Students can explore other course/topic animations
1. Algebra, Trig., Calculus, (incorporate more with time)
'''

# This class ensures that I have a tabbed panel to switch between courses on the CoursesPage
class CoursesTabs(TabbedPanel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_default_tab = False
        self.size_hint = {1,1}

        #Creating the different tabs
        self.trigonometryTab = TabbedPanelItem(text='Trigonometry')
        self.algebraTab = TabbedPanelItem(text='Algebra')
        self.calculusTab = TabbedPanelItem(text='Calculus')

        # Animated Vidoe Lessons for Each Tab
        self.trigonometryVideo = VideoPlayer(source='trigonometry animation video source', # UPDATE THE VIDEO LINKS
                                            state='pause',
                                            options={'eos': 'pause'})
        self.algebraVideo = VideoPlayer(source='algebra animation video', #UPDATE THE VIDEO LINKS
                                            state='pause',
                                            options={'eos': 'pause'})
        self.calculusVideo = VideoPlayer(source='calculus animation video', #UPDATE THE VIDEO LINKS
                                            state='pause',
                                            options={'eos': 'pause'})
        
        # Putting the videos in each of the tabs
        self.trigonometryTab.add_widget(self.trigonometryVideo)
        self.algebraTab.add_widget(self.algebraVideo)
        self.calculusTab.add_widget(self.calculusVideo)

        # When switching between tabs, make sure that you pause the other video
        self.bind(current_tab=self.onTabSwitch)

        # Original Button Functionality from previous Class to return to the Main Page
        self.switchBackButton = Button(
            text='Go Back',
            size_hint= (0.2, 0.1),
            pos_hint= {'center_x': 0.5, 'center_y':0.1}
        )
        self.switchBackButton.bind(on_press=self.switchBack)
        self.add_widget(self.switchBackButton)

# Tab Switching Functionality to Ensure there is no overlay of videos
    def onTabSwitch(self, *args):
        self.trigonometryVideo.state = 'pause'
        self.algebraVideo.state = 'pause'
        self.calculusVideo.state = 'pause'

        # Once you are on a current tab, the video should start playing
        current_tab = self.current_tab
        if current_tab == self.trigonometryTab:
            self.trigonometryVideo.state = 'play'
        elif current_tab == self.algebraTab:
            self.algebraVideo.state = 'play'
        elif current_tab == self.calculusTab:
            self.calculusVideo.state = 'play'

    def switchBack(self, item):
        myapp.screen_manager.transition = SlideTransition(direction='left')
        myapp.screen_manager.current = "First"

# Main function: Runs the central program
class MyApp(App):
    def build(self):
        # First Page Program
        self.screen_manager = ScreenManager()
        self.firstpage = EnteringPage()
        screen = Screen(name='First')
        screen.add_widget(self.firstpage)
        self.screen_manager.add_widget(screen)

        # Second Page Program
        self.secondPage = TutorialPage()
        screen = Screen(name='Second')
        screen.add_widget(self.secondPage)
        self.screen_manager.add_widget(screen)
    
        # Third Page Program
        self.coursesPage = CoursesTabs()
        screen = Screen(name='Third')
        screen.add_widget(self.coursesPage)
        self.screen_manager.add_widget(screen)
        return self.screen_manager # ENSURE THAT THIS COMES LAST


myapp = MyApp()
myapp.run()