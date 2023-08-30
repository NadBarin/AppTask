from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatIconButton
from kivy.uix.button import Button
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.pickers import MDDatePicker
from datetime import datetime
from kivymd.uix.list import TwoLineAvatarIconListItem, ILeftBodyTouch
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.bottomsheet import MDBottomSheet
from database import Database
from datetime import timedelta
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

from backend_kivyagg import FigureCanvasKivyAgg

db = Database()
KV = '''
<DrawerClickableItem@MDNavigationDrawerItem>
    focus_color: "#e7e4c0"
    text_color: "#fffafa"
    icon_color: "#4a4939"
    ripple_color: "#c5bdd2"
    selected_color: "#0c6c4d"

<Tab>
    MDLabel:
        id: label
        halign: "center"  
<DialogContent>:
    orientation: "vertical"
    spacing: "10dp"
    size_hint: 1, None
    height: "130dp"

    GridLayout:
        rows: 1

        MDTextField:
            id: task_text
            hint_text: "Add Task..."
            pos_hint: {"center_y": .4}
            max_text_length: 50
            on_text_validate: (app.add_task(task_text, date_text.text), app.close_dialog())

        MDIconButton:
            icon: 'calendar'
            on_release: root.show_date_picker()
            padding: '10dp'

    MDLabel:
        spacing: '10dp'
        id: date_text

    BoxLayout:
        orientation: 'horizontal'

        MDRaisedButton:
            text: "SAVE"
            on_release: (app.add_task(task_text, date_text.text), app.close_dialog())
        MDFlatButton:
            text: 'CANCEL'
            on_release: app.close_dialog()
<ListItemWithCheckbox>:
    id: the_list_item
    markup: True
    LeftCheckbox:
        id: check
        on_release: 
            root.mark(check, the_list_item)
    IconRightWidget:
        icon: 'dots-vertical'
        on_release: 
            root.show_list_bottom_sheet(the_list_item)
MDScreen:
    MDNavigationLayout:
        MDScreenManager:
            id: screen_manager
            MDScreen:
                name: "scr 1"
                MDBoxLayout:
                    orientation: "vertical"
                    MDTopAppBar:
                        title: f"Your own tasks"
                        elevation: 4
                        pos_hint: {"top": 1}
                        #md_bg_color: "#e7e4c0"
                        #specific_text_color: "#4a4939"
                        left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]
                    MDTabs:
                        lock_swiping: True
                        id: tabs
                        on_tab_switch: app.on_tab_switch(*args)
                        Tab:
                            id: Tasks
                            title: "Tasks"
                            ScrollView:
                                #pos_hint: {'center_y': .6, 'center_x': .5}
                                #size_hint: .9, .8
                                MDList:
                                    id: container
                            MDFillRoundFlatButton:
                                text: "+"
                                font_size : 40
                                on_release: app.show_task_dialog() #functionality to be added later
                                pos_hint: {'x': .8, 'y':.05}  
                        Tab:
                            id: Schedule
                            title: "Schedule"
                            ScrollView:
                                do_scroll_y: True
                                do_scroll_x: True
                                BoxLayout: 
                                    id:layout 
                                    adaptive_height: True
                                    adaptive_height: True
                        Tab:
                            id: Productivity
                            title: "Productivity"
                            ScrollView:
                                do_scroll_y: True
                                do_scroll_x: True
                                BoxLayout: 
                                    id:layout2 
                                    adaptive_height: True
                                    adaptive_width: True
            MDScreen:
                name: "scr 2"
                MDBoxLayout:
                    orientation: "vertical"
                    MDTopAppBar:
                        title: f"Your coop tasks"
                        elevation: 4
                        pos_hint: {"top": 1}
                        #md_bg_color: "#e7e4c0"
                        #specific_text_color: "#4a4939"
                        left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]
                    MDTabs:
                        id: tabs
                        on_tab_switch: app.on_tab_switch(*args)
                        Tab:
                            id: coop_Tasks
                            title: "Tasks"
                        Tab:
                            id: coop_Schedule
                            title: "Schedule"
                        Tab:
                            id: coop_Productivity
                            title: "Productivity"
        MDNavigationDrawer:
            id: nav_drawer
            radius: (0, 16, 16, 0)
            MDNavigationDrawerMenu:
                MDNavigationDrawerHeader:
                    title: "Task manager"
                    #title_color: "#ffffff"
                    spacing: "4dp"
                    padding: "12dp", 0, 0, "56dp"
                MDNavigationDrawerLabel:
                    text: "menu"
                DrawerClickableItem:
                    text: "Your own tasks"
                    text_color: "#00000"
                    on_press:
                        nav_drawer.set_state("close")
                        screen_manager.current = "scr 1"          
                DrawerClickableItem:
                    text: "Your coop tasks"
                    text_color: "#00000"
                    on_press:
                        nav_drawer.set_state("close")
                        screen_manager.current = "scr 2"
'''
class Tab(MDFloatLayout, MDTabsBase):
    pass
class MenuHeader(MDBoxLayout):
    pass

class ListItemWithCheckbox (TwoLineAvatarIconListItem):
    def __init__(self, pk=None, level=0, **kwargs):
        super().__init__(**kwargs)
        self.pk = pk
        self.level = level
    def callback_for_Delete_task(self,bottom_sheet_menu,the_list_item):
        data=db.delete_task(the_list_item.pk)
        c=[]
        a=[]
        for i in range(len(self.parent.children)):
            a.append(self.parent.children[i].pk)
        if (data!=0):
            for i in range(len(a)):
                for j in range(len(data)):
                    if (a[i]==data[j][0]):
                        c.append(int(i))
            for i in reversed(c):
                self.parent.remove_widget(self.parent.children[i])
        self.parent.remove_widget(the_list_item)
        bottom_sheet_menu.dismiss()

    def show_list_bottom_sheet(self,the_list_item):
        bottom_sheet_menu = MDBottomSheet()
        #bottom_sheet_menu.add_widget(
        #    Button(
        #        text="Add Subtask", icon="plus", on_press=TaskManager().callback_for_Add_Subtask(bottom_sheet_menu, the_list_item)
        #    )
        #)
        #bottom_sheet_menu.add_widget(
        #    Button(
        #        text="Delete task", icon="trash-can-outline",
        #        on_press=self.callback_for_Delete_task(bottom_sheet_menu, the_list_item)
        #    )
        #)

        bottom_sheet_menu.open()
        bottom_sheet_menu.sheet_list.ids.box_sheet_list.padding = (16, 0, 16, 0)

    def mark(self, check, the_list_item):
        t = ''
        for j in range(the_list_item.level):
            t = t + '       '
        if check.active == True:
            the_list_item.text = t+'[s]' + the_list_item.text[len(t):len(the_list_item.text)] + '[/s]'
            db.mark_task_as_complete(the_list_item.pk, str(datetime.now().strftime('%A %d %B %Y')))# here
        else:
            the_list_item.text = t+str(db.mark_task_as_incomplete(the_list_item.pk))# Here
class LeftCheckbox(ILeftBodyTouch, MDCheckbox): #Custom left container
    pass
class DialogContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.date_text.text = str(datetime.now().strftime('%A %d %B %Y'))
    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save)
        date_dialog.open()
    def on_save(self, instance, value, date_range):
        date = value.strftime('%A %d %B %Y')
        self.ids.date_text.text = str(date)
class TaskManager(MDApp):
    f=0
    l=0
    pr=0
    task_list_dialog = None
    def build(self):
        self.theme_cls.primary_palette = "Cyan"
        self.theme_cls.theme_style = "Light"
        return Builder.load_string(KV)

    def callback_for_Add_Subtask(self, bottom_sheet_menu, the_list_item):
        TaskManager.f = 1
        TaskManager.l = the_list_item.level + 1
        TaskManager.pr = the_list_item.pk
        bottom_sheet_menu.dismiss()
        self.show_task_dialog()
    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        if (tab_text=='Schedule'):
            self.root.ids.layout.clear_widgets()
            self.print_gant_graph()
        if (tab_text=='Productivity'):
            self.root.ids.layout2.clear_widgets()
            self.print_prod_graph()
    def on_start(self):
        try:
            t=''
            tasks_view = db.get_tasks()
            for i in range(len(tasks_view)):
                for j in range(tasks_view[i][5]):
                    t=t+'       '
                if (tasks_view[i][6]==0):
                    add_task = ListItemWithCheckbox(pk=tasks_view[i][0], text=t+tasks_view[i][1], secondary_text=t+tasks_view[i][2],level=tasks_view[i][5])
                    self.root.ids.container.add_widget(add_task)
                else:
                    add_task = ListItemWithCheckbox(pk=tasks_view[i][0], text=t+'[s]' + tasks_view[i][1] + '[/s]', secondary_text=t+tasks_view[i][2],level=tasks_view[i][5])
                    add_task.ids.check.active = True
                    self.root.ids.container.add_widget(add_task)
                t=''
        except Exception as e:
            print(e)
            pass
    def show_task_dialog(self):
        TaskManager.task_list_dialog = None
        if not TaskManager.task_list_dialog:
            TaskManager.task_list_dialog = MDDialog(
                title="Create Task",
                type="custom",
                content_cls=DialogContent(),
            )
        TaskManager.task_list_dialog.open()
    def close_dialog(self):
        TaskManager.task_list_dialog.dismiss()
    def add_task(self, task, task_date):
        if (self.f==0):
            db.create_task(task.text, task_date,0,0,None)  # Here
            self.root.ids.container.clear_widgets()
            self.on_start()
        else:
            db.create_task(task.text, task_date, TaskManager.pr,TaskManager.l,None)  # Here
            self.root.ids.container.clear_widgets()
            self.on_start()
        TaskManager.f=0
        task.text = ''
    def print_gant_graph(self):
        tasks=[]
        e=[]
        end=[]
        try:
            uncomplete_tasks = []
            completed_tasks = []
            tasks_view = db.get_tasks()
            for i in range(len(tasks_view)):
                if (tasks_view[i][6] == 1):
                    completed_tasks.append(tasks_view[i])
                else:
                    uncomplete_tasks.append(tasks_view[i])
            if uncomplete_tasks != []:
                for task in uncomplete_tasks:
                    tasks.append(task[1])
                    en = datetime.strptime(task[2], '%A %d %B %Y')
                    date = datetime.now()
                    later = (en.date() - date.date())
                    e.append(later / timedelta(days=1))
                    end.append(en)
                e = np.array(e)
                end = np.array(end)
                fig, ax = plt.subplots(1, 1)
                font_dictA = {"va": "center", "ha": "right", "rotation": 0, "wrap": True, "fontsize": 25}
                font_dictB = {"va": "center", "ha": "right", "rotation": 90, "wrap": True, "fontsize": 25}
                ax.barh(tasks, e, left=0)
                xticks_labels = pd.date_range(date, end=end.max() + timedelta(days=1)).strftime("%m/%d/%y")
                xticks_minor = np.arange(0, e.max(), 1)
                ax.set_yticks(tasks)
                ax.set_yticklabels(labels=tasks, fontdict= font_dictA)
                if (e.max() > 365 * 3):
                    xticks = np.arange(0, e.max()+ 1, 365)
                    ax.set_xticks(xticks)
                    ax.set_xticklabels(xticks_labels[::365], fontdict=font_dictB)
                elif (e.max() > 365):
                    xticks = np.arange(0, e.max()+ 1, 90)
                    ax.set_xticks(xticks)
                    ax.set_xticklabels(xticks_labels[::90], fontdict=font_dictB)
                elif (e.max() >182):
                    xticks = np.arange(0, e.max() + 1, 30)
                    ax.set_xticks(xticks)
                    ax.set_xticklabels(xticks_labels[::30], fontdict=font_dictB)
                elif (e.max() > 30):
                    xticks = np.arange(0, e.max() + 1, 7)
                    ax.set_xticks(xticks)
                    ax.set_xticks(xticks_minor, minor=True)
                    ax.set_xticklabels(xticks_labels[::7], fontdict=font_dictB)
                else:
                    xticks = np.arange(0, e.max() + 1, 3)
                    ax.set_xticks(xticks)
                    ax.set_xticks(xticks_minor, minor=True)
                    ax.set_xticklabels(xticks_labels[::3], fontdict=font_dictB)
                fig.tight_layout()
                if ((len(tasks))>30):
                    self.root.ids.layout.adaptive_height=False
                    self.root.ids.layout.size_hint_y=None
                    self.root.ids.layout.height = int((len(tasks))*(len(tasks)))
                else:
                    self.root.ids.layout.height = self.root.height
                self.root.ids.layout.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        except Exception as e:
            print(e)
            pass
    def print_prod_graph(self):
        try:
            k=0
            completed_tasks = []
            tasks_view = db.get_tasks()
            for i in range(len(tasks_view)):
                if (tasks_view[i][6] == 1):
                    completed_tasks.append(tasks_view[i])
            k = int(len(tasks_view))
            if (completed_tasks != []):
                plt.rcParams['font.size'] = '25'
                t = [0,0,0,0]
                dates = []
                font_dictA = {"va": "top", "ha": "center", "rotation": 0, "wrap": True, "fontsize": 25}
                for task in completed_tasks:
                    dates.append(task[3])
                fig, ax = plt.subplots(4, 1)
                fig.suptitle('Сompleted tasks from all for', fontsize=30, fontweight='bold', fontdict= font_dictA)
                for i in range(len(dates)):
                    if (str(datetime.now().strftime('%A %d %B %Y'))==dates[i]):
                        t[0] += 1
                ax[0].bar(1,t[0])
                ax[0].FontSize = 25
                ax[0].set_title('Day',fontdict= font_dictA)
                today = datetime.today()
                for i in range(len(dates)):
                    if ((today - timedelta(datetime.weekday(today)) <= today) and (today + timedelta(6 - (datetime.weekday(today))) >= today)):
                        t[1] += 1
                ax[1].bar(1,  t[1])
                ax[1].set_title('Week',fontdict= font_dictA)
                for i in range(len(dates)):
                    en = datetime.strptime(dates[i], '%A %d %B %Y')
                    if (en.month==datetime.today().month):
                        t[2]+=1
                ax[2].bar(1, t[2])
                ax[2].set_title('Month',fontdict= font_dictA)
                for i in range(len(dates)):
                    en = datetime.strptime(dates[i], '%A %d %B %Y')
                    if (en.year == datetime.today().year):
                        t[3] += 1
                ax[3].bar(1, t[3])
                ax[3].set_title('Year',fontdict= font_dictA)
                for i in range(4):
                    ax[i].set_xlim([0, 2])
                    ax[i].set_ylim([0, k])
                    ax[i].locator_params(axis='x', nbins=2)
                    ax[i].locator_params(axis='y', nbins=k + 1)
                    ax[i].get_xaxis().set_visible(False)
                    ax[i].text(x=1, y=int(k/2), s=str(round(((t[i]/k)*100),2))+'%', horizontalalignment = 'center', fontsize = 30)
                if (k>1000):
                    yticks = np.arange(0, k,1000)
                    for i in range(4):
                        if (k - yticks.max() < 1000):
                            yticks = np.delete(yticks, len(yticks) - 1)
                        yticks = np.append(yticks, k)
                        ax[i].set_yticks(yticks)
                elif (k>100):
                    yticks = np.arange(0, k, 100)
                    if (k-yticks.max()<100):
                        yticks=np.delete(yticks,len(yticks)-1)
                    yticks =np.append(yticks,k)
                    for i in range(4):
                        ax[i].set_yticks(yticks)
                elif (k>20):
                    yticks = np.arange(0, k, 10)
                    if (k-yticks.max()<5):
                        yticks=np.delete(yticks,len(yticks)-1)
                    yticks =np.append(yticks,k)
                    yticks_minor = np.arange(0, k, 5)
                    for i in range(4):
                        ax[i].set_yticks(yticks_minor, minor=True)
                        ax[i].set_yticks(yticks)
                elif (k>5):
                    yticks = np.arange(0, k, 5)
                    yticks_minor = np.arange(0, k, 1)
                    for i in range(4):
                        ax[i].set_yticks(yticks_minor, minor=True)
                        ax[i].set_yticks(yticks)
                #fig.tight_layout()
                self.root.ids.layout2.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        except Exception as e:
            print(e)
            pass
TaskManager().run()