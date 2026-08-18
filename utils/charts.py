import matplotlib.pyplot as plt

def create_pie_chart(matched, missing):

    labels = ["Matched", "Missing"]
    sizes = [len(matched), len(missing)]

    fig, ax = plt.subplots(figsize=(2.4, 1.9))

    ax.pie(
        sizes,
        labels=labels,
        autopct="%1.0f%%",
        startangle=90,
        radius=0.75,
        textprops={"fontsize": 8}
    )

    ax.set_title(
        "Skill Analysis",
        fontsize=9,
        pad=2
    )

    ax.set_aspect("equal")

    # Remove unnecessary white space
    fig.subplots_adjust(
        left=0.02,
        right=0.98,
        top=0.85,
        bottom=0.02
    )

    return fig
