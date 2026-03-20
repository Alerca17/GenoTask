"""Package entry point for the GenoTask Alien Landing GA."""

try:
    from alien_lander_ga.gui.app import App
except ModuleNotFoundError:
    # Allow running as: `python main.py` from inside `alien_lander_ga/`.
    import os
    import sys

    package_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if package_parent not in sys.path:
        sys.path.insert(0, package_parent)
    from alien_lander_ga.gui.app import App


def run() -> None:
    app = App()
    app.run()


if __name__ == "__main__":
    run()
