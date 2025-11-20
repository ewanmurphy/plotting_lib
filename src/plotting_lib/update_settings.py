import os
from typing import List, Optional
import matplotlib as mpl
import matplotlib.pyplot as plt

colors_rsb = [
    "#C22C1E",  # red
    "#009B9E",  # teal
    "#F5B34C",  # orange
    "#E986DF",  # pinkish
    "#4ADA75",  # green
    "#7f7f7f",  # gray
    "#021373",
    "#F5D596",
    "#935EEB",  # purple
    "#F23064",  # sete pink
    "#F58C56",
]

def update_settings(
    usetex: Optional[bool] = False,
    style: Optional[str] = "APS",
    colors: Optional[List] = None,
    latex_preamble: Optional[str] = None,
    settings: Optional[dict] = None,
):
    """

    Parameters:
    -----------
    usetex: bool
        If True, use LaTeX for text rendering. Default is False.

    style: str
        Choose journal style of the plots. Default is 'APS'.
        Available options are:
        - 'APS': American Physical Society style
        - 'Nature': Nature style
        - 'Quantum': Quantum style

    colors: List
        List of colors to use in the plots. Default is None.
        If None, the default color cycle is used.

    latex_preamble: str
        LaTeX preamble to use in the plots. Default is None.
        If None, the default preamble is used.

    settings: dict
        Dictionary of settings to update. Default is None.
        If None, no additional settings are updated.

    """

    # make style available in the module through self.current_style
    update_settings.current_style = style.lower()

    if not latex_preamble:
        from .latex_preamble import latex_preamble

    if usetex:
        texparams = {  # 'backend': 'PDF',
            "text.usetex": True,
            "text.latex.preamble": latex_preamble,
        }
        plt.rcParams["font.family"] = "Computer Modern"
        plt.rcParams.update(texparams)

    if colors is not None:
        plt.rcParams["axes.prop_cycle"] = mpl.cycler(color=colors)
    else:
        plt.rcParams["axes.prop_cycle"] = mpl.cycler(color=colors_rsb)

    # find all available styles in the styles folder
    available_styles = os.listdir(
        os.path.join(os.path.dirname(__file__), "journal_styles")
    )
    available_styles = [
        x.split(".")[0] for x in available_styles if x.endswith(".mplstyle")
    ]

    if not style.lower() in available_styles:
        raise Warning(
            f"Style {style} not available. Available styles are: {available_styles}. Using default style 'aps'.",
        )

    base_style = os.path.join(
        os.path.dirname(__file__), "journal_styles", "base.mplstyle"
    )
    style = style.lower()
    style = os.path.join(
        os.path.dirname(__file__), "journal_styles", f"{style}.mplstyle"
    )
    plt.style.use([base_style, style])

    if settings:
        plt.rcParams.update(settings)

    return
