import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
import os
from nipype.interfaces import fsl
from nipype.interfaces.semtools.registration import brainsresample

# Handle brain imaging data.
# Preporcessng is done by fMRIPrep.

class fMRIimage:
    def __init__(self, img_path):
        self.img = nib.load(img_path)
        self.img_path = img_path
        self.img_data = self.img.get_data()

    def __str__(self):
        return str(self.img.header) + '\npath = ' + self.img_path

    def mask_non_brain_region(self):
        # USE fmriprep!
        filename, file_extension1 = os.path.splitext(self.img_path)
        filename, file_extension2 = os.path.splitext(filename)
        out_path = filename + '_mask_non_brain_region' + file_extension2 + file_extension1
        if not os.path.isfile(out_path):
            btr = fsl.BET()
            btr.inputs.in_file = self.img_path
            btr.inputs.out_file = out_path
            btr.inputs.frac = 0.25
            btr.inputs.functional = True
            btr.inputs.output_type = 'NIFTI_GZ'
            btr.cmdline
            btr.run()
        self.img = nib.load(out_path)
        self.img_path = out_path
        self.img_data = self.img.get_data()

    def get_neighbor_voxels_of_a_point(self, x, y, z, neighbor_size):
        max_x = x + neighbor_size + 1
        max_y = y + neighbor_size + 1
        max_z = z + neighbor_size + 1
        min_x = x - neighbor_size
        min_y = y - neighbor_size
        min_z = z - neighbor_size
        out = self.img_data[min_x:max_x, min_y:max_y, min_z:max_z,:]
        assert out.shape[:3] == (2 * neighbor_size + 1, 2 * neighbor_size + 1, 2 * neighbor_size + 1)
        return out

    def get_all_neigbor_voxels_with_size(self, neighbor_size):
        shape = self.img_data.shape
        out = []
        for x in range(0 + neighbor_size, shape[0] - neighbor_size):
            for y in range(0 + neighbor_size, shape[1] - neighbor_size):
                for z in range(0 + neighbor_size, shape[2] - neighbor_size):
                    out.append = get_neighbor_voxels_of_a_point(self, x, y, z, neighbor_size)
        return np.array(out)

    def show_slices(self, x, y, z, v):
        fig, axes = plt.subplots(1, 3)
        slices = [self.img_data[x, :, :, v], self.img_data[:, y, :, v], self.img_data[:, :, z, v]]
        for i, slice in enumerate(slices):
            axes[i].imshow(slice.T, cmap="gray", origin="lower")
        plt.show()

def concat_sessions(img_list):
    out_list = []
    for img in img_list:
        array = img.img_data
        out_list.append(array[:, :, :, 3:-5]) #Refer to Hanke et al., 2014
    img_data = np.concatenate(out_list, axis=-1)
    return img_data

if __name__ == "__main__":
    data_path = '/Users/YiSangHyun/ds000113-download/sub-03/ses-movie/func'
    img_list = []
    for i in range(1,9):
        img = fMRIimage(os.path.join(data_path, 'sub-03_ses-movie_task-movie_run-{}_bold.nii.gz'.format(i)))
        img_list.append(img)
    #img.show_slices(40,40,20,3)
    #img.mask_non_brain_region()

    #img.show_slices(40,40,20,3)

    #img_data = img.get_data()
    print(concat_sessions(img_list).shape)
