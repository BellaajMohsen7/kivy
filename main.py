import os
import json
from datetime import datetime
import uuid

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldHelperText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogSupportingText, MDDialogButtonContainer, MDDialogContentContainer
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText, MDSnackbarActionButton, MDSnackbarActionButtonText
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window

# Set mobile-friendly window size for testing
Window.size = (400, 700)

class DatabaseManager:
    def __init__(self):
        self.data_file = 'fitness_data.json'
        self.data = self.load_data()
    
    def create_tables(self):
        if not self.data:
            self.data = {
                "app_stats": {
                    "total_exercises": 0,
                    "total_sessions": 0, 
                    "total_volume": 0,
                    "weekly_workouts": 0
                },
                "workout_sessions": {},
                "user_settings": {"name": "BellaajMohsen7", "weight_unit": "kg", "theme": "dark"}
            }
            self.save_data()
    
    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading data: {e}")
            return {}
    
    def save_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def get_app_stats(self):
        return self.data.get('app_stats', {
            "total_exercises": 0,
            "total_sessions": 0,
            "total_volume": 0,
            "weekly_workouts": 0
        })
    
    def get_workout_sessions(self):
        return self.data.get('workout_sessions', {})
    
    def create_workout_session(self, name, workout_type="Custom"):
        session_id = f"session_{str(uuid.uuid4())[:8]}"
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M")
        
        session_data = {
            "id": session_id, "name": name, "date": current_date, "time": current_time,
            "workout_type": workout_type, "exercises": {}, "status": "active"
        }
        
        self.data['workout_sessions'][session_id] = session_data
        self.update_stats()
        self.save_data()
        return session_id
    
    def delete_workout_session(self, session_id):
        if session_id in self.data['workout_sessions']:
            del self.data['workout_sessions'][session_id]
            self.update_stats()
            self.save_data()
            return True
        return False
    
    def get_workout_session(self, session_id):
        return self.data['workout_sessions'].get(session_id, {})
    
    def add_exercise(self, session_id, exercise_name, muscle_group="General"):
        if session_id not in self.data['workout_sessions']:
            return None
        
        exercise_id = f"exercise_{str(uuid.uuid4())[:8]}"
        exercise_data = {
            "id": exercise_id, "name": exercise_name, "muscle_group": muscle_group,
            "sets": {}, "created_at": datetime.now().strftime("%H:%M")
        }
        
        self.data['workout_sessions'][session_id]['exercises'][exercise_id] = exercise_data
        self.update_stats()
        self.save_data()
        return exercise_id
    
    def delete_exercise(self, session_id, exercise_id):
        if (session_id in self.data['workout_sessions'] and 
            exercise_id in self.data['workout_sessions'][session_id]['exercises']):
            del self.data['workout_sessions'][session_id]['exercises'][exercise_id]
            self.update_stats()
            self.save_data()
            return True
        return False
    
    def add_set(self, session_id, exercise_id, weight, reps):
        if (session_id not in self.data['workout_sessions'] or 
            exercise_id not in self.data['workout_sessions'][session_id]['exercises']):
            return None
        
        sets = self.data['workout_sessions'][session_id]['exercises'][exercise_id]['sets']
        set_number = len(sets) + 1
        set_id = f"set_{set_number}"
        
        volume = float(weight) * int(reps)
        set_data = {
            "set_number": set_number, "weight": float(weight), "reps": int(reps),
            "volume": volume, "created_at": datetime.now().strftime("%H:%M")
        }
        
        sets[set_id] = set_data
        self.update_stats()
        self.save_data()
        return set_id
    
    def update_set(self, session_id, exercise_id, set_id, weight=None, reps=None):
        if (session_id in self.data['workout_sessions'] and 
            exercise_id in self.data['workout_sessions'][session_id]['exercises'] and
            set_id in self.data['workout_sessions'][session_id]['exercises'][exercise_id]['sets']):
            
            set_data = self.data['workout_sessions'][session_id]['exercises'][exercise_id]['sets'][set_id]
            
            if weight is not None:
                set_data['weight'] = float(weight)
            if reps is not None:
                set_data['reps'] = int(reps)
            
            set_data['volume'] = set_data['weight'] * set_data['reps']
            self.update_stats()
            self.save_data()
            return True
        return False
    
    def delete_set(self, session_id, exercise_id, set_id):
        if (session_id in self.data['workout_sessions'] and 
            exercise_id in self.data['workout_sessions'][session_id]['exercises'] and
            set_id in self.data['workout_sessions'][session_id]['exercises'][exercise_id]['sets']):
            del self.data['workout_sessions'][session_id]['exercises'][exercise_id]['sets'][set_id]
            self.update_stats()
            self.save_data()
            return True
        return False
    
    def update_stats(self):
        total_exercises = 0
        total_sessions = len(self.data['workout_sessions'])
        total_volume = 0
        
        for session in self.data['workout_sessions'].values():
            total_exercises += len(session['exercises'])
            for exercise in session['exercises'].values():
                for set_data in exercise['sets'].values():
                    total_volume += set_data['volume']
        
        self.data['app_stats'] = {
            "total_exercises": total_exercises,
            "total_sessions": total_sessions,
            "total_volume": int(total_volume),
            "weekly_workouts": min(total_sessions, 7)
        }

class PerfectStatCard(MDCard):
    def __init__(self, title, value, subtitle, icon, color, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = color
        self.elevation = 6
        self.padding = dp(20)
        self.height = dp(140)
        self.size_hint_y = None
        self.radius = [20, 20, 20, 20]
        
        # Animation
        self.opacity = 0
        anim = Animation(opacity=1, duration=0.6)
        anim.start(self)
        
        layout = MDBoxLayout(orientation='vertical', spacing=dp(8))
        
        # Header with icon and title - PERFECTLY aligned
        header_layout = MDBoxLayout(orientation='horizontal', spacing=dp(12), size_hint_y=None, height=dp(32))
        
        icon_button = MDIconButton(
            icon=icon, style="standard", theme_icon_color="Custom", icon_color=(1, 1, 1, 1),
            size_hint=(None, None), size=(dp(32), dp(32))
        )
        
        title_label = MDLabel(
            text=title, theme_text_color="Custom", text_color=(1, 1, 1, 0.9),
            font_size=sp(15), bold=True, valign="middle", size_hint_y=None, height=dp(32)
        )
        
        header_layout.add_widget(icon_button)
        header_layout.add_widget(title_label)
        
        # Value - large and centered
        self.value_label = MDLabel(
            text=str(value), theme_text_color="Custom", text_color=(1, 1, 1, 1),
            font_size=sp(32), bold=True, size_hint_y=None, height=dp(45),
            halign="center", valign="middle"
        )
        
        # Subtitle - centered
        subtitle_label = MDLabel(
            text=subtitle, theme_text_color="Custom", text_color=(1, 1, 1, 0.8),
            font_size=sp(12), size_hint_y=None, height=dp(20), 
            halign="center", valign="middle"
        )
        
        layout.add_widget(header_layout)
        layout.add_widget(self.value_label)
        layout.add_widget(subtitle_label)
        self.add_widget(layout)
    
    def update_value(self, new_value):
        self.value_label.text = str(new_value)
        anim = Animation(opacity=0.8, duration=0.15) + Animation(opacity=1, duration=0.15)
        anim.start(self.value_label)

class PerfectWorkoutCard(MDCard):
    def __init__(self, session_id, session_data, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.session_id = session_id
        self.session_data = session_data
        self.main_screen = main_screen
        
        self.md_bg_color = [0.15, 0.15, 0.15, 1]
        self.elevation = 4
        self.padding = dp(20)
        self.size_hint_y = None
        self.height = dp(130)
        self.radius = [16, 16, 16, 16]
        
        self.build_card()
    
    def build_card(self):
        main_layout = MDBoxLayout(orientation='vertical', spacing=dp(12))
        
        # Header with type indicator and content
        header_layout = MDBoxLayout(orientation='horizontal', spacing=dp(12))
        
        # Workout type indicator
        type_colors = {
            'Push': [0.94, 0.35, 0.35, 1], 'Pull': [0.23, 0.51, 0.96, 1],
            'Legs': [0.06, 0.72, 0.51, 1], 'Custom': [0.55, 0.36, 0.97, 1]
        }
        type_indicator = MDCard(
            md_bg_color=type_colors.get(self.session_data.get('workout_type', 'Custom'), type_colors['Custom']),
            size_hint_x=None, width=dp(6), height=dp(50), radius=[3, 3, 3, 3]
        )
        
        # Content - properly aligned
        content_layout = MDBoxLayout(orientation='vertical', spacing=dp(4))
        
        # Workout name
        name_label = MDLabel(
            text=self.session_data['name'], font_size=sp(17), bold=True,
            size_hint_y=None, height=dp(25), valign="middle"
        )
        
        # Date and time
        date_time_label = MDLabel(
            text=f"{self.session_data['date']} • {self.session_data.get('time', '00:00')}",
            font_size=sp(13), theme_text_color="Secondary",
            size_hint_y=None, height=dp(20), valign="middle"
        )
        
        content_layout.add_widget(name_label)
        content_layout.add_widget(date_time_label)
        
        header_layout.add_widget(type_indicator)
        header_layout.add_widget(content_layout)
        
        # Stats row - perfectly aligned
        stats_layout = MDBoxLayout(orientation='horizontal', spacing=dp(20), size_hint_y=None, height=dp(30))
        
        exercises_count = len(self.session_data.get('exercises', {}))
        total_sets = sum(len(ex.get('sets', {})) for ex in self.session_data.get('exercises', {}).values())
        total_volume = sum(sum(s.get('volume', 0) for s in ex.get('sets', {}).values()) 
                          for ex in self.session_data.get('exercises', {}).values())
        
        stats_layout.add_widget(self.create_perfect_stat("💪", f"{exercises_count} Ex"))
        stats_layout.add_widget(self.create_perfect_stat("📋", f"{total_sets} Sets"))
        stats_layout.add_widget(self.create_perfect_stat("⚖️", f"{total_volume:.0f}kg"))
        
        # Actions row
        actions_layout = MDBoxLayout(orientation='horizontal', spacing=dp(12), size_hint_y=None, height=dp(40))
        
        view_button = MDButton(
            MDButtonText(text="Open Workout"), style="elevated", 
            theme_bg_color="Custom", md_bg_color=[0.23, 0.51, 0.96, 1],
            size_hint_y=None, height=dp(40), on_release=lambda x: self.view_workout()
        )
        
        delete_button = MDIconButton(
            icon="delete-outline", style="standard", theme_icon_color="Custom",
            icon_color=[0.94, 0.27, 0.27, 1], size_hint_x=None, width=dp(40),
            on_release=lambda x: self.confirm_delete()
        )
        
        actions_layout.add_widget(view_button)
        actions_layout.add_widget(delete_button)
        
        main_layout.add_widget(header_layout)
        main_layout.add_widget(stats_layout)
        main_layout.add_widget(actions_layout)
        self.add_widget(main_layout)
    
    def create_perfect_stat(self, emoji, text):
        layout = MDBoxLayout(orientation='horizontal', spacing=dp(6), size_hint_x=None, width=dp(80))
        
        emoji_label = MDLabel(
            text=emoji, font_size=sp(14), size_hint_x=None, width=dp(20), 
            halign="center", valign="middle"
        )
        
        text_label = MDLabel(
            text=text, font_size=sp(12), theme_text_color="Secondary",
            valign="middle"
        )
        
        layout.add_widget(emoji_label)
        layout.add_widget(text_label)
        return layout
    
    def view_workout(self):
        app = MDApp.get_running_app()
        app.workout_screen.set_current_session(self.session_id)
        app.screen_manager.current = 'workout'
    
    def confirm_delete(self):
        dialog = MDDialog(
            MDDialogHeadlineText(text="Delete Workout"),
            MDDialogSupportingText(text=f"Delete '{self.session_data['name']}'? This cannot be undone."),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="CANCEL"), style="text", on_release=lambda x: dialog.dismiss()),
                MDButton(MDButtonText(text="DELETE"), style="text", theme_text_color="Custom",
                        text_color=[0.94, 0.27, 0.27, 1], on_release=lambda x: self.delete_workout(dialog)),
            ),
        )
        dialog.open()
    
    def delete_workout(self, dialog):
        app = MDApp.get_running_app()
        app.db_manager.delete_workout_session(self.session_id)
        self.main_screen.update_statistics()
        dialog.dismiss()
        
        snackbar = MDSnackbar(
            MDSnackbarText(text="Workout deleted successfully"),
            size_hint_x=0.95, pos_hint={"center_x": 0.5}
        )
        snackbar.open()

class PerfectSetCard(MDCard):
    def __init__(self, set_id, set_data, exercise_screen, **kwargs):
        super().__init__(**kwargs)
        self.set_id = set_id
        self.set_data = set_data
        self.exercise_screen = exercise_screen
        
        self.md_bg_color = [0.12, 0.12, 0.12, 1]
        self.elevation = 3
        self.padding = dp(20)
        self.size_hint_y = None
        self.height = dp(90)
        self.radius = [12, 12, 12, 12]
        
        self.build_card()
    
    def build_card(self):
        main_layout = MDBoxLayout(orientation='horizontal', spacing=dp(16))
        
        # Set number - perfect circle
        set_indicator = MDCard(
            md_bg_color=[0.23, 0.51, 0.96, 1], size_hint_x=None, width=dp(50), height=dp(50), 
            radius=[25, 25, 25, 25]
        )
        set_label = MDLabel(
            text=str(self.set_data['set_number']), font_size=sp(18), bold=True,
            halign="center", valign="middle", theme_text_color="Custom", text_color=(1, 1, 1, 1)
        )
        set_indicator.add_widget(set_label)
        
        # Details - perfectly aligned
        details_layout = MDBoxLayout(orientation='vertical', spacing=dp(6))
        
        # Main info - weight and reps
        main_info = MDLabel(
            text=f"{self.set_data['weight']}kg × {self.set_data['reps']} reps",
            font_size=sp(16), bold=True, size_hint_y=None, height=dp(22),
            valign="middle"
        )
        
        # Secondary info - volume and time
        secondary_info = MDLabel(
            text=f"Vol: {self.set_data['volume']:.0f}kg • {self.set_data.get('created_at', '00:00')}",
            font_size=sp(13), theme_text_color="Secondary", size_hint_y=None, height=dp(18),
            valign="middle"
        )
        
        details_layout.add_widget(main_info)
        details_layout.add_widget(secondary_info)
        
        # Action buttons - perfectly aligned
        action_layout = MDBoxLayout(orientation='horizontal', size_hint_x=None, width=dp(80), spacing=dp(8))
        
        edit_button = MDIconButton(
            icon="pencil", style="standard", theme_icon_color="Primary",
            size_hint=(None, None), size=(dp(36), dp(36)), on_release=lambda x: self.edit_set()
        )
        
        delete_button = MDIconButton(
            icon="delete-outline", style="standard", theme_icon_color="Custom",
            icon_color=[0.94, 0.27, 0.27, 1], size_hint=(None, None), size=(dp(36), dp(36)),
            on_release=lambda x: self.confirm_delete()
        )
        
        action_layout.add_widget(edit_button)
        action_layout.add_widget(delete_button)
        
        main_layout.add_widget(set_indicator)
        main_layout.add_widget(details_layout)
        main_layout.add_widget(action_layout)
        self.add_widget(main_layout)
    
    def edit_set(self):
        content = MDBoxLayout(orientation='vertical', spacing=dp(20), size_hint_y=None, height=dp(180))
        
        # Current values display
        current_info = MDLabel(
            text=f"Current: {self.set_data['weight']}kg × {self.set_data['reps']} reps",
            font_size=sp(15), theme_text_color="Secondary", size_hint_y=None, height=dp(30),
            halign="center", valign="middle"
        )
        
        weight_field = MDTextField(
            MDTextFieldHintText(text="Weight (kg)"),
            text=str(self.set_data['weight']), input_filter="float", 
            size_hint_y=None, height=dp(60), font_size=sp(16)
        )
        
        reps_field = MDTextField(
            MDTextFieldHintText(text="Repetitions"),
            text=str(self.set_data['reps']), input_filter="int",
            size_hint_y=None, height=dp(60), font_size=sp(16)
        )
        
        content.add_widget(current_info)
        content.add_widget(weight_field)
        content.add_widget(reps_field)
        
        dialog = MDDialog(
            MDDialogHeadlineText(text=f"Edit Set {self.set_data['set_number']}"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="CANCEL"), style="text", on_release=lambda x: dialog.dismiss()),
                MDButton(MDButtonText(text="UPDATE"), style="text",
                        on_release=lambda x: self.update_set(dialog, weight_field.text, reps_field.text)),
            ),
        )
        dialog.open()
    
    def update_set(self, dialog, weight, reps):
        try:
            weight_val = float(weight) if weight else self.set_data['weight']
            reps_val = int(reps) if reps else self.set_data['reps']
            
            if weight_val > 0 and reps_val > 0:
                app = MDApp.get_running_app()
                success = app.db_manager.update_set(
                    self.exercise_screen.current_session_id,
                    self.exercise_screen.current_exercise_id,
                    self.set_id, weight_val, reps_val
                )
                
                if success:
                    self.exercise_screen.refresh_sets()
                    app.main_screen.update_statistics()
                    
                    snackbar = MDSnackbar(
                        MDSnackbarText(text="Set updated successfully"),
                        size_hint_x=0.95, pos_hint={"center_x": 0.5}
                    )
                    snackbar.open()
        except ValueError:
            snackbar = MDSnackbar(
                MDSnackbarText(text="Please enter valid numbers"),
                size_hint_x=0.95, pos_hint={"center_x": 0.5}
            )
            snackbar.open()
        
        dialog.dismiss()
    
    def confirm_delete(self):
        dialog = MDDialog(
            MDDialogHeadlineText(text="Delete Set"),
            MDDialogSupportingText(text=f"Delete Set {self.set_data['set_number']}?"),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="CANCEL"), style="text", on_release=lambda x: dialog.dismiss()),
                MDButton(MDButtonText(text="DELETE"), style="text", theme_text_color="Custom",
                        text_color=[0.94, 0.27, 0.27, 1], on_release=lambda x: self.delete_set(dialog)),
            ),
        )
        dialog.open()
    
    def delete_set(self, dialog):
        app = MDApp.get_running_app()
        app.db_manager.delete_set(self.exercise_screen.current_session_id,
                                  self.exercise_screen.current_exercise_id, self.set_id)
        self.exercise_screen.refresh_sets()
        app.main_screen.update_statistics()
        dialog.dismiss()

class PerfectHeaderCard(MDCard):
    def __init__(self, title, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = [0.1, 0.1, 0.1, 1]
        self.elevation = 4
        self.padding = dp(16)
        self.size_hint_y = None
        self.height = dp(60)
        self.radius = [0, 0, 16, 16]
        
        layout = MDBoxLayout(orientation='horizontal', spacing=dp(12))
        
        # Back button - perfectly sized
        back_button = MDIconButton(
            icon="arrow-left", style="standard", size_hint_x=None, width=dp(40),
            size_hint=(None, None), size=(dp(40), dp(40))
        )
        
        # Title - perfectly aligned
        title_label = MDLabel(
            text=title, font_size=sp(18), bold=True, valign="middle"
        )
        
        layout.add_widget(back_button)
        layout.add_widget(title_label)
        self.add_widget(layout)
        
        # Store references
        self.back_button = back_button
        self.title_label = title_label
    
    def set_back_action(self, action):
        self.back_button.bind(on_release=action)
    
    def set_title(self, title):
        self.title_label.text = title

class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        main_layout = MDBoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16))
        
        # Header section - perfectly aligned
        header_layout = MDBoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None, height=dp(85))
        
        welcome_label = MDLabel(
            text="Welcome back, BellaajMohsen7!", font_size=sp(20), bold=True,
            size_hint_y=None, height=dp(30), valign="middle"
        )
        
        date_label = MDLabel(
            text=datetime.now().strftime("Today is %A, %B %d"), font_size=sp(15),
            theme_text_color="Secondary", size_hint_y=None, height=dp(25), valign="middle"
        )
        
        motivation_label = MDLabel(
            text="Ready to crush your workout?", font_size=sp(13),
            theme_text_color="Primary", size_hint_y=None, height=dp(22), valign="middle"
        )
        
        header_layout.add_widget(welcome_label)
        header_layout.add_widget(date_label)
        header_layout.add_widget(motivation_label)
        
        # Stats section
        stats_header = MDLabel(
            text="Your Progress", font_size=sp(18), bold=True, size_hint_y=None, height=dp(35),
            valign="middle"
        )
        
        # Perfect stat cards
        self.total_exercises_card = PerfectStatCard(
            "Exercises", "0", "Total completed", "dumbbell", [0.23, 0.51, 0.96, 1]
        )
        self.total_sessions_card = PerfectStatCard(
            "Sessions", "0", "Workouts done", "calendar-check", [0.06, 0.72, 0.51, 1]
        )
        self.total_volume_card = PerfectStatCard(
            "Volume", "0 kg", "Weight lifted", "weight-kilogram", [0.55, 0.36, 0.97, 1]
        )
        self.weekly_workouts_card = PerfectStatCard(
            "This Week", "0", "Days trained", "fire", [0.94, 0.35, 0.35, 1]
        )
        
        # Quick actions
        actions_header = MDLabel(
            text="Quick Actions", font_size=sp(18), bold=True, size_hint_y=None, height=dp(35),
            valign="middle"
        )
        
        actions_layout = MDBoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(110))
        
        new_workout_button = MDButton(
            MDButtonText(text="Start New Workout"), style="elevated", 
            theme_bg_color="Custom", md_bg_color=[0.23, 0.51, 0.96, 1],
            size_hint_y=None, height=dp(50), on_release=self.show_new_workout_dialog
        )
        
        quick_add_button = MDButton(
            MDButtonText(text="Quick Templates"), style="outlined",
            size_hint_y=None, height=dp(45), on_release=self.show_quick_add_dialog
        )
        
        actions_layout.add_widget(new_workout_button)
        actions_layout.add_widget(quick_add_button)
        
        # Recent workouts
        workouts_header = MDLabel(
            text="Recent Workouts", font_size=sp(18), bold=True, size_hint_y=None, height=dp(35),
            valign="middle"
        )
        
        self.workouts_scroll = MDScrollView()
        self.workouts_layout = MDBoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None, height=dp(0))
        self.workouts_scroll.add_widget(self.workouts_layout)
        
        # Add components
        main_layout.add_widget(header_layout)
        main_layout.add_widget(stats_header)
        main_layout.add_widget(self.total_exercises_card)
        main_layout.add_widget(self.total_sessions_card)
        main_layout.add_widget(self.total_volume_card)
        main_layout.add_widget(self.weekly_workouts_card)
        main_layout.add_widget(actions_header)
        main_layout.add_widget(actions_layout)
        main_layout.add_widget(workouts_header)
        main_layout.add_widget(self.workouts_scroll)
        
        self.add_widget(main_layout)
    
    def update_statistics(self):
        app = MDApp.get_running_app()
        stats = app.db_manager.get_app_stats()
        
        self.total_exercises_card.update_value(stats['total_exercises'])
        self.total_sessions_card.update_value(stats['total_sessions'])
        self.total_volume_card.update_value(f"{stats['total_volume']:,}")
        self.weekly_workouts_card.update_value(stats.get('weekly_workouts', 0))
        
        self.refresh_workouts_list()
    
    def refresh_workouts_list(self):
        self.workouts_layout.clear_widgets()
        self.workouts_layout.height = dp(0)
        
        app = MDApp.get_running_app()
        sessions = app.db_manager.get_workout_sessions()
        
        sorted_sessions = sorted(sessions.items(), key=lambda x: x[1]['date'], reverse=True)
        
        for session_id, session_data in sorted_sessions:
            workout_card = PerfectWorkoutCard(session_id, session_data, self)
            self.workouts_layout.add_widget(workout_card)
            self.workouts_layout.height += dp(142)  # Card height + spacing
        
        if not sessions:
            self.add_empty_state()
    
    def add_empty_state(self):
        empty_state = MDCard(
            md_bg_color=[0.1, 0.1, 0.1, 1], elevation=2, padding=dp(32),
            size_hint_y=None, height=dp(180), radius=[16, 16, 16, 16]
        )
        
        empty_layout = MDBoxLayout(orientation='vertical', spacing=dp(12))
        
        emoji_label = MDLabel(
            text="🏋️‍♂️", font_size=sp(48), halign="center", valign="middle",
            size_hint_y=None, height=dp(60)
        )
        
        title_label = MDLabel(
            text="No workouts yet", font_size=sp(18), bold=True, halign="center", 
            theme_text_color="Secondary", size_hint_y=None, height=dp(30), valign="middle"
        )
        
        subtitle_label = MDLabel(
            text="Start your fitness journey today!", font_size=sp(14),
            halign="center", theme_text_color="Secondary", size_hint_y=None, height=dp(25),
            valign="middle"
        )
        
        empty_layout.add_widget(emoji_label)
        empty_layout.add_widget(title_label)
        empty_layout.add_widget(subtitle_label)
        
        empty_state.add_widget(empty_layout)
        self.workouts_layout.add_widget(empty_state)
        self.workouts_layout.height += dp(192)
    
    def show_new_workout_dialog(self, *args):
        # FIXED DIALOG CONTENT - Properly aligned
        content = MDBoxLayout(orientation='vertical', spacing=dp(16), size_hint_y=None, height=dp(280))
        
        # Workout name field - properly aligned
        workout_name_field = MDTextField(
            MDTextFieldHintText(text="Workout name"),
            MDTextFieldHelperText(text="e.g., Push Day, Morning Run, Leg Day"),
            size_hint_y=None, height=dp(70), font_size=sp(16)
        )
        
        # Type selection header - properly aligned
        type_label = MDLabel(
            text="Choose workout type:", font_size=sp(16), bold=True,
            size_hint_y=None, height=dp(30), valign="middle"
        )
        
        # Type buttons container - scrollable and properly aligned
        type_scroll = MDScrollView(size_hint_y=None, height=dp(160))
        type_layout = MDBoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        type_layout.bind(minimum_height=type_layout.setter('height'))
        
        type_buttons = []
        workout_types = [
            ('Push Day', 'Push'), 
            ('Pull Day', 'Pull'), 
            ('Leg Day', 'Legs'), 
            ('Cardio Session', 'Cardio'), 
            ('Custom Workout', 'Custom')
        ]
        selected_type = ['Custom']
        
        for display_name, wtype in workout_types:
            btn = MDButton(
                MDButtonText(text=display_name), 
                style="outlined", 
                size_hint_y=None, 
                height=dp(48),
                on_release=lambda x, t=wtype: self.select_workout_type(t, type_buttons, selected_type)
            )
            type_buttons.append(btn)
            type_layout.add_widget(btn)
        
        # Set last button as elevated (selected)
        type_buttons[-1].style = "elevated"
        type_scroll.add_widget(type_layout)
        
        # Add all content with proper spacing
        content.add_widget(workout_name_field)
        content.add_widget(type_label)
        content.add_widget(type_scroll)
        
        # Create dialog with proper sizing
        dialog = MDDialog(
            MDDialogHeadlineText(text="Create New Workout"),
            MDDialogSupportingText(text="Let's start your training session!"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="CANCEL"), 
                    style="text", 
                    on_release=lambda x: dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="START WORKOUT"), 
                    style="text",
                    on_release=lambda x: self.create_new_workout(dialog, workout_name_field.text, selected_type[0])
                ),
            ),
        )
        dialog.open()
    
    def select_workout_type(self, workout_type, buttons, selected_type):
        selected_type[0] = workout_type
        for btn in buttons:
            btn.style = "elevated" if btn.children[0].text.endswith(' Day') and workout_type in btn.children[0].text or btn.children[0].text.startswith(workout_type) else "outlined"
    
    def show_quick_add_dialog(self, *args):
        templates = [("Quick Push", "Push"), ("Quick Pull", "Pull"), ("Quick Legs", "Legs"), ("Quick Cardio", "Cardio")]
        
        content = MDBoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None, height=dp(220))
        content.add_widget(MDLabel(
            text="Choose a quick template:", font_size=sp(15), bold=True,
            size_hint_y=None, height=dp(30), valign="middle"
        ))
        
        for name, wtype in templates:
            btn = MDButton(
                MDButtonText(text=name), style="outlined", size_hint_y=None, height=dp(42),
                on_release=lambda x, n=name, t=wtype: self.create_quick_workout(dialog, n, t)
            )
            content.add_widget(btn)
        
        dialog = MDDialog(
            MDDialogHeadlineText(text="Quick Start"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="CANCEL"), style="text", on_release=lambda x: dialog.dismiss()),
            ),
        )
        dialog.open()
    
    def create_quick_workout(self, dialog, name, workout_type):
        app = MDApp.get_running_app()
        session_id = app.db_manager.create_workout_session(name, workout_type)
        self.update_statistics()
        dialog.dismiss()
        
        app.workout_screen.set_current_session(session_id)
        app.screen_manager.current = 'workout'
    
    def create_new_workout(self, dialog, workout_name, workout_type):
        if not workout_name.strip():
            workout_name = f"{workout_type} Workout"
        
        app = MDApp.get_running_app()
        session_id = app.db_manager.create_workout_session(workout_name.strip(), workout_type)
        self.update_statistics()
        dialog.dismiss()
        
        app.workout_screen.set_current_session(session_id)
        app.screen_manager.current = 'workout'

class WorkoutScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_session_id = None
        self.build_ui()
    
    def build_ui(self):
        main_layout = MDBoxLayout(orientation='vertical', spacing=dp(0))
        
        # Perfect header
        self.header_card = PerfectHeaderCard("Workout Details")
        self.header_card.set_back_action(self.go_back)
        
        # Content
        content_layout = MDBoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16))
        
        # Workout info card
        self.info_card = MDCard(
            md_bg_color=[0.15, 0.15, 0.15, 1], elevation=4, padding=dp(20),
            size_hint_y=None, height=dp(120), radius=[16, 16, 16, 16]
        )
        
        info_layout = MDBoxLayout(orientation='vertical', spacing=dp(8))
        
        self.workout_name_label = MDLabel(
            text="Workout Name", font_size=sp(18), bold=True, size_hint_y=None, height=dp(28),
            valign="middle"
        )
        
        self.workout_date_label = MDLabel(
            text="Date • Time", font_size=sp(14), theme_text_color="Secondary",
            size_hint_y=None, height=dp(22), valign="middle"
        )
        
        self.workout_stats_label = MDLabel(
            text="0 exercises • 0 sets", font_size=sp(13), theme_text_color="Primary",
            size_hint_y=None, height=dp(20), valign="middle"
        )
        
        # Type indicator
        self.type_indicator = MDCard(
            md_bg_color=[0.55, 0.36, 0.97, 1], size_hint_y=None, height=dp(6), radius=[3, 3, 3, 3]
        )
        
        info_layout.add_widget(self.workout_name_label)
        info_layout.add_widget(self.workout_date_label)
        info_layout.add_widget(self.workout_stats_label)
        info_layout.add_widget(self.type_indicator)
        self.info_card.add_widget(info_layout)
        
        # Action buttons
        actions_layout = MDBoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(105))
        
        add_exercise_button = MDButton(
            MDButtonText(text="Add Exercise"), style="elevated", size_hint_y=None, height=dp(50),
            theme_bg_color="Custom", md_bg_color=[0.06, 0.72, 0.51, 1], on_release=self.show_add_exercise_dialog
        )
        
        # Quick add - horizontal scroll
        quick_scroll = MDScrollView(size_hint_y=None, height=dp(45))
        quick_add_layout = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(45))
        
        common_exercises = ['Bench Press', 'Squat', 'Deadlift', 'Pull-ups']
        for exercise in common_exercises:
            btn = MDButton(
                MDButtonText(text=exercise), style="outlined", size_hint_x=None, width=dp(110),
                on_release=lambda x, ex=exercise: self.quick_add_exercise(ex)
            )
            quick_add_layout.add_widget(btn)
        
        quick_scroll.add_widget(quick_add_layout)
        
        actions_layout.add_widget(add_exercise_button)
        actions_layout.add_widget(quick_scroll)
        
        # Exercises section
        exercises_header = MDLabel(
            text="Exercises", font_size=sp(18), bold=True, size_hint_y=None, height=dp(35),
            valign="middle"
        )
        
        self.exercises_scroll = MDScrollView()
        self.exercises_layout = MDBoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None, height=dp(0))
        self.exercises_scroll.add_widget(self.exercises_layout)
        
        content_layout.add_widget(self.info_card)
        content_layout.add_widget(actions_layout)
        content_layout.add_widget(exercises_header)
        content_layout.add_widget(self.exercises_scroll)
        
        main_layout.add_widget(self.header_card)
        main_layout.add_widget(content_layout)
        self.add_widget(main_layout)
    
    def set_current_session(self, session_id):
        self.current_session_id = session_id
        self.refresh_session_info()
        self.refresh_exercises()
    
    def refresh_session_info(self):
        if not self.current_session_id:
            return
        
        app = MDApp.get_running_app()
        session_data = app.db_manager.get_workout_session(self.current_session_id)
        
        if session_data:
            self.workout_name_label.text = session_data['name']
            self.workout_date_label.text = f"{session_data['date']} • {session_data.get('time', '00:00')}"
            self.header_card.set_title(session_data['name'])
            
            exercises_count = len(session_data.get('exercises', {}))
            total_sets = sum(len(ex.get('sets', {})) for ex in session_data.get('exercises', {}).values())
            self.workout_stats_label.text = f"{exercises_count} exercises • {total_sets} sets"
            
            workout_type = session_data.get('workout_type', 'Custom')
            colors = {
                'Push': [0.94, 0.35, 0.35, 1], 'Pull': [0.23, 0.51, 0.96, 1],
                'Legs': [0.06, 0.72, 0.51, 1], 'Custom': [0.55, 0.36, 0.97, 1]
            }
            self.type_indicator.md_bg_color = colors.get(workout_type, colors['Custom'])
    
    def refresh_exercises(self):
        self.exercises_layout.clear_widgets()
        self.exercises_layout.height = dp(0)
        
        if not self.current_session_id:
            return
        
        app = MDApp.get_running_app()
        session_data = app.db_manager.get_workout_session(self.current_session_id)
        
        if session_data and 'exercises' in session_data:
            exercises = session_data['exercises']
            
            if not exercises:
                self.add_exercise_empty_state()
            else:
                for exercise_id, exercise_data in exercises.items():
                    exercise_card = self.create_perfect_exercise_card(exercise_id, exercise_data)
                    self.exercises_layout.add_widget(exercise_card)
                    self.exercises_layout.height += dp(102)  # Card height + spacing
    
    def add_exercise_empty_state(self):
        empty_state = MDCard(
            md_bg_color=[0.1, 0.1, 0.1, 1], elevation=2, padding=dp(24),
            size_hint_y=None, height=dp(140), radius=[12, 12, 12, 12]
        )
        
        empty_layout = MDBoxLayout(orientation='vertical', spacing=dp(10))
        
        emoji_label = MDLabel(
            text="💪", font_size=sp(36), halign="center", valign="middle",
            size_hint_y=None, height=dp(45)
        )
        
        title_label = MDLabel(
            text="No exercises yet", font_size=sp(16), bold=True, halign="center", 
            theme_text_color="Secondary", size_hint_y=None, height=dp(25), valign="middle"
        )
        
        subtitle_label = MDLabel(
            text="Add your first exercise!", font_size=sp(13),
            halign="center", theme_text_color="Secondary", size_hint_y=None, height=dp(20),
            valign="middle"
        )
        
        empty_layout.add_widget(emoji_label)
        empty_layout.add_widget(title_label)
        empty_layout.add_widget(subtitle_label)
        
        empty_state.add_widget(empty_layout)
        self.exercises_layout.add_widget(empty_state)
        self.exercises_layout.height += dp(152)
    
    def create_perfect_exercise_card(self, exercise_id, exercise_data):
        card = MDCard(
            md_bg_color=[0.15, 0.15, 0.15, 1], elevation=4, padding=dp(16),
            size_hint_y=None, height=dp(90), radius=[12, 12, 12, 12]
        )
        
        main_layout = MDBoxLayout(orientation='horizontal', spacing=dp(12))
        
        # Exercise emoji - perfect alignment
        emoji_map = {
            'Chest': '💪', 'Back': '🎯', 'Legs': '🦵', 'Arms': '💪', 'Shoulders': '🔥', 'Core': '⚡'
        }
        emoji = emoji_map.get(exercise_data['muscle_group'], '🏋️')
        
        emoji_label = MDLabel(
            text=emoji, font_size=sp(24), size_hint_x=None, width=dp(40), 
            halign="center", valign="middle"
        )
        
        # Exercise details
        details_layout = MDBoxLayout(orientation='vertical', spacing=dp(4))
        
        name_label = MDLabel(
            text=exercise_data['name'], font_size=sp(15), bold=True, 
            size_hint_y=None, height=dp(22), valign="middle"
        )
        
        muscle_label = MDLabel(
            text=exercise_data['muscle_group'], font_size=sp(12),
            theme_text_color="Secondary", size_hint_y=None, height=dp(18), valign="middle"
        )
        
        sets_count = len(exercise_data['sets'])
        total_volume = sum(s.get('volume', 0) for s in exercise_data['sets'].values())
        
        stats_label = MDLabel(
            text=f"{sets_count} sets • {total_volume:.0f}kg", font_size=sp(11),
            theme_text_color="Primary", size_hint_y=None, height=dp(16), valign="middle"
        )
        
        details_layout.add_widget(name_label)
        details_layout.add_widget(muscle_label)
        details_layout.add_widget(stats_label)
        
        # Action buttons
        action_layout = MDBoxLayout(orientation='horizontal', size_hint_x=None, width=dp(80), spacing=dp(6))
        
        view_button = MDButton(
            MDButtonText(text="Open"), style="elevated", size_hint=(None, None), size=(dp(55), dp(32)),
            on_release=lambda x: self.view_exercise(exercise_id)
        )
        
        delete_button = MDIconButton(
            icon="delete-outline", style="standard", theme_icon_color="Custom",
            icon_color=[0.94, 0.27, 0.27, 1], size_hint=(None, None), size=(dp(32), dp(32)),
            on_release=lambda x: self.confirm_delete_exercise(exercise_id, exercise_data['name'])
        )
        
        action_layout.add_widget(view_button)
        action_layout.add_widget(delete_button)
        
        main_layout.add_widget(emoji_label)
        main_layout.add_widget(details_layout)
        main_layout.add_widget(action_layout)
        card.add_widget(main_layout)
        return card
    
    def quick_add_exercise(self, exercise_name):
        muscle_groups = {'Bench Press': 'Chest', 'Squat': 'Legs', 'Deadlift': 'Back', 'Pull-ups': 'Back'}
        muscle_group = muscle_groups.get(exercise_name, 'General')
        
        app = MDApp.get_running_app()
        exercise_id = app.db_manager.add_exercise(self.current_session_id, exercise_name, muscle_group)
        
        if exercise_id:
            self.refresh_exercises()
            self.refresh_session_info()
            app.main_screen.update_statistics()
            
            snackbar = MDSnackbar(
                MDSnackbarText(text=f"{exercise_name} added!"),
                size_hint_x=0.95, pos_hint={"center_x": 0.5}
            )
            snackbar.open()
    
    def view_exercise(self, exercise_id):
        app = MDApp.get_running_app()
        app.exercise_screen.set_current_exercise(self.current_session_id, exercise_id)
        app.screen_manager.current = 'exercise'
    
    def confirm_delete_exercise(self, exercise_id, exercise_name):
        dialog = MDDialog(
            MDDialogHeadlineText(text="Delete Exercise"),
            MDDialogSupportingText(text=f"Delete '{exercise_name}' and all its sets?"),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="CANCEL"), style="text", on_release=lambda x: dialog.dismiss()),
                MDButton(MDButtonText(text="DELETE"), style="text", theme_text_color="Custom",
                        text_color=[0.94, 0.27, 0.27, 1], on_release=lambda x: self.delete_exercise(dialog, exercise_id)),
            ),
        )
        dialog.open()
    
    def delete_exercise(self, dialog, exercise_id):
        app = MDApp.get_running_app()
        app.db_manager.delete_exercise(self.current_session_id, exercise_id)
        self.refresh_exercises()
        self.refresh_session_info()
        app.main_screen.update_statistics()
        dialog.dismiss()
        
        snackbar = MDSnackbar(
            MDSnackbarText(text="Exercise deleted successfully"),
            size_hint_x=0.95, pos_hint={"center_x": 0.5}
        )
        snackbar.open()
    
    def show_add_exercise_dialog(self, *args):
        # FIXED EXERCISE DIALOG - Properly aligned
        content = MDBoxLayout(orientation='vertical', spacing=dp(16), size_hint_y=None, height=dp(300))
        
        exercise_name_field = MDTextField(
            MDTextFieldHintText(text="Exercise name"),
            MDTextFieldHelperText(text="e.g., Bench Press, Bicep Curls"),
            size_hint_y=None, height=dp(70), font_size=sp(16)
        )
        
        # Muscle group selection
        muscle_label = MDLabel(
            text="Target muscle group:", font_size=sp(16), bold=True,
            size_hint_y=None, height=dp(30), valign="middle"
        )
        
        muscle_scroll = MDScrollView(size_hint_y=None, height=dp(170))
        muscle_layout = MDBoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        muscle_layout.bind(minimum_height=muscle_layout.setter('height'))
        
        muscle_buttons = []
        muscle_groups = [
            ('Chest', 'Chest'), ('Back', 'Back'), ('Legs', 'Legs'), 
            ('Arms', 'Arms'), ('Shoulders', 'Shoulders'), ('Core', 'Core')
        ]
        selected_muscle = ['Chest']
        
        for display_name, muscle in muscle_groups:
            btn = MDButton(
                MDButtonText(text=display_name), 
                style="outlined", 
                size_hint_y=None, 
                height=dp(48),
                on_release=lambda x, m=muscle: self.select_muscle_group(m, muscle_buttons, selected_muscle)
            )
            muscle_buttons.append(btn)
            muscle_layout.add_widget(btn)
        
        muscle_buttons[0].style = "elevated"
        muscle_scroll.add_widget(muscle_layout)
        
        content.add_widget(exercise_name_field)
        content.add_widget(muscle_label)
        content.add_widget(muscle_scroll)
        
        dialog = MDDialog(
            MDDialogHeadlineText(text="Add Exercise"),
            MDDialogSupportingText(text="Choose an exercise to add to your workout"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="CANCEL"), style="text", on_release=lambda x: dialog.dismiss()),
                MDButton(MDButtonText(text="ADD EXERCISE"), style="text",
                        on_release=lambda x: self.add_exercise(dialog, exercise_name_field.text, selected_muscle[0])),
            ),
        )
        dialog.open()
    
    def select_muscle_group(self, muscle_group, buttons, selected_muscle):
        selected_muscle[0] = muscle_group
        for btn in buttons:
            btn.style = "elevated" if btn.children[0].text == muscle_group else "outlined"
    
    def add_exercise(self, dialog, exercise_name, muscle_group):
        if not exercise_name.strip():
            snackbar = MDSnackbar(
                MDSnackbarText(text="Please enter an exercise name"),
                size_hint_x=0.95, pos_hint={"center_x": 0.5}
            )
            snackbar.open()
            return
        
        app = MDApp.get_running_app()
        exercise_id = app.db_manager.add_exercise(self.current_session_id, exercise_name.strip(), muscle_group)
        
        if exercise_id:
            self.refresh_exercises()
            self.refresh_session_info()
            app.main_screen.update_statistics()
            
            snackbar = MDSnackbar(
                MDSnackbarText(text=f"{exercise_name} added successfully!"),
                MDSnackbarActionButton(
                    MDSnackbarActionButtonText(text="ADD SET"),
                    on_release=lambda x: self.view_exercise(exercise_id)
                ),
                size_hint_x=0.95, pos_hint={"center_x": 0.5}
            )
            snackbar.open()
        
        dialog.dismiss()
    
    def go_back(self, *args):
        app = MDApp.get_running_app()
        app.screen_manager.current = 'main'
        app.main_screen.update_statistics()

class ExerciseScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_session_id = None
        self.current_exercise_id = None
        self.build_ui()
    
    def build_ui(self):
        main_layout = MDBoxLayout(orientation='vertical', spacing=dp(0))
        
        # Perfect header
        self.header_card = PerfectHeaderCard("Exercise Details")
        self.header_card.set_back_action(self.go_back)
        
        # Content
        content_layout = MDBoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16))
        
        # Exercise info card
        self.info_card = MDCard(
            md_bg_color=[0.15, 0.15, 0.15, 1], elevation=4, padding=dp(20),
            size_hint_y=None, height=dp(130), radius=[16, 16, 16, 16]
        )
        
        info_layout = MDBoxLayout(orientation='horizontal', spacing=dp(16))
        
        # Exercise emoji
        emoji_layout = MDBoxLayout(orientation='vertical', size_hint_x=None, width=dp(60))
        
        self.exercise_emoji = MDLabel(
            text="🏋️", font_size=sp(36), halign="center", valign="middle",
            size_hint_y=None, height=dp(50)
        )
        
        emoji_layout.add_widget(MDLabel())
        emoji_layout.add_widget(self.exercise_emoji)
        emoji_layout.add_widget(MDLabel())
        
        # Exercise details
        details_layout = MDBoxLayout(orientation='vertical', spacing=dp(6))
        
        self.exercise_name_label = MDLabel(
            text="Exercise Name", font_size=sp(17), bold=True, size_hint_y=None, height=dp(26),
            valign="middle"
        )
        
        self.muscle_group_label = MDLabel(
            text="Muscle Group", font_size=sp(14), theme_text_color="Secondary",
            size_hint_y=None, height=dp(20), valign="middle"
        )
        
        self.exercise_stats_label = MDLabel(
            text="0 sets • 0 total volume", font_size=sp(13), theme_text_color="Primary",
            size_hint_y=None, height=dp(18), valign="middle"
        )
        
        self.last_performed_label = MDLabel(
            text="Added just now", font_size=sp(11), theme_text_color="Secondary",
            size_hint_y=None, height=dp(16), valign="middle"
        )
        
        details_layout.add_widget(self.exercise_name_label)
        details_layout.add_widget(self.muscle_group_label)
        details_layout.add_widget(self.exercise_stats_label)
        details_layout.add_widget(self.last_performed_label)
        
        info_layout.add_widget(emoji_layout)
        info_layout.add_widget(details_layout)
        self.info_card.add_widget(info_layout)
        
        # Action buttons - perfectly aligned
        actions_layout = MDBoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(110))
        
        add_set_button = MDButton(
            MDButtonText(text="Add Set"), style="elevated", size_hint_y=None, height=dp(50),
            theme_bg_color="Custom", md_bg_color=[0.55, 0.36, 0.97, 1], on_release=self.show_add_set_dialog
        )
        
        quick_sets_button = MDButton(
            MDButtonText(text="Quick Multiple Sets"), style="outlined", size_hint_y=None, height=dp(45),
            on_release=self.show_quick_sets_dialog
        )
        
        actions_layout.add_widget(add_set_button)
        actions_layout.add_widget(quick_sets_button)
        
        # Sets section header - perfectly aligned
        sets_header_layout = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        sets_header = MDLabel(
            text="Sets", font_size=sp(18), bold=True, valign="middle"
        )
        
        self.sets_summary = MDLabel(
            text="0 completed", font_size=sp(13), theme_text_color="Secondary", 
            halign="right", valign="middle"
        )
        
        sets_header_layout.add_widget(sets_header)
        sets_header_layout.add_widget(self.sets_summary)
        
        # Sets scroll view
        self.sets_scroll = MDScrollView()
        self.sets_layout = MDBoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None, height=dp(0))
        self.sets_scroll.add_widget(self.sets_layout)
        
        # Add components
        content_layout.add_widget(self.info_card)
        content_layout.add_widget(actions_layout)
        content_layout.add_widget(sets_header_layout)
        content_layout.add_widget(self.sets_scroll)
        
        main_layout.add_widget(self.header_card)
        main_layout.add_widget(content_layout)
        self.add_widget(main_layout)
    
    def set_current_exercise(self, session_id, exercise_id):
        self.current_session_id = session_id
        self.current_exercise_id = exercise_id
        self.refresh_exercise_info()
        self.refresh_sets()
    
    def refresh_exercise_info(self):
        if not self.current_session_id or not self.current_exercise_id:
            return
        
        app = MDApp.get_running_app()
        session_data = app.db_manager.get_workout_session(self.current_session_id)
        
        if (session_data and 'exercises' in session_data and 
            self.current_exercise_id in session_data['exercises']):
            
            exercise_data = session_data['exercises'][self.current_exercise_id]
            
            self.exercise_name_label.text = exercise_data['name']
            self.muscle_group_label.text = exercise_data['muscle_group']
            self.header_card.set_title(exercise_data['name'])
            
            # Update emoji based on muscle group
            emoji_map = {
                'Chest': '💪', 'Back': '🎯', 'Legs': '🦵', 'Arms': '💪', 'Shoulders': '🔥', 'Core': '⚡'
            }
            self.exercise_emoji.text = emoji_map.get(exercise_data['muscle_group'], '🏋️')
            
            # Calculate stats
            sets = exercise_data.get('sets', {})
            total_volume = sum(s.get('volume', 0) for s in sets.values())
            sets_count = len(sets)
            
            self.exercise_stats_label.text = f"{sets_count} sets • {total_volume:.0f}kg total volume"
            self.sets_summary.text = f"{sets_count} completed"
            
            created_at = exercise_data.get('created_at', '')
            if created_at:
                self.last_performed_label.text = f"Added at {created_at}"
            else:
                self.last_performed_label.text = "Added just now"
    
    def refresh_sets(self):
        self.sets_layout.clear_widgets()
        self.sets_layout.height = dp(0)
        
        if not self.current_session_id or not self.current_exercise_id:
            return
        
        app = MDApp.get_running_app()
        session_data = app.db_manager.get_workout_session(self.current_session_id)
        
        if (session_data and 'exercises' in session_data and 
            self.current_exercise_id in session_data['exercises']):
            
            exercise_data = session_data['exercises'][self.current_exercise_id]
            sets = exercise_data.get('sets', {})
            
            if not sets:
                self.add_sets_empty_state()
            else:
                sorted_sets = sorted(sets.items(), key=lambda x: x[1]['set_number'])
                
                for set_id, set_data in sorted_sets:
                    set_card = PerfectSetCard(set_id, set_data, self)
                    self.sets_layout.add_widget(set_card)
                    self.sets_layout.height += dp(102)  # Card height + spacing
    
    def add_sets_empty_state(self):
        empty_state = MDCard(
            md_bg_color=[0.1, 0.1, 0.1, 1], elevation=2, padding=dp(24),
            size_hint_y=None, height=dp(140), radius=[12, 12, 12, 12]
        )
        
        empty_layout = MDBoxLayout(orientation='vertical', spacing=dp(10))
        
        emoji_label = MDLabel(
            text="🏋️‍♂️", font_size=sp(36), halign="center", valign="middle",
            size_hint_y=None, height=dp(45)
        )
        
        title_label = MDLabel(
            text="No sets recorded", font_size=sp(16), bold=True, halign="center", 
            theme_text_color="Secondary", size_hint_y=None, height=dp(25), valign="middle"
        )
        
        subtitle_label = MDLabel(
            text="Add your first set to start tracking!", font_size=sp(13),
            halign="center", theme_text_color="Secondary", size_hint_y=None, height=dp(20),
            valign="middle"
        )
        
        empty_layout.add_widget(emoji_label)
        empty_layout.add_widget(title_label)
        empty_layout.add_widget(subtitle_label)
        
        empty_state.add_widget(empty_layout)
        self.sets_layout.add_widget(empty_state)
        self.sets_layout.height += dp(152)
    
    def show_add_set_dialog(self, *args):
        # FIXED SET DIALOG - Properly aligned content
        content = MDBoxLayout(orientation='vertical', spacing=dp(16), size_hint_y=None, height=dp(280))
        
        # Previous set info (if available)
        app = MDApp.get_running_app()
        session_data = app.db_manager.get_workout_session(self.current_session_id)
        exercise_data = session_data['exercises'][self.current_exercise_id]
        sets = exercise_data.get('sets', {})
        
        last_weight = 0
        last_reps = 0
        if sets:
            last_set = max(sets.values(), key=lambda x: x['set_number'])
            last_weight = last_set['weight']
            last_reps = last_set['reps']
        
        # Header with set number - properly aligned
        header_label = MDLabel(
            text=f"Set {len(sets) + 1} for {exercise_data['name']}", font_size=sp(16), bold=True,
            size_hint_y=None, height=dp(30), halign="center", valign="middle"
        )
        content.add_widget(header_label)
        
        # Previous set info - properly aligned
        if sets:
            previous_info = MDLabel(
                text=f"Previous: {last_weight}kg × {last_reps} reps", font_size=sp(13),
                theme_text_color="Secondary", size_hint_y=None, height=dp(25), 
                halign="center", valign="middle"
            )
            content.add_widget(previous_info)
        
        # Input fields - properly sized
        weight_field = MDTextField(
            MDTextFieldHintText(text="Weight (kg)"),
            MDTextFieldHelperText(text="Enter the weight you're lifting"),
            text=str(last_weight) if last_weight > 0 else "", input_filter="float",
            size_hint_y=None, height=dp(70), font_size=sp(16)
        )
        
        reps_field = MDTextField(
            MDTextFieldHintText(text="Repetitions"),
            MDTextFieldHelperText(text="How many reps did you complete?"),
            text=str(last_reps) if last_reps > 0 else "", input_filter="int",
            size_hint_y=None, height=dp(70), font_size=sp(16)
        )
        
        content.add_widget(weight_field)
        content.add_widget(reps_field)
        
        # Quick weight adjustment buttons - properly aligned
        if last_weight > 0:
            quick_label = MDLabel(
                text="Quick adjustments:", font_size=sp(13), bold=True,
                theme_text_color="Secondary", size_hint_y=None, height=dp(25), valign="middle"
            )
            
            quick_buttons_layout = MDBoxLayout(orientation='horizontal', spacing=dp(6), size_hint_y=None, height=dp(40))
            increments = [-5, -2.5, 2.5, 5]
            for inc in increments:
                btn = MDButton(
                    MDButtonText(text=f"{inc:+g}kg"), style="outlined", size_hint_x=None, width=dp(70),
                    on_release=lambda x, i=inc: self.adjust_weight(weight_field, last_weight + i)
                )
                quick_buttons_layout.add_widget(btn)
            
            content.add_widget(quick_label)
            content.add_widget(quick_buttons_layout)
        
        dialog = MDDialog(
            MDDialogHeadlineText(text="Add New Set"),
            MDDialogSupportingText(text="Track your performance!"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="CANCEL"), style="text", on_release=lambda x: dialog.dismiss()),
                MDButton(MDButtonText(text="ADD SET"), style="text",
                        on_release=lambda x: self.add_set(dialog, weight_field.text, reps_field.text)),
            ),
        )
        dialog.open()
    
    def adjust_weight(self, weight_field, new_weight):
        weight_field.text = str(new_weight)
    
    def show_quick_sets_dialog(self, *args):
        # FIXED QUICK SETS DIALOG - Properly aligned
        content = MDBoxLayout(orientation='vertical', spacing=dp(16), size_hint_y=None, height=dp(240))
        
        header_label = MDLabel(
            text="Add multiple sets quickly", font_size=sp(16), bold=True,
            size_hint_y=None, height=dp(30), halign="center", valign="middle"
        )
        
        sets_field = MDTextField(
            MDTextFieldHintText(text="Number of sets"),
            MDTextFieldHelperText(text="How many sets do you want to add?"),
            text="3", input_filter="int", size_hint_y=None, height=dp(70), font_size=sp(16)
        )
        
        weight_field = MDTextField(
            MDTextFieldHintText(text="Weight (kg)"),
            MDTextFieldHelperText(text="Same weight for all sets"),
            input_filter="float", size_hint_y=None, height=dp(70), font_size=sp(16)
        )
        
        reps_field = MDTextField(
            MDTextFieldHintText(text="Reps per set"),
            MDTextFieldHelperText(text="Same reps for all sets"),
            input_filter="int", size_hint_y=None, height=dp(70), font_size=sp(16)
        )
        
        content.add_widget(header_label)
        content.add_widget(sets_field)
        content.add_widget(weight_field)
        content.add_widget(reps_field)
        
        dialog = MDDialog(
            MDDialogHeadlineText(text="Quick Add Sets"),
            MDDialogSupportingText(text="Add multiple sets with same weight and reps"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="CANCEL"), style="text", on_release=lambda x: dialog.dismiss()),
                MDButton(MDButtonText(text="ADD SETS"), style="text",
                        on_release=lambda x: self.add_multiple_sets(dialog, sets_field.text, weight_field.text, reps_field.text)),
            ),
        )
        dialog.open()
    
    def add_multiple_sets(self, dialog, num_sets, weight, reps):
        try:
            sets_count = int(num_sets) if num_sets else 0
            weight_val = float(weight) if weight else 0
            reps_val = int(reps) if reps else 0
            
            if sets_count > 0 and weight_val > 0 and reps_val > 0 and sets_count <= 10:
                app = MDApp.get_running_app()
                
                for i in range(sets_count):
                    app.db_manager.add_set(self.current_session_id, self.current_exercise_id, weight_val, reps_val)
                
                self.refresh_sets()
                self.refresh_exercise_info()
                app.main_screen.update_statistics()
                
                snackbar = MDSnackbar(
                    MDSnackbarText(text=f"Added {sets_count} sets successfully!"),
                    size_hint_x=0.95, pos_hint={"center_x": 0.5}
                )
                snackbar.open()
            else:
                snackbar = MDSnackbar(
                    MDSnackbarText(text="Please enter valid values (max 10 sets)"),
                    size_hint_x=0.95, pos_hint={"center_x": 0.5}
                )
                snackbar.open()
        except ValueError:
            snackbar = MDSnackbar(
                MDSnackbarText(text="Please enter valid numbers"),
                size_hint_x=0.95, pos_hint={"center_x": 0.5}
            )
            snackbar.open()
        
        dialog.dismiss()
    
    def add_set(self, dialog, weight, reps):
        try:
            weight_val = float(weight) if weight else 0
            reps_val = int(reps) if reps else 0
            
            if weight_val > 0 and reps_val > 0:
                app = MDApp.get_running_app()
                set_id = app.db_manager.add_set(self.current_session_id, self.current_exercise_id, weight_val, reps_val)
                
                if set_id:
                    self.refresh_sets()
                    self.refresh_exercise_info()
                    app.main_screen.update_statistics()
                    
                    snackbar = MDSnackbar(
                        MDSnackbarText(text=f"Set added: {weight_val}kg × {reps_val} reps"),
                        MDSnackbarActionButton(
                            MDSnackbarActionButtonText(text="ADD ANOTHER"),
                            on_release=lambda x: self.show_add_set_dialog()
                        ),
                        size_hint_x=0.95, pos_hint={"center_x": 0.5}
                    )
                    snackbar.open()
            else:
                snackbar = MDSnackbar(
                    MDSnackbarText(text="Please enter valid weight and reps"),
                    size_hint_x=0.95, pos_hint={"center_x": 0.5}
                )
                snackbar.open()
        except ValueError:
            snackbar = MDSnackbar(
                MDSnackbarText(text="Please enter valid numbers"),
                size_hint_x=0.95, pos_hint={"center_x": 0.5}
            )
            snackbar.open()
        
        dialog.dismiss()
    
    def go_back(self, *args):
        app = MDApp.get_running_app()
        app.screen_manager.current = 'workout'

class FitnessTrackerApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "FitTracker Pro"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.material_style = "M3"
        self.db_manager = DatabaseManager()
        
    def build(self):
        self.screen_manager = MDScreenManager()
        
        self.main_screen = MainScreen(name='main')
        self.workout_screen = WorkoutScreen(name='workout')
        self.exercise_screen = ExerciseScreen(name='exercise')
        
        self.screen_manager.add_widget(self.main_screen)
        self.screen_manager.add_widget(self.workout_screen)
        self.screen_manager.add_widget(self.exercise_screen)
        
        self.screen_manager.current = 'main'
        
        Clock.schedule_once(self.initialize_app, 0.1)
        
        return self.screen_manager
    
    def initialize_app(self, dt):
        self.db_manager.create_tables()
        self.main_screen.update_statistics()
        
        Clock.schedule_once(self.show_welcome_message, 1.5)
    
    def show_welcome_message(self, dt):
        if not self.db_manager.get_workout_sessions():
            snackbar = MDSnackbar(
                MDSnackbarText(text="Welcome to FitTracker Pro! Ready to start your fitness journey?"),
                MDSnackbarActionButton(
                    MDSnackbarActionButtonText(text="GET STARTED"),
                    on_release=lambda x: self.main_screen.show_new_workout_dialog()
                ),
                size_hint_x=0.95, pos_hint={"center_x": 0.5}, auto_dismiss=False
            )
            snackbar.open()

if __name__ == '__main__':
    FitnessTrackerApp().run()