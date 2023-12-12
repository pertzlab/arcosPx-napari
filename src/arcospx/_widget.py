"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
from time import sleep
from typing import Literal

from arcos4py.tools import track_events_image
from magicgui import magic_factory
from napari.layers import Image
from napari.qt.threading import FunctionWorker, thread_worker
from napari.types import LayerDataTuple
from napari.utils import progress


class AbortException(Exception):
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
    pbar = progress(total=0)

    @thread_worker(connect={"returned": pbar.close})
    def remove_image_background_2() -> LayerDataTuple:
        selected_image = image.data
        # removed_background = remove_image_background(
        #     image=selected_image, filter_type=filter_type, size=size, dims=dims, crop_time_axis=crop_time_axis
        # )

        removed_background = selected_image

        layer_properties = {"name": f"{image.name} background removed"}
        sleep(0.5)
        return (removed_background, layer_properties, "image")

    return remove_image_background_2()


@magic_factory()
def track_events(
    image_selector: Image,
    threshold: int = 300,
    eps: int = 10,
    epsPrev: int = 50,
    minClSz: int = 50,
    minSamples: int = 2,
    nPrev: int = 2,
    dims: str = "TXY",
) -> FunctionWorker[LayerDataTuple]:
    pbar = progress(total=0)

    @thread_worker(connect={"returned": pbar.close})
    def track_events_2() -> LayerDataTuple:
        global abort_flag

        # Reset the abort flag at the start of each execution
        abort_flag = False

        if abort_flag:
            # Return an error message
            # return "Interrupt error: Operation aborted by user."
            # Or raise a custom exception
            pbar.close()
            raise AbortException("Operation aborted by user.")

        selected_image = image_selector.data
        img_tracked = track_events_image(
            selected_image >= threshold,
            eps=eps,
            epsPrev=epsPrev,
            minClSz=minClSz,
            minSamples=minSamples,
            nPrev=nPrev,
            dims=dims,
        )

        if abort_flag:
            # Return an error message
            # return "Interrupt error: Operation aborted by user."
            # Or raise a custom exception
            pbar.close()
            raise AbortException("Operation aborted by user.")

        # Like this we create the layer as a layer-data-tuple object which will automatically be parsed by napari and added to the viewer
        # This is more flexible and does not require the function to know about the viewer directly
        # Additionally like this you can now set the metadata of the layer
        layer_properties = {
            "name": f"{image_selector.name} tracked",
            "metadata": {
                "threshold": threshold,
                "eps": eps,
                "epsPrev": epsPrev,
                "minClSz": minClSz,
                "nPrev": nPrev,
                "filename": image_selector.name,  ## eg. setting medatada to the name of the image layer
            },
        }
        return (img_tracked, layer_properties, "labels")

    # return the layer data tuple
    return track_events_2()


@magic_factory()
def abort_process():
    global abort_flag
    abort_flag = True
