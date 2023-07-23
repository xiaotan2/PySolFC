import os
import time

from pysollib.mfxutil import KwStruct
from pysollib.mfxutil import format_time
from pysollib.mygettext import _
from pysollib.settings import TOP_TITLE
from pysollib.stats import ProgressionFormatter, PysolStatsFormatter
from pysollib.ui.tktile.tkutil import bind, loadImage

from six.moves import tkinter
from six.moves import tkinter_font
from six.moves import tkinter_ttk as ttk

from .tkwidget import MfxDialog, MfxMessageDialog


# ************************************************************************
# *
# ************************************************************************
class Leaderboard(MfxDialog):
    def __init__(self, parent, app, game, player, **kw):
        try:
            player_scores = game.get_leaderboard()
            player_scores = sorted(player_scores, key=lambda p: p["score"], reverse=True)
        except Exception as e:
            player_scores = None
            print(e)
        
        kw = self.initKw(kw)
        title = _('Leaderboard')
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)

        self.font = app.getFont('default')
        self.tkfont = tkinter_font.Font(parent, self.font)
        self.font_metrics = self.tkfont.metrics()
        style = ttk.Style(parent)
        heading_font = style.lookup('Heading', 'font')  # treeview heading
        heading_tkfont = tkinter_font.Font(parent, heading_font)

        top_frame, bottom_frame = self.createFrames(kw)
        tkinter.Label(top_frame, text="Global leaderboard scores").grid(column=0, row=0)

        table_frame = tkinter.Frame(top_frame)
        table_frame.grid(column=0, row=1, padx=10, pady=10)

        e = tkinter.Entry(table_frame, width=40, font=heading_tkfont)
        e.grid(row=0, column=0)
        e.insert(tkinter.END, "Player Name")

        e = tkinter.Entry(table_frame, width=20, font=heading_tkfont)
        e.grid(row=0, column=1)
        e.insert(tkinter.END, "Score")

        for idx, player in enumerate(player_scores):
            e = tkinter.Entry(table_frame, width=40)
            e.grid(row=idx + 1, column=0)
            e.insert(tkinter.END, player["player"])

            e = tkinter.Entry(table_frame, width=20)
            e.grid(row=idx + 1, column=1)
            e.insert(tkinter.END, player["score"])

        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)

    def initKw(self, kw):
        kw = KwStruct(
            kw,
            strings=(_("&OK"),),
            default=0,
            separator=False,
        )
        return MfxDialog.initKw(self, kw)

    def mDone(self, button):
        MfxDialog.mDone(self, button)
