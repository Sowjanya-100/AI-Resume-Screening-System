import matplotlib.pyplot as plt

def create_pie_chart(matched, missing):

    labels = ["Matched", "Missing"]
    sizes = [len(matched), len(missing)]

    if sum(sizes) == 0:
        sizes = [1, 1]

    fig, ax = plt.subplots(figsize=(2, 2))

    ax.pie(
        sizes,
        labels=labels,
        autopct="%1.0f%%",
        startangle=90,
        radius=0.9,
        textprops={"fontsize": 10}
    )

    ax.set_title("Skill Analysis", fontsize=11)
    plt.tight_layout(pad=0.2)

   

    return fig