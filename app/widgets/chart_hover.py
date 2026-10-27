"""Mouse-hover tooltips and highlight animation for matplotlib charts."""

from __future__ import annotations


def _fmt(value: float) -> str:
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


def _bar_containers(bars):
    """Normalize ax.bar / ax.barh return value into a list of containers.

    Matplotlib's BarContainer subclasses tuple, so treating it like a plain
    list/tuple wrongly walks each Rectangle as its own series — every hover
    then picks labels[0].
    """
    try:
        from matplotlib.container import BarContainer
    except Exception:  # pragma: no cover
        BarContainer = tuple  # type: ignore[misc, assignment]

    if isinstance(bars, BarContainer):
        return [bars]
    if isinstance(bars, (list, tuple)):
        return list(bars)
    return [bars]


def _container_patches(container):
    try:
        from matplotlib.container import BarContainer
        from matplotlib.patches import Rectangle
    except Exception:  # pragma: no cover
        return list(container) if hasattr(container, "__iter__") else [container]

    if isinstance(container, BarContainer):
        return list(container)
    if isinstance(container, Rectangle):
        return [container]
    if hasattr(container, "__iter__"):
        return list(container)
    return [container]


def enable_bar_hover(
    canvas, ax, bars, labels=None, series_names=None, *, horizontal: bool = False
):
    """Highlight a bar and show its value while the cursor is over it."""
    if not bars:
        return

    flat = []
    meta = []
    containers = _bar_containers(bars)
    for c_idx, container in enumerate(containers):
        patches = _container_patches(container)
        name = None
        if series_names and c_idx < len(series_names):
            name = series_names[c_idx]
        for p_idx, patch in enumerate(patches):
            flat.append(patch)
            label = ""
            if labels and p_idx < len(labels):
                label = labels[p_idx]
            value = patch.get_width() if horizontal else patch.get_height()
            meta.append((label, name, value))

    annot = ax.annotate(
        "",
        xy=(0, 0),
        xytext=(12, 12),
        textcoords="offset points",
        bbox=dict(
            boxstyle="round,pad=0.35",
            fc="#12233A",
            ec="none",
            alpha=0.92,
        ),
        color="#FFFFFF",
        fontsize=8,
        fontweight="600",
        visible=False,
        zorder=20,
    )
    base_alphas = [float(p.get_alpha() if p.get_alpha() is not None else 1.0) for p in flat]
    base_lws = [float(p.get_linewidth()) for p in flat]
    active = {"idx": None}

    def _reset():
        for i, patch in enumerate(flat):
            patch.set_alpha(base_alphas[i])
            patch.set_linewidth(base_lws[i])
            patch.set_edgecolor("none")
        annot.set_visible(False)
        active["idx"] = None

    def on_move(event):
        if event.inaxes != ax:
            if active["idx"] is not None:
                _reset()
                canvas.draw_idle()
            return

        found = None
        for i, patch in enumerate(flat):
            contains, _ = patch.contains(event)
            if contains:
                found = i
                break

        if found is None:
            if active["idx"] is not None:
                _reset()
                canvas.draw_idle()
            return

        if active["idx"] == found:
            return

        _reset()
        active["idx"] = found
        patch = flat[found]
        label, series, value = meta[found]
        patch.set_alpha(min(1.0, base_alphas[found] + 0.15))
        patch.set_linewidth(2.0)
        patch.set_edgecolor("#12233A")

        bits = []
        if label:
            bits.append(str(label))
        if series:
            bits.append(str(series))
        bits.append(_fmt(value))
        if horizontal:
            annot.xy = (value, patch.get_y() + patch.get_height() / 2)
        else:
            annot.xy = (patch.get_x() + patch.get_width() / 2, value)
        annot.set_text("\n".join(bits))
        annot.set_visible(True)
        canvas.draw_idle()

    def on_leave(_event):
        if active["idx"] is not None:
            _reset()
            canvas.draw_idle()

    canvas.mpl_connect("motion_notify_event", on_move)
    canvas.mpl_connect("axes_leave_event", on_leave)


def enable_line_hover(canvas, ax, lines, x_labels=None):
    """Grow the nearest marker and show series/value on hover."""
    if not lines:
        return

    annot = ax.annotate(
        "",
        xy=(0, 0),
        xytext=(12, 12),
        textcoords="offset points",
        bbox=dict(
            boxstyle="round,pad=0.35",
            fc="#12233A",
            ec="none",
            alpha=0.92,
        ),
        color="#FFFFFF",
        fontsize=8,
        fontweight="600",
        visible=False,
        zorder=20,
    )
    base_sizes = [float(line.get_markersize()) for line in lines]
    base_widths = [float(line.get_linewidth()) for line in lines]
    active = {"key": None}

    def _reset():
        for i, line in enumerate(lines):
            line.set_markersize(base_sizes[i])
            line.set_linewidth(base_widths[i])
            line.set_alpha(1.0)
        annot.set_visible(False)
        active["key"] = None

    def on_move(event):
        if event.inaxes != ax or event.xdata is None or event.ydata is None:
            if active["key"] is not None:
                _reset()
                canvas.draw_idle()
            return

        best = None
        best_dist = float("inf")
        for li, line in enumerate(lines):
            xd = line.get_xdata()
            yd = line.get_ydata()
            for pi, (x, y) in enumerate(zip(xd, yd)):
                # Display-distance so scale differences don't skew pick.
                try:
                    dx, dy = ax.transData.transform((x, y)) - ax.transData.transform(
                        (event.xdata, event.ydata)
                    )
                    dist = (dx * dx + dy * dy) ** 0.5
                except Exception:
                    continue
                if dist < best_dist:
                    best_dist = dist
                    best = (li, pi, x, y)

        # ~18 px hit radius
        if best is None or best_dist > 18:
            if active["key"] is not None:
                _reset()
                canvas.draw_idle()
            return

        li, pi, x, y = best
        key = (li, pi)
        if active["key"] == key:
            return

        _reset()
        active["key"] = key
        line = lines[li]
        for i, other in enumerate(lines):
            other.set_alpha(1.0 if i == li else 0.35)
        line.set_markersize(base_sizes[li] + 3.5)
        line.set_linewidth(base_widths[li] + 0.8)

        name = line.get_label() or "Series"
        if name.startswith("_"):
            name = "Series"
        x_lab = ""
        if x_labels is not None:
            try:
                idx = int(round(float(x)))
                if 0 <= idx < len(x_labels):
                    x_lab = str(x_labels[idx])
            except Exception:
                pass
        text = f"{name}\n{x_lab}\n{_fmt(y)}" if x_lab else f"{name}\n{_fmt(y)}"
        annot.xy = (x, y)
        annot.set_text(text)
        annot.set_visible(True)
        canvas.draw_idle()

    def on_leave(_event):
        if active["key"] is not None:
            _reset()
            canvas.draw_idle()

    canvas.mpl_connect("motion_notify_event", on_move)
    canvas.mpl_connect("axes_leave_event", on_leave)
