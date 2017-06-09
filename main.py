import kivy

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty

import os
import csv

# Utiliser des popup pour le parcours de fichier
# https://kivy.org/docs/api-kivy.uix.filechooser.html#kivy.uix.filechooser.FileChooserListView
# screens : home & jeu

Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
#Config.set('graphics', 'resizable', False)

cards = []

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class GameScreen(Screen):
    text_guess = ObjectProperty(None)
    progress_bar = ObjectProperty(None)
    input_to_test = ObjectProperty(None)

    index = 0
    errors = 0

    def on_enter(self, *args):
        self.input_to_test.focus = True
        self.text_guess.text = self.draw_card()
        self.progress_bar.max = len(cards)
        self.index = 0
        self.errors = 0

    def validate(self):
        answer = self.input_to_test.text

        if self.index < len(cards):
            if self.check_answer(answer):
                self.progress_bar.value = self.progress_bar.value + 1
                self.input_to_test.text = ""
                self.input_to_test.background_color = (1, 1, 1, 1)

                if self.index+1 < len(cards):
                    self.index = self.index + 1
                    self.text_guess.text = self.draw_card()
                    Clock.schedule_once(self._refocus_ti)
                else:
                    text = "You made " + str(self.errors) + " error for " + str(len(cards)) + " cards"
                    popup = Popup(title='Results', content=Label(text=text), size_hint=(0.9, 0.9),
                                  on_dismiss=self.quit_game)
                    popup.open()
            else:
                self.input_to_test.background_color = (1, 0, 0, 1)
                self.input_to_test.text = ""
                self.errors = self.errors + 1
                Clock.schedule_once(self._refocus_ti)

    def draw_card(self):
        return cards[self.index][0]

    def check_answer(self, answer):
        return answer == cards[self.index][1]

    def _refocus_ti(self, *args):
        del args
        self.input_to_test.focus = True

    def quit_game(self, *args):
        del args
        self.manager.current = "home"
    

class MainScreen(Screen):

    text_input = ObjectProperty(None)
    loadfile = ObjectProperty(None)


    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load CSV", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        global cards
        with open(os.path.join(path, filename[0]), "r") as stream:
            csv_reader = csv.reader(stream)
            cards = list(csv_reader)
            self.text_input.text = filename[0]

        self.dismiss_popup()

class Manager(ScreenManager):
    main_screen = ObjectProperty(None)
    browse_screen = ObjectProperty(None)


class MainApp(App):
    def build(self):
        return Manager()

if __name__ == '__main__':
    MainApp(title="Flashcard Trainer").run()