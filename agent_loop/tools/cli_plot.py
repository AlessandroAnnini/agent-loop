import plotext as plt
import time

tool_definition = {
    "name": "cli_plot",
    "description": (
        "This is the default plotting and charting tool."
        "Render advanced terminal charts using plotext. Use this to visualize data in the terminal, for charts, graphs, plots, etc. that have not to be saved to a file."
        "Supports line, scatter, bar, histogram, datetime, log-scales, subplots, styling, and streaming."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "data": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "array", "items": {"type": ["number", "string"]}},
                        "y": {"type": "array", "items": {"type": "number"}},
                        "label": {"type": "string"},
                        "type": {
                            "type": "string",
                            "enum": ["line", "scatter", "bar", "hist"],
                        },
                        "yaxis": {"type": "string", "enum": ["left", "right"]},
                        "color": {"type": "string"},
                        "marker": {"type": "string"},
                        "fill": {"type": "boolean"},
                    },
                    "required": ["y", "type"],
                },
                "description": "List of series to plot.",
            },
            "style": {
                "type": "object",
                "properties": {
                    "width": {"type": "integer"},
                    "height": {"type": "integer"},
                    "title": {"type": "string"},
                    "xlabel": {"type": "string"},
                    "ylabel": {"type": "array", "items": {"type": "string"}},
                    "grid": {"type": "array", "items": {"type": "boolean"}},
                    "xscale": {"type": "string"},
                    "yscale": {"type": "string"},
                },
                "description": "Styling options for the plot.",
            },
            "stream": {
                "type": "object",
                "properties": {
                    "frames": {"type": "integer"},
                    "interval": {"type": "number"},
                    "clear_terminal": {"type": "boolean"},
                },
                "description": "Streaming mode configuration.",
            },
        },
        "required": ["data"],
    },
}


def handle_call(input_data):
    try:
        plt.clear_figure()
        data_series = input_data["data"]
        style = input_data.get("style", {})
        stream_cfg = input_data.get("stream")

        # Styling
        if style.get("width") and style.get("height"):
            plt.plotsize(style["width"], style["height"])
        if style.get("title"):
            plt.title(style["title"])
        if style.get("xlabel"):
            plt.xlabel(style["xlabel"])
        if style.get("ylabel"):
            ylabels = style["ylabel"]
            plt.ylabel(ylabels[0], *(ylabels[1:] if len(ylabels) > 1 else []))
        if style.get("grid"):
            plt.grid(*style["grid"])
        if style.get("xscale"):
            plt.xscale(style["xscale"])
        if style.get("yscale"):
            plt.yscale(style["yscale"])

        # Plot data
        for series in data_series:
            func = {
                "line": plt.plot,
                "scatter": plt.scatter,
                "bar": plt.bar,
                "hist": plt.hist,
            }[series["type"]]

            args = []
            if "x" in series:
                args.append(series["x"])
            args.append(series["y"])

            kwargs = {}
            for opt in ("label", "yaxis", "color", "marker"):
                if series.get(opt):
                    kwargs[opt] = series[opt]
            if series.get("fill"):
                kwargs["fillx" if series["type"] in ("line", "scatter") else "fill"] = (
                    True
                )

            func(*args, **kwargs)

        # Streaming mode
        if stream_cfg:
            frames = stream_cfg.get("frames", 1)
            interval = stream_cfg.get("interval", 0.1)
            clear_term = stream_cfg.get("clear_terminal", True)

            for _ in range(frames):
                if clear_term:
                    plt.clear_terminal()
                plt.show()
                time.sleep(interval)
                plt.clear_data()
        else:
            plt.show()

        return {"status": "Rendered successfully."}

    except Exception as e:
        return {"error": f"Plotting failed: {e}"}
