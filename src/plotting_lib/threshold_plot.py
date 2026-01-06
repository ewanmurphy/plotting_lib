import numpy as np
from numpy import ndarray
import plotting_lib as pl
from plotting_lib.plotting import plot_marker_style
import matplotlib.pyplot as plt
import pandas as pd
import typer
from enum import Enum
import textwrap
from typing import List, Dict, Tuple, Callable, Any

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
def generate_threshold_plot_cmd(csv_file_path: str,
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

    generate_threshold_plot(csv_file_path, title, style, output_path, threshold_value, threshold_error, threshold_error_below , threshold_error_above , trim_x_above, trim_y_above, trim_x_below, trim_y_below)

def generate_threshold_plot(csv_file_path: str,
                            title: str,
                            style: Style = Style.base,
                            output_path: str = "",
                            threshold_value: float = None,
                            threshold_error: float = None,
                            threshold_error_below: float = None,
                            threshold_error_above: float = None,
                            trim_x_above: float = np.inf,
                            trim_y_above: float = np.inf,
                            trim_x_below: float = -np.inf,
                            trim_y_below: float = -np.inf,
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
    #ax.set_yscale("log")
    ax.loglog()
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


def threshold_plot_from_function(
        logical_error_function: Callable[[int, int], int],
        physical_error_range: ndarray,
        num_shots: int,
        kwargs_with_labels: Tuple[Dict[str, Any], str],
        title : str = None,
        path : str = None,
        include_physical_error : bool = False,
):

    labeled_df_list = []
    for labelled_kwargs in kwargs_with_labels:
        label = labelled_kwargs[1]
        kwargs = labelled_kwargs[0]
        labeled_df = pd.DataFrame(columns=["physical error", "logical error", "logical error interval above", "logical error interval below", "label"])
        labeled_df["physical error"] =  physical_error_range
        labeled_df["label"] = label
        labeled_df["logical error interval above"] = 0
        labeled_df["logical error interval below"] = 0
        print(label)
        logical_errors = []
        for physical_error in physical_error_range:
            logical_flips = logical_error_function(physical_error, num_shots, **kwargs)
            print(logical_flips)
            logical_errors.append(logical_flips / num_shots)
        labeled_df["logical error"] = logical_errors
        labeled_df_list.append(labeled_df)

    if include_physical_error:
        labeled_df = pd.DataFrame(columns=["physical error", "logical error", "logical error interval above", "logical error interval below", "label"])
        labeled_df["physical error"] =  physical_error_range
        labeled_df["logical error"] =  physical_error_range
        labeled_df["label"] = "Physical Error"
        labeled_df["logical error interval above"] = 0
        labeled_df["logical error interval below"] = 0
        labeled_df_list.append(labeled_df)

    plot_df = pd.concat(labeled_df_list, ignore_index=True)

    if title == None:
        title = "Temp Plot"
    plot_df.to_csv(f"{title}.csv", index=False)
    if path == None:
        generate_threshold_plot(
            f"{title}.csv",
            title,
            output_path=f"{title}.pdf"
        )
    else:
        generate_threshold_plot(
            f"{title}.csv",
            title,
            output_path=path
        )

def main():
    app()

if __name__ == "__main__":
    main()
