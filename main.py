import tkinter as tk
from gui import ContactManagerApp
import os
from dotenv import load_dotenv


def main():
    # Load environment variables
    load_dotenv()

    # Create the GUI application
    root = tk.Tk()
    app = ContactManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()