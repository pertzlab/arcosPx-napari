import numpy as np
from numpy.testing import assert_array_equal
from skimage.io import imread


def test_remove_background(make_napari_viewer, qtbot):
    """
    Test background removal on a simple image.
    """
    viewer = make_napari_viewer()
    test_img = imread("src/arcospx/_tests/test_data/1_growing.tif")
    viewer.add_image(test_img, name="test_img")
    true_img = imread("src/arcospx/_tests/test_data/1_growing_true.tif")
    _, widget = viewer.window.add_plugin_dock_widget(
        "arcosPx-napari", "Remove Background"
    )
    widget.image.value = viewer.layers["test_img"]
    widget.filter_type.value = "gaussian"
    widget.size_0.value = 1
    widget.size_1.value = 1
    widget.size_2.value = 1

    with qtbot.waitSignal(viewer.layers.events.inserted, timeout=10000):
        widget()

    assert_array_equal(viewer.layers[1].data, true_img)


def test_track_events(make_napari_viewer, qtbot):
    """
    Test tracking on a simple image.
    """
    viewer = make_napari_viewer()
    test_img = np.where(
        imread("src/arcospx/_tests/test_data/1_growing.tif") == 0, 2, 0
    )
    viewer.add_image(test_img, name="test_img")
    true_img = imread(
        "src/arcospx/_tests/test_data/1_growing_track_events_true.tif"
    )
    _, widget = viewer.window.add_plugin_dock_widget(
        "arcosPx-napari", "Track Events"
    )
    widget.image_selector.value = viewer.layers["test_img"]
    widget.threshold.value = 1
    widget.eps.value = 1
    widget.epsPrev.value = 1
    widget.minClSz.value = 1
    widget.minSamples.value = 1
    widget.nPrev.value = 1

    with qtbot.waitSignal(viewer.layers.events.inserted, timeout=10000):
        widget()

    assert_array_equal(viewer.layers[1].data, true_img)
