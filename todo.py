from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.uix.behaviors import ButtonBehavior
from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp

# Set a background color for the window
Window.clearcolor = get_color_from_hex('#F5F5F5')


class RoundedButton(Button):
    def __init__(self, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.font_size = dp(14)
        self.color = (1, 1, 1, 1)
        self.background_color = get_color_from_hex('#2196F3')
        with self.canvas.before:
            Color(0, 0, 0, 0.2)
            self.rect_shadow = RoundedRectangle(
                size=self.size, pos=(self.x, self.y - dp(2)), radius=[dp(10)])
            Color(*self.background_color)
            self.rect = RoundedRectangle(
                size=self.size, pos=self.pos, radius=[dp(10)])
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.bind(on_press=self.on_press_effect)
        self.bind(on_release=self.on_release_effect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect_shadow.pos = (self.x, self.y - dp(2))
        self.rect.size = self.size
        self.rect_shadow.size = self.size

    def on_press_effect(self, instance):
        anim = Animation(
            size=(self.size[0] - dp(3), self.size[1] - dp(3)), duration=0.1)
        anim.start(self)

    def on_release_effect(self, instance):
        anim = Animation(
            size=(self.size[0] + dp(3), self.size[1] + dp(3)), duration=0.1)
        anim.start(self)


class EditTaskPopup(Popup):
    def __init__(self, task, **kwargs):
        super(EditTaskPopup, self).__init__(**kwargs)
        self.task = task
        self.title = "Edit Task"
        self.size_hint = (0.9, 0.5)
        self.background = 'atlas://data/images/defaulttheme/button'

        layout = BoxLayout(orientation='vertical',
                           padding=dp(20), spacing=dp(20))

        self.text_input = TextInput(
            text=task.task_label.text, multiline=False, size_hint=(1, 0.7), font_size=dp(18),
            background_color=get_color_from_hex('#FFFFFF'), foreground_color=get_color_from_hex('#333333'), halign="center", padding=[dp(10), dp(10), dp(10), dp(10)])
        layout.add_widget(self.text_input)

        button_layout = BoxLayout(size_hint=(1, 0.3), spacing=dp(20))

        save_button = RoundedButton(
            text="Save", background_color=get_color_from_hex('#4CAF50'))
        save_button.bind(on_press=self.save_task)
        button_layout.add_widget(save_button)

        cancel_button = RoundedButton(
            text="Cancel", background_color=get_color_from_hex('#F44336'))
        cancel_button.bind(on_press=self.dismiss)
        button_layout.add_widget(cancel_button)

        layout.add_widget(button_layout)

        self.add_widget(layout)

    def save_task(self, instance):
        self.task.task_label.text = self.text_input.text
        self.dismiss()


class Task(ButtonBehavior, BoxLayout):
    def __init__(self, title, completed=False, **kwargs):
        super(Task, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(80)
        self.padding = [dp(10), dp(5), dp(10), dp(5)]
        self.spacing = dp(10)

        with self.canvas.before:
            Color(1, 1, 1, 0.9)
            self.rect = RoundedRectangle(
                size=self.size, pos=self.pos, radius=[dp(10)])
            self.bind(pos=self.update_rect, size=self.update_rect)

        self.completed = CheckBox(size_hint=(None, 1), width=dp(50))
        self.completed.active = completed
        self.add_widget(self.completed)

        self.task_label = Label(text=title, halign='left', valign='middle', size_hint=(1, 1),
                                font_size=dp(16), color=get_color_from_hex('#333333'))
        self.task_label.bind(size=self.task_label.setter('text_size'))
        self.add_widget(self.task_label)

        button_layout = BoxLayout(orientation='vertical', size_hint=(
            None, 1), width=dp(60), spacing=dp(10))

        edit_button = RoundedButton(text='Edit', background_color=get_color_from_hex('#2196F3'),
                                    size_hint=(1, None), height=dp(35))
        edit_button.bind(on_press=self.edit_task)
        button_layout.add_widget(edit_button)

        delete_button = RoundedButton(text='Delete', background_color=get_color_from_hex('#F44336'),
                                      size_hint=(1, None), height=dp(35))
        delete_button.bind(on_press=self.delete_task)
        button_layout.add_widget(delete_button)

        self.add_widget(button_layout)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def edit_task(self, instance):
        popup = EditTaskPopup(task=self)
        popup.open()

    def delete_task(self, instance):
        parent = self.parent
        if parent:
            anim = Animation(opacity=0, duration=0.5)
            anim.bind(on_complete=lambda *args: parent.remove_widget(self))
            anim.start(self)


class TodoScreen(Screen):
    def __init__(self, **kwargs):
        super(TodoScreen, self).__init__(**kwargs)
        self.tasks = []

        main_layout = BoxLayout(orientation='vertical',
                                padding=dp(20), spacing=dp(20))

        header = BoxLayout(orientation='horizontal',
                           size_hint=(1, None), height=dp(60))
        header.add_widget(Label(text='To-Do App', font_size=dp(32),
                          color=get_color_from_hex('#333333'), bold=True))

        main_layout.add_widget(header)

        self.title_input = TextInput(hint_text='Enter task', multiline=False, size_hint=(1, None), height=dp(50),
                                     font_size=dp(18), background_color=get_color_from_hex('#FFFFFF'),
                                     foreground_color=get_color_from_hex('#333333'), halign="center",
                                     padding=[dp(10), dp(10), dp(10), dp(10)])
        main_layout.add_widget(self.title_input)

        button_layout = BoxLayout(size_hint=(
            1, None), height=dp(50), spacing=dp(20))

        add_button = RoundedButton(
            text='Add Task', background_color=get_color_from_hex('#4CAF50'))
        add_button.bind(on_press=self.add_task)
        button_layout.add_widget(add_button)

        up_button = RoundedButton(
            text='Up', background_color=get_color_from_hex('#2196F3'))
        up_button.bind(on_press=self.move_task_up)
        button_layout.add_widget(up_button)

        down_button = RoundedButton(
            text='Down', background_color=get_color_from_hex('#2196F3'))
        down_button.bind(on_press=self.move_task_down)
        button_layout.add_widget(down_button)

        main_layout.add_widget(button_layout)

        self.task_container = GridLayout(
            cols=1, size_hint_y=None, spacing=dp(20))
        self.task_container.bind(
            minimum_height=self.task_container.setter('height'))

        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.task_container)
        main_layout.add_widget(scroll_view)

        self.add_widget(main_layout)

    def add_task(self, instance):
        task_title = self.title_input.text.strip()
        if task_title:
            task = Task(title=task_title)
            self.task_container.add_widget(task)
            self.tasks.append(task)
            self.title_input.text = ''
            anim = Animation(opacity=1, d=0.5)
            anim.start(task)

    def move_task_up(self, instance):
        current_task = self.get_selected_task()
        if current_task:
            index = self.tasks.index(current_task)
            if index > 0:
                self.tasks.remove(current_task)
                self.tasks.insert(index - 1, current_task)
                self.refresh_task_list()

    def move_task_down(self, instance):
        current_task = self.get_selected_task()
        if current_task:
            index = self.tasks.index(current_task)
            if index < len(self.tasks) - 1:
                self.tasks.remove(current_task)
                self.tasks.insert(index + 1, current_task)
                self.refresh_task_list()

    def get_selected_task(self):
        for task in self.tasks:
            if task.completed.active:
                return task
        return None

    def refresh_task_list(self):
        self.task_container.clear_widgets()
        for task in self.tasks:
            self.task_container.add_widget(task)


class TodoApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(TodoScreen(name='todo'))
        return sm


if __name__ == '__main__':
    TodoApp().run()
