"""
This module containst the magic factory widgets for arcospx
"""
from time import sleep
from typing import Literal, Union

import numpy as np
from arcos4py.tools import remove_image_background
from arcos4py.tools._detect_events import ImageTracker, Linker
from magicgui import magic_factory
from napari.layers import Image
from napari.qt.threading import FunctionWorker, thread_worker
from napari.types import LayerDataTuple
from napari.utils import progress
from napari.utils.notifications import show_info
from skimage.filters import threshold_otsu


def do_nothing_function():
    pass


@magic_factory()
def remove_background(
    image: Image,
    filter_type: Literal["gaussian", "median"] = "gaussian",
    size_0: int = 20,
    size_1: int = 5,
    size_2: int = 5,
    dims: str = "TXY",
    crop_time_axis: bool = False,
) -> FunctionWorker[LayerDataTuple]:
    size_tuple = (size_0, size_1, size_2)
    pbar = progress(total=0)

    @thread_worker(connect={"returned": pbar.close})
    def remove_image_background_2() -> LayerDataTuple:
        selected_image = image.data
        removed_background = remove_image_background(
            image=selected_image,
            filter_type=filter_type,
            size=size_tuple,
            dims=dims,
            crop_time_axis=crop_time_axis,
        )
        removed_background = np.clip(removed_background, 0, None)

        layer_properties = {"name": f"{image.name} background removed"}
        sleep(0.1)  # need this for the tests to pass ...
        return (removed_background, layer_properties, "image")

    return remove_image_background_2()


def _on_thresholder_init(widget):
    def update_slider(image: Image):
        # probably don't want to read then throw this array away...
        # but just an example
        min_value = np.min(image.data)
        max_value = np.max(image.data)
        widget.threshold.max = max_value
        widget.threshold.min = min_value
        widget.threshold.value = threshold_otsu(image.data)

    widget.image_selector.changed.connect(update_slider)


@magic_factory(
    auto_call=True,
    threshold={"widget_type": "FloatSlider", "max": 1},
    widget_init=_on_thresholder_init,
)
def thresholder(
    image_selector: Image,
    threshold: float = 0.5,
) -> LayerDataTuple:
    binary_image = np.where(image_selector.data > threshold, 1, 0)
    return (binary_image, {"name": f"{image_selector.name} binary"}, "image")


def _on_track_events_init(widget):
    def _reset_callbutton_name():
        widget.call_button.text = "Run"

    def _set_widget_worker(funciton_worker):
        widget.arcos_worker.value = funciton_worker
        widget.call_button.text = "Abort"
        widget.arcos_worker.value.finished.connect(_reset_callbutton_name)

    widget.called.connect(_set_widget_worker)


@magic_factory(
    arcos_worker={"visible": False}, widget_init=_on_track_events_init
)
def track_events(
    image_selector: Image,
    arcos_worker: Union[FunctionWorker, None] = None,
    eps: float = 1.5,
    epsPrev: float = 0,
    minClSz: int = 9,
    nPrev: int = 1,
    dims: str = "TXY",
) -> FunctionWorker[LayerDataTuple]:
    if arcos_worker is not None and arcos_worker.is_running:
        arcos_worker.quit()
        show_info("Operation aborted by user.")
        return FunctionWorker(do_nothing_function)

    pbar = progress(total=image_selector.data.shape[0])

    @thread_worker(connect={"finished": pbar.close, "yielded": pbar.update})
    def track_events_2() -> LayerDataTuple:
        # Reset the abort flag at the start of each executio

        selected_image = image_selector.data
        # Adjust parameters based on dimensionality

        layer_properties = {
            "name": f"{image_selector.name} tracked",
            "metadata": {
                "eps": eps,
                "epsPrev": epsPrev,
                "minClSz": minClSz,
                "nPrev": nPrev,
                "filename": image_selector.name,  ## eg. setting medatada to the name of the image layer
            },
        }

        linker = Linker(
            eps=eps,
            epsPrev=epsPrev if epsPrev else None,
            minClSz=minClSz,
            nPrev=nPrev,
            predictor=False,
        )
        tracker = ImageTracker(linker)
        # find indices of T in dims
        img_tracked = np.zeros_like(selected_image, dtype=np.uint16)
        for idx, timepoint in enumerate(tracker.track(selected_image, dims)):
            img_tracked[idx] = timepoint
            yield 1

        return (img_tracked, layer_properties, "labels")

    # return the layer data tuple
    arcos_worker = track_events_2()
    return arcos_worker
