import numpy as np
import plotting_lib as pl
from plotting_lib.plotting import plot_marker_style
import matplotlib.pyplot as plt
import pandas as pd
import typer
from enum import Enum
import textwrap

marker_cycle = [
    "o",
    "s",
    "^",
    "v",
    "D",
    "x"
]

class Style(str, Enum):
    base = "base",
    aps = "APS",
    nature = "Nature",
    quantum = "Quantum"
    

app = typer.Typer()


@app.command()
def generate_threshold_plot(csv_file_path: str,
                            title: str,
                            style: Style = Style.base,
                            output_path: str = typer.Option("", help="If no output path is provided, the plot will be saved in the current directory with the same name as the title"),
                            threshold_value: float = typer.Option(None, help="Theshold value for the plot"),
                            threshold_error: float = typer.Option(None, help="Symmetric error for the threshold"),
                            threshold_error_below: float = typer.Option(None, help="Asymmetric error for the threshold"),
                            threshold_error_above: float = typer.Option(None, help="Asymmetric error for the threshold"),
                            trim_x_above: float = typer.Option(np.inf, help="Data points with an physical error above this value, exclusive, will not be plotted"),
                            trim_y_above: float = typer.Option(np.inf, help="Data points with an logical error above this value, exclusive, will not be plotted"),
                            trim_x_below: float = typer.Option(-np.inf, help="Data points with an physical error below this value, exclusive, will not be plotted"),
                            trim_y_below: float = typer.Option(-np.inf, help="Data points with an logical error below this value, exclusive, will not be plotted"),
):
    """
    Generate threshold plots
    """
    pl.update_settings(usetex=True, style=style, colors=pl.colors_rsb)
    fig, ax = pl.create_fig()

    pd_df = pd.read_csv(csv_file_path)
    labels = pd_df["label"].unique().tolist()
    trim_mask = (pd_df["physical error"] <= trim_x_above) & (pd_df["physical error"] >= trim_x_below) & (pd_df["logical error"] <= trim_y_above) & (pd_df["logical error"] >= trim_y_below)
    if len(pd_df[trim_mask]) == 0:
        raise typer.BadParameter(f"""
        The trim values you have provided remove all data points
        trim_x_below: {trim_x_below}
        trim_y_below: {trim_y_below}
        trim_x_above: {trim_x_above}
        trim_y_above: {trim_y_above}
        """)
    for label_num, label in enumerate(labels):
        color = f"C{label_num}"
        df_mask = (pd_df["label"] == label) & trim_mask
        x = pd_df[df_mask]["physical error"].to_numpy()
        y = pd_df[df_mask]["logical error"].to_numpy()
        y_error_above = pd_df[df_mask]["logical error interval above"].to_numpy()
        y_error_below = pd_df[df_mask]["logical error interval below"].to_numpy()
        ax.plot(x, y,
                **plot_marker_style(color=color, ls="solid", marker=marker_cycle[label_num % len(marker_cycle)]), markevery=1,
                label=label)
        ax.fill_between(x, y - y_error_below, y + y_error_above, color=color, alpha=0.2)

    # Add threshold value
    if threshold_value != None:
        ax.axvline(threshold_value, color="black", linestyle="--")
        if threshold_error != None:
            ax.axvspan(threshold_value - threshold_error, threshold_value + threshold_error, color="black", alpha=0.2)
        elif threshold_error_below != None and threshold_error_above != None:
            ax.axvspan(threshold_value - threshold_error_below, threshold_value + threshold_error_above, color="black", alpha=0.2)

    # Set axis labels
    ax.set_xlabel(r"Physical Error Rate")
    ax.set_ylabel(r"\(p_{L}\)")
    ax.set_yscale("log")
    ax.margins(x=0.05)
    #ax.grid(True)
    ax.legend(framealpha=1, facecolor="white") # add legend
    wrap_title = "\n".join(textwrap.wrap(title, width=40))
    ax.set_title(wrap_title)
    pl.add_label(ax, text="")
    pl.tight_layout()

    if output_path == "":
        pl.save_fig(fig, f"{title}.pdf")
    else:
        pl.save_fig(fig, output_path)

def main():
    app()

if __name__ == "__main__":
    main()
