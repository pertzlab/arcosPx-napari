import numpy as np
import pytest
from qtpy import QtCore
from arcospx import make_sample_data, remove_background, track_events
import napari
from skimage.io import imread
from numpy.testing import assert_array_equal
from qtpy.QtCore import QTimer
from napari.layers.image import Image
from arcos4py.tools import remove_image_background, track_events_image
from pytestqt import qtbot

def test_remove_background(make_napari_viewer, qtbot):
    """
    Test background removal on a simple image.
    """
    viewer = make_napari_viewer()
    test_img = imread('src/arcospx/_tests/test_data/1_growing.tif')
    viewer.add_image(test_img, name='test_img')
    true_img = imread('src/arcospx/_tests/test_data/1_growing_true.tif')
    _,widget = viewer.window.add_plugin_dock_widget("arcosPx-napari", "Remove Background")
    widget.image.value = viewer.layers['test_img']
    widget.filter_type.value = "gaussian"
    widget.size_0.value = 1
    widget.size_1.value = 1
    widget.size_2.value = 1
    worker = widget()
    with qtbot.waitSignal(worker.finished, timeout=10000):
        pass
    assert_array_equal(viewer.layers[1].data, true_img)


def test_track_events(make_napari_viewer, qtbot):
    """
    Test tracking on a simple image.
    """
    viewer = make_napari_viewer()
    test_img = imread('src/arcospx/_tests/test_data/test_data_track_events.tif')
    viewer.add_image(test_img, name='test_img')
    true_img = imread('src/arcospx/_tests/test_data/test_track_events_true.tif')
    _, widget = viewer.window.add_plugin_dock_widget("arcosPx-napari", "Track Events")
    widget.image_selector.value = viewer.layers['test_img']
    widget.threshold.value = 300
    widget.eps.value = 10
    widget.epsPrev.value = 50
    widget.minClSz.value = 50
    widget.minSamples.value = 2
    widget.nPrev.value = 2
    worker = widget()
    with qtbot.waitSignal(worker.finished, timeout=10000):
        pass
    assert_array_equal(viewer.layers[1].data, true_img)

