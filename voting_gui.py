import requests
import json
import wx
from wx.adv import Sound

def req(method, url, data=None, headers=None, sounds=True):
	resp = method(url, data=data, headers=headers)
	print(resp.status_code, url, "\n")
	if str(resp.status_code).startswith("2"):
		if sounds:
			Sound("sounds/success.wav").Play(wx.adv.SOUND_ASYNC)
		return json.loads(resp.text)
	else:
		if sounds:
			Sound("sounds/error.wav").Play(wx.adv.SOUND_ASYNC)
		return [resp.status_code, resp.text]


class Window(wx.Frame):
	def __init__(self, title, **kwargs):
		super(Window, self).__init__(parent=None, id=wx.ID_ANY, title=title, **kwargs)
		self.polls = req(requests.get, API_ROOT + "polls/", headers={"Authorization": "Token " + TOKEN}, sounds=False)
		self._initialize()
		for index, poll in enumerate(self.polls):
			self.poll_list.Append(poll["title"], clientData=index)
		self.poll_list.SetSelection(0)
		self.show_questions(event=None)

	def _initialize(self):
		panel = wx.Panel(self)
		panel.SetLabel(self.GetTitle())
		poll_list_label = wx.StaticText(panel, label="&Ankete")
		self.poll_list = wx.ListBox(panel, style=wx.LB_SINGLE|wx.LB_NEEDED_SB)
		self.poll_list.Bind(wx.EVT_LISTBOX, self.show_questions)
		poll_questions_label = wx.StaticText(panel, label="&Pitanja")
		self.poll_questions = wx.Choice(panel)
		self.poll_questions.Bind(wx.EVT_CHOICE, self.show_choices)
		poll_question_choices_label = wx.StaticText(panel, label="&Opcije")
		self.poll_question_choices = wx.Choice(panel)
		vote_button = wx.Button(panel, label="&Glasaj")
		vote_button.Bind(wx.EVT_BUTTON, self.on_vote)
		sizer = wx.GridBagSizer(5, 10)
		sizer.Add(poll_list_label, (0, 0), (1, 1))
		sizer.Add(self.poll_list, (1, 0), (1, 1), flag=wx.EXPAND|wx.ALL)
		right_sizer = wx.BoxSizer(wx.VERTICAL)
		right_sizer.Add(poll_questions_label)
		right_sizer.Add(self.poll_questions, flag=wx.EXPAND|wx.ALL)
		right_sizer.Add(poll_question_choices_label)
		right_sizer.Add(self.poll_question_choices, flag=wx.EXPAND|wx.ALL)
		right_sizer.Add(vote_button, flag=wx.ALIGN_CENTER|wx.ALL)
		sizer.Add(right_sizer, (1, 1), (1, 1), wx.EXPAND)
		sizer.AddGrowableRow(1)
		panel.SetSizerAndFit(sizer)
		self.Fit()
		self.Center()
		self.Show()

	def show_questions(self, event):
		self.poll_questions.Clear()
		for index, question in enumerate(self.polls[self.poll_list.GetClientData(self.poll_list.GetSelection())]["questions"]):
			self.poll_questions.Append(question["question_text"], clientData=index)
		self.poll_questions.SetSelection(0)
		self.show_choices(event=None)

	def show_choices(self, event):
		self.poll_question_choices.Clear()
		for choice in self.polls[self.poll_list.GetClientData(self.poll_list.GetSelection())]["questions"][self.poll_questions.GetClientData(self.poll_questions.GetSelection())]["choices"]:
			self.poll_question_choices.Append(choice["choice_text"], clientData=choice["id"])
		self.poll_question_choices.SetSelection(0)

	def on_vote(self, event):
		vote = req(requests.patch, API_ROOT + "polls/vote/" + str(self.poll_question_choices.GetClientData(self.poll_question_choices.GetSelection())) + "/", headers=HEADERS)


app = wx.App()
APP_TITLE = "DP Ankete"
# METHODS = {"GET": requests.get, "POST": requests.post, "PUT": requests.put, "PATCH": requests.patch, "DELETE": requests.delete}
API_ROOT = "https://dp95.pythonanywhere.com/api/"
with wx.TextEntryDialog(None, "Unesite korisničko ime za pristup API-ju", "Korisničko ime") as username_dlg:
	if username_dlg.ShowModal() == wx.ID_OK:
		USERNAME = username_dlg.GetValue()
		with wx.PasswordEntryDialog(None, "Unesite lozinku za pristup API-ju", "Lozinka") as password_dlg:
			if password_dlg.ShowModal() == wx.ID_OK:
				PASSWORD = password_dlg.GetValue()
				TOKEN = req(requests.post, API_ROOT + "auth/token/login/", data={"username": USERNAME, "password": PASSWORD}, sounds=False)["auth_token"]
				HEADERS = {"Authorization": "Token " + TOKEN}
w = Window(APP_TITLE)
app.MainLoop()
