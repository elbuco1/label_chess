

class StartPageView(base.View):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        self.minsize = 25
        self.buttons = {}

        self.config_window()

    def create_view(self):
        """Create all app's widgets
        """
        self.container = tk.LabelFrame(self, text="Menu")
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)
        self.container.grid(row=0, column=0,
                            sticky="nsew")

        self.buttons["video"] = tk.Button(
            master=self.container,
            text="Download Game Video"
        )
        self.buttons["video"].grid(row=0, column=0, sticky="nsew")

        self.buttons["pgn"] = tk.Button(
            master=self.container,
            text="Download Game PGN"
        )
        self.buttons["pgn"].grid(row=1, column=0, sticky="nsew")

        self.buttons["annotation"] = tk.Button(
            master=self.container,
            text="Annotate"
        )
        self.buttons["annotation"].grid(row=2, column=0, sticky="nsew")

    def config_window(self):
        """Configure app's root node (tk.Tk()) i.e., self
        """
        self.rowconfigure(0, minsize=self.minsize, weight=1)
        self.columnconfigure(0, minsize=self.minsize, weight=1)
        self.grid(row=0, column=0, sticky="nsew")
        self.master.title("Chess annotator")
