import matplotlib.pyplot as plt

def create_pie_chart(matched, missing):

    labels = ["Matched", "Missing"]
    sizes = [len(matched), len(missing)]

    fig, ax = plt.subplots(figsize=(2.2, 2.2))

    ax.pie(
        sizes,
        labels=labels,
        autopct="%1.0f%%",
        startangle=90,
        radius=0.8,
        textprops={"fontsize": 9}
    )

    ax.set_title("Skill Analysis", fontsize=10, pad=5)

    plt.tight_layout(pad=0.3)

    return fig
