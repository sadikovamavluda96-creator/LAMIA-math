import math
import ast
import operator as op

from kivy.app import App
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

Window.clearcolor = (0.95, 0.94, 1, 1)

PURPLE = (0.36, 0.16, 0.62, 1)
LIGHT_BLUE = (0.72, 0.86, 1, 1)
WHITE = (1, 1, 1, 1)
DARK = (0.12, 0.08, 0.18, 1)

ALLOWED = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "sqrt": math.sqrt, "log": math.log10, "ln": math.log,
    "exp": math.exp, "abs": abs,
    "pi": math.pi, "e": math.e,
    "factorial": math.factorial
}

BIN_OPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
    ast.Div: op.truediv, ast.Pow: op.pow, ast.Mod: op.mod,
}

UNARY_OPS = {ast.UAdd: op.pos, ast.USub: op.neg}

def safe_eval(expression):
    expression = expression.replace("×", "*").replace("÷", "/").replace("^", "**")
    expression = expression.replace("π", "pi")

    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value

        if isinstance(node, ast.Name) and node.id in ALLOWED:
            return ALLOWED[node.id]

        if isinstance(node, ast.BinOp) and type(node.op) in BIN_OPS:
            left = evaluate(node.left)
            right = evaluate(node.right)
            return BIN_OPS[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPS:
            return UNARY_OPS[type(node.op)](evaluate(node.operand))

        if isinstance(node, ast.Call):
            func = evaluate(node.func)
            args = [evaluate(a) for a in node.args]
            return func(*args)

        raise ValueError("Invalid expression")

    return evaluate(tree)

class CalcButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = sp(18)
        self.bold = True
        self.background_normal = ""
        self.background_color = kwargs.pop("button_color", LIGHT_BLUE)
        self.color = kwargs.pop("text_color", DARK)
        self.size_hint_y = None
        self.height = dp(48)

class LamiaCalculator(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(10), spacing=dp(7), **kwargs)

        title = Label(
            text="[b]LAMIA CALCULATOR[/b]",
            markup=True,
            font_size=sp(23),
            color=PURPLE,
            size_hint_y=None,
            height=dp(42)
        )
        self.add_widget(title)

        self.display = TextInput(
            text="",
            multiline=False,
            readonly=True,
            halign="right",
            font_size=sp(27),
            foreground_color=DARK,
            background_color=WHITE,
            size_hint_y=None,
            height=dp(62),
            padding=[dp(10), dp(12)]
        )
        self.add_widget(self.display)

        self.history = []
        self.history_label = Label(
            text="",
            color=(0.25, 0.20, 0.30, 1),
            font_size=sp(13),
            halign="left",
            valign="top",
            size_hint_y=None
        )
        self.history_label.bind(texture_size=self.history_label.setter("size"))

        scroll = ScrollView(size_hint_y=None, height=dp(72))
        scroll.add_widget(self.history_label)
        self.add_widget(scroll)

        grid = GridLayout(cols=5, spacing=dp(5), size_hint_y=1)

        buttons = [
            ("C", "clear", PURPLE, WHITE), ("⌫", "back", PURPLE, WHITE),
            ("(", "(", LIGHT_BLUE, DARK), (")", ")", LIGHT_BLUE, DARK),
            ("÷", "÷", PURPLE, WHITE),

            ("sin", "sin(", LIGHT_BLUE, DARK), ("cos", "cos(", LIGHT_BLUE, DARK),
            ("tan", "tan(", LIGHT_BLUE, DARK), ("√", "sqrt(", LIGHT_BLUE, DARK),
            ("^", "^", PURPLE, WHITE),

            ("7", "7", LIGHT_BLUE, DARK), ("8", "8", LIGHT_BLUE, DARK),
            ("9", "9", LIGHT_BLUE, DARK), ("×", "×", PURPLE, WHITE),
            ("π", "π", LIGHT_BLUE, DARK),

            ("4", "4", LIGHT_BLUE, DARK), ("5", "5", LIGHT_BLUE, DARK),
            ("6", "6", LIGHT_BLUE, DARK), ("−", "-", PURPLE, WHITE),
            ("e", "e", LIGHT_BLUE, DARK),

            ("1", "1", LIGHT_BLUE, DARK), ("2", "2", LIGHT_BLUE, DARK),
            ("3", "3", LIGHT_BLUE, DARK), ("+", "+", PURPLE, WHITE),
            ("=", "=", PURPLE, WHITE),

            ("0", "0", LIGHT_BLUE, DARK), (".", ".", LIGHT_BLUE, DARK),
            ("log", "log(", LIGHT_BLUE, DARK), ("ln", "ln(", LIGHT_BLUE, DARK),
            ("x!", "factorial(", LIGHT_BLUE, DARK),
        ]

        for text, value, color, text_color in buttons:
            btn = CalcButton(text=text, button_color=color, text_color=text_color)
            btn.bind(on_press=lambda b, v=value: self.press(v))
            grid.add_widget(btn)

        self.add_widget(grid)

    def press(self, value):
        if value == "clear":
            self.display.text = ""
            return

        if value == "back":
            self.display.text = self.display.text[:-1]
            return

        if value == "=":
            expression = self.display.text
            if not expression:
                return
            try:
                result = safe_eval(expression)
                if isinstance(result, float):
                    if result.is_integer():
                        result = int(result)
                    else:
                        result = round(result, 10)
                self.history.insert(0, f"{expression} = {result}")
                self.history = self.history[:10]
                self.history_label.text = "\n".join(self.history)
                self.display.text = str(result)
            except Exception:
                self.display.text = "Error"
            return

        if self.display.text == "Error":
            self.display.text = ""

        self.display.text += value

class LAMIAApp(App):
    title = "LAMIA Calculator"

    def build(self):
        return LamiaCalculator()

if __name__ == "__main__":
    LAMIAApp().run()
