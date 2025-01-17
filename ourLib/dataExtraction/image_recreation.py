# NAME
#        image_recreation
#
# DESCRIPTION
#
#
# AUTHORS
#
#       Raphaël AGATHON - Maxime CLUCHLAGUE - Graziella HUSSON - Valentina ZELAYA
#       Marie ADLER - Aurélien BENOIT - Thomas GRASSELLINI - Lucie MARTIN

from nibabel import save
from os import path
from os import makedirs
from ..filesHandlers import nifimage
from ..filesHandlers import image


def image_recreation(folder_path, image_collection):
    for key in image_collection.nifimage_dict.keys():
        obj = image_collection.nifimage_dict[key]
        if isinstance(obj, nifimage.NifImage):
            name = image_collection.nifimage_dict[key].get_name()
            save(image_collection.nifimage_dict[key].get_image(),
                 path.join(folder_path, path.basename(name).split('.')[0]) + ".nii.gz")
        elif isinstance(obj, image.Image):
            obj.save(path.join(folder_path, path.basename(obj.filename)))


def image_recreation_from_list(folder_path, image_collection_list):
    for ic in image_collection_list:

        folder_path_ic = path.join(folder_path, ic.get_name())

        if not path.exists(folder_path_ic):
            makedirs(folder_path_ic)

        image_recreation(folder_path_ic, ic)
