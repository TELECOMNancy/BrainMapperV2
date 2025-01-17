# NAME
#
#        clustering_plot
#
# DESCRIPTION
#
#       'clustering_plot' contains all the plotting functions
#
# AUTHORS
#
#       Raphaël AGATHON - Maxime CLUCHLAGUE - Graziella HUSSON - Valentina ZELAYA
#       Marie ADLER - Aurélien BENOIT - Thomas GRASSELLINI - Lucie MARTIN

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import BrainMapper
from nilearn import plotting
from .nilearn_plot_upgraded import view_markers
import numpy as np
from scipy.cluster.hierarchy import dendrogram


def plot_silhouette(labels, colors=None):
    """
    Method to make the silhouette plot

    Arguments :
        labels{list} -- list of labels after clustering
        colors -- clustering colors
    """
    sample_silhouettes, labels = BrainMapper.compute_sample_silhouettes(labels)
    average = np.mean(sample_silhouettes)

    # Dict of the form {label:[list of silhouettes]}
    labels_dict = {}

    for sample in zip(sample_silhouettes, labels):
        if sample[1] >= 0:
            labels_dict[sample[1]] = labels_dict[sample[1]] + [sample[0]] if sample[1] in labels_dict.keys() else [
                sample[0]]

    graph_offset = 1  # used to indicate the end of the last graph, so bar graphs don't overlap
    number_of_clusters = len(labels_dict.keys())
    colors = get_color(sorted(labels_dict.keys()))

    plt.figure()
    plt.xlim([np.min(sample_silhouettes), 1])
    plt.ylim([0, len(sample_silhouettes) + 1 + len(
        set(labels))])  # There is len(sample_silhouettes) and 1+len(set(labels)) blanks
    # Add the bars
    for label in sorted(labels_dict.keys()):
        color = colors[label]
        y = sorted(labels_dict[label] + [np.min(labels_dict[
                                                    label])])  # [np.min(labels_dict[label])] is here beacuse of step='pre' (we need 2 y to create a bar)
        plt.fill_betweenx(np.arange(graph_offset, graph_offset + len(y)),
                          0, y,
                          facecolor=color, edgecolor=color, alpha=0.7, step="pre")
        # plt.scatter(np.arange(graph_offset, graph_offset + len(y)),y, facecolor=color)
        plt.text(0.95, graph_offset + int(0.5 * len(y)), str(label), color=color)
        graph_offset += len(y)
    # Add the average silhouette
    plt.axvline(x=average, ymin=0, ymax=graph_offset, color='red', linestyle='--',
                label='average = {:.2f}'.format(average))

    plt.title("The silhouette plot for the various clusters.")
    plt.xlabel("The silhouette coefficient values")
    plt.legend()
    # plt.ylabel("Cluster label",labelpad=0.10)
    plt.yticks([])
    plt.show()


def plot_3d_fuzzy(labels: list, belong, centroids: list):
    """
    Method to make the 3d plot used for FuzzyCMeans clustering

    Arguments :
        labels{list} -- list of labels after clustering
        belong{list} -- list of affiliations of each point to a cluster
    """

    color_dict = get_color(sorted(set(labels)))
    points_list, _ = get_points_list_colors_list(labels)

    colors_bis = []

    for i in range(len(points_list)):
        color = [0, 0, 0, 1]
        for label in set(labels):
            color[0] = color[0] + color_dict[label][0] * belong[i][label]
            color[1] = color[1] + color_dict[label][1] * belong[i][label]
            color[2] = color[2] + color_dict[label][2] * belong[i][label]
        colors_bis.append(tuple(color))
        # #print("plot_3d_fuzzy -> colors[i] APRES", colors_bis[i])

    if len(centroids[0]) == 3:
        centroids_colors = [color_dict[i] for i in sorted(set(labels))]
        view = view_markers(points_list,
                            labels=labels,
                            colors=colors_bis,
                            marker_size=5,
                            centers=centroids,
                            centers_colors=centroids_colors
                            )
    else:
        view = view_markers(points_list,
                            labels=labels,
                            colors=colors_bis,
                            marker_size=5,
                            )

    view.open_in_browser()


def plot_3d_clusters(labels: list, centroids: list = None, marker_size=5.):
    """
    Method to make the 3d plot used for FuzzyCMeans clustering

    Arguments :
        labels{list} -- list of labels after clustering
        colors -- clustering colors
    """

    points_list, colors_list = get_points_list_colors_list(labels)

    unique_labels, counts = np.unique(labels, return_counts=True)
    # label_counts = dict(zip(unique_labels, counts))

    centroids_colors = None
    if centroids is not None:
        # To #print the centers we need the list of centers and the color of each cluster
        color_dict = get_color(sorted(unique_labels))
        centroids_colors = [color_dict[i] for i in sorted(unique_labels)]

    view = view_markers(points_list, labels=labels, colors=colors_list, marker_size=marker_size, centers=centroids,
                        centers_colors=centroids_colors)
    # view.save_as_html("Affichage.html")
    view.open_in_browser()


def plot_3d(points, marker_size=5.):
    """plot a 3d view of the points
    
    Arguments:
        points {list} -- [(X,Y,Z)]
    
    Keyword Arguments:
        marker_size {[type]} -- size of a marker (default: {5.})
    """
    labels = [0] * len(points)
    view = view_markers(points, labels=labels, colors=None, marker_size=marker_size, centers=None, centers_colors=None)
    view.open_in_browser()


def plot_cross_section(labels: list, coordinates):
    """
    Method to make three cross-section of the brain

    Arguments :
        labels{list} -- list of labels after clustering
    """
    points_list, colors_list = get_points_list_colors_list(labels)
    display = plotting.plot_anat(cut_coords=coordinates)
    for point, color in zip(points_list, colors_list):
        display.add_markers([point], marker_color=[color])
    plotting.show()


def plot_glass_brain(labels: list):
    points_list, colors_list = get_points_list_colors_list(labels)
    plotting.plot_connectome(np.zeros((len(colors_list), len(colors_list))), np.array(points_list),
                             node_color=colors_list)
    plotting.show()


def plot_dendrogram(model):
    """
    Method to make a dendogram of a hierarchical agglomerative clustering

    Arguments:
        model -- result of an agglomerative clustering
    """

    # Children of hierarchical clustering
    children = model.children_
    labels = list(model.labels_)

    # Distances between each pair of children
    # Since we don't have this information, we can use a uniform one for plotting
    distance = np.arange(children.shape[0])

    # The number of observations contained in each cluster level
    no_of_observations = np.arange(2, children.shape[0] + 2)

    # Create linkage matrix and then plot the dendrogram
    linkage_matrix = np.column_stack([children, distance, no_of_observations]).astype(float)

    # Plot the corresponding dendrogram
    colors = get_color(set(labels), in_int=True)
    colors[-1] = (83, 135, 2)
    number_of_clusters = len(set(labels))

    for i in range(0, linkage_matrix.shape[0] - number_of_clusters + 1):
        labels.append(labels[int(linkage_matrix[i][0])])
    for i in range(0, number_of_clusters - 1):
        labels.append(-1)

    lis = []

    def link_color_func(k):
        color = colors[labels[k]]
        string = '#'
        lis.append(k)
        for c in color:
            cl = format(c, 'x')
            if len(cl) == 1:
                cl = "0" + cl
            string = string + cl
        return string

    plt.figure()
    dendrogram(linkage_matrix, link_color_func=link_color_func)
    plt.title('Dendrogram')
    plt.ylabel('Distance')
    plt.show()


def get_points_list_colors_list(labels: list, in_int: bool = False) -> (list, list):
    """
    Obtains the points list and colors list from labels.
    It is used in the function that are based on nilearn plotting.

    Arguments:
        labels {list} -- labels resulting of a clustering

    Returns:
        points list, colors list
    """
    points = BrainMapper.current_extracted_clusterizable_data

    color_dict = get_color(sorted(set(labels)), in_int=in_int)
    colors_list = []
    points_list = []
    for i in range(len(labels)):
        points_list.append([points[i, 0], points[i, 1], points[i, 2]])
        colors_list.append(color_dict[labels[i]])
    return points_list, colors_list


def get_color(distinct_labels: list, in_int: bool = False) -> dict:
    """
    Get a dict to homogeinize the color

    Arguments:
        distinct_labels {list} -- [**sorted** list of the **distinct** labels]
        in_int {bool} -- set to True if you want rgba in int [0,255] else default to False and rgba in float [0,1]
    Returns:
        dict -- [key = label: value = color in rgba]
    """

    number_of_clusters = len(distinct_labels)
    color_dict = {}
    if -1 in distinct_labels:
        number_of_clusters = number_of_clusters - 1
        if not in_int:
            color_dict[-1] = (1, 0, 0, 1)
        else:
            color_dict[-1] = (255, 0, 0, 1)
        distinct_labels.remove(-1)
    for label in distinct_labels:
        color_dict[label] = cm.inferno(float(label) / float(number_of_clusters), bytes=in_int)
    return color_dict
