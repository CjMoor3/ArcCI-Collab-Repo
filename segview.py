#title: Segmentation Analysis GUI
#author: Xin Miao 
#ver 1.0    8/7/2020
#Inspired by: Nick Wright

#purpose: Creates a GUI for selecting image segmentation parameters. 

# Python 3:
    
        # a=image_data        
        # print(type(a), a.dtype, a.shape)
        # print(a)      # Debug Miao      
    
    
import tkinter as tk
from tkinter import *

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import h5py
import os
import argparse
from ctypes import *
from osgeo import gdal
#from sklearn.ensemble import RandomForestClassifier
from select import select
import sys
import preprocess as pp
from segment2 import segment_image2 as segment_image
from lib import utils
#from lib import attribute_calculations as attr_calc
from skimage.segmentation import mark_boundaries

x0=0 # Global variable of current mouse click position
y0=0
gauss_sigma0=2         #Segmentation parameter
feature_separation0=5


class PrintColor:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class Buttons(tk.Frame):
    # Defines the properties of all the controller buttons to be used by the GUI.
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent         # It works as a bridge to link to other class-functions

        #self.parent.geometry('800x300') #CJ revise to resize GUI

        #tk.Grid.rowconfigure(root, 0, weight=1) #CJ: apply resizing weights to GUI...
        #tk.Grid.columnconfigure(root, 0, weight=1) #... for use with any resolution.
        #frame = tk.Frame(root)
        #frame.grid(row=0, column=0, sticky='nsew')
        
        self.zoom=100
        
        label_Zoom=tk.Label(self, text="Zoom +-")
        label_Zoom.grid(column=0, row=0, pady=(0,2), sticky='nsew')
        
        # Define get_slider_value() function in the same class (Button)
        Zoom_slider = tk.Scale(self, from_=50, to=400, length=160, orient=HORIZONTAL, relief=RAISED, 
                               command=self.get_Zoom_slider_value) # length default=100
        
        Zoom_slider.grid(column=0, row=1, pady=(0,20), sticky='nsew')
        Zoom_slider.set(100)
        # a=Zoom_slider.get()
        
        # print ("Zoom value:", a)
#-----------------------------------------------------------------------------        
        # Create a Tkinter variable       
        label0=tk.Label(self, text="Choose a segmentation method:")
        label0.grid(column=0, row=2, pady=(0,2), sticky='nsew')
        
        tkvar = StringVar(self) # Tkinter variable, 'tracing', to update certain widgets when an associated variable is modified.
        # Dictionary with options
        choices = { 'Default','Method 1','Method 2'}
        tkvar.set('Default') # set the default option
        
        
        methodOptionMenu = tk.OptionMenu(self, tkvar, *choices, command=self.get_method_option_value)  # 
        methodOptionMenu.config(width=18)
        methodOptionMenu.grid(column=0, row=3, pady=(0,80), sticky='nsew')
#-----------------------------------------------------------------------------
        
        label1=tk.Label(self, text="Gauss_sigma:")
        label1.grid(column=0, row=4, pady=(0,2), sticky='nsw')
        
        Seg_para_slider1 = tk.Scale(self, from_=0, to=10, length=160, orient=HORIZONTAL, relief=RAISED,
                                    command=self.get_para_slider1_value) # length default=100      
        Seg_para_slider1.grid(column=0, row=5, pady=(0,20), sticky='nsw')

        Seg_para_slider1.set(gauss_sigma0)
        
        label2=tk.Label(self, text="Feature separation:")
        label2.grid(column=0, row=6, pady=(0,2), sticky='nsw')
        
        Seg_para_slider2 = tk.Scale(self, from_=0, to=12, length=160, orient=HORIZONTAL, relief=RAISED,
                                    command=self.get_para_slider2_value)
        Seg_para_slider2.grid(column=0, row=7, pady=(0,20), sticky='nsw')
        Seg_para_slider2.set(feature_separation0)
        
#----------------------------------------------------------------------------- 
        previous_btn = tk.Button(self, text="Previous Image", width=18, height=2,
                             command=lambda: parent.event_manager.previous_image())
        previous_btn.grid(column=0, row=8, pady=(40,1), sticky='nsw')
       
        next_btn = tk.Button(self, text="Next Image", width=18, height=2,
                             command=lambda: parent.event_manager.next_image())
        next_btn.grid(column=0, row=9, pady=(20,1), sticky='nsw')
        
        quit_btn = tk.Button(self, text="Save and Quit", width=18, height=2,
                             command=lambda: parent.event_manager.quit_event())
        quit_btn.grid(column=0, row=10, padx=15, pady=(20,1), sticky='nsw')

        load_first_btn = tk.Button(self, text="Initialize Image", width=18, height=2,
                                   command=lambda: parent.event_manager.initialize_image())
        load_first_btn.grid(column=0, row=1, padx=15, pady=(20,0), sticky='nsw')

    def get_Zoom_slider_value(self, new_value):
        self.zoom=new_value    
        try:              # Without it, the first time GUI showing up will trigger set() and this func and request to updatae a non-type (blank) image
            self.parent.image_display.update_images(x0,y0)
        except TypeError as error:
            pass
    # def set_para_slider1_value(self):
    #     Seg_para_slider1.set(2)
        
    def get_para_slider1_value(self, new_value):
        global gauss_sigma0   
        gauss_sigma0=int(new_value)  # returned value is 'str'     
        try:              # Without it, the first time GUI showing up will trigger set() and this func and request to updatae a non-type (blank) image
            self.parent.image_display.update_images(x0,y0)
        except TypeError as error:
            pass
 
    def get_para_slider2_value(self, new_value):
        global feature_separation0
        feature_separation0=int(new_value)
        try:
            self.parent.image_display.update_images(x0,y0)
        except TypeError as error:
            pass       
    def get_method_option_value () :
#        print(self.tkvar.get())
        print("Choose 1")
        
class ProgressBar(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.total_counter = tk.StringVar()
        self.total_counter.set("Total Progress: {}".format(0))
        self.image_tracker = tk.StringVar()
        self.image_tracker.set("")

        total_text = tk.Label(self, textvariable=self.total_counter)
        total_text.grid(column=0, row=0)

        image_text = tk.Label(self, textvariable=self.image_tracker)
        image_text.grid(column=0, row=1)

    def update_progress(self):
#        self.total_counter.set("Total Progress: {}".format(self.parent.data.get_num_labels()))
        self.image_tracker.set("Image {} of {}".format(self.parent.data.im_index + 1,
                                                       len(self.parent.data.available_images)))


class ImageDisplay(tk.Frame):  # Main script to display images

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.parent = parent
        # Initialize class variables
        # Populated in initialize_image method:
        self.display_image = None
        self.disp_xdim, self.disp_ydim, = 0, 0
        # Populated in update_images:
        self.zoom_win_x, self.zoom_win_y = 0, 0
              
        # Creating the canvas where the images will be
        self.fig = plt.figure(figsize=[12, 10])  # width, height 12', 10'
        self.fig.subplots_adjust(left=0.01, right=0.99, bottom=0.05, top=0.99, wspace=0.01, hspace=0.01)

        canvas = FigureCanvasTkAgg(self.fig, self) # Bring 'plt.figure' into TK frame 'self'； add the canvas, which is what we intend to render the graph to.
        canvas.draw()
      
#        toolbar = NavigationToolbar2TkAgg(canvas, frame)
        
        canvas.get_tk_widget().grid(column=0, row=0)

        self.cid = self.fig.canvas.mpl_connect('button_press_event', parent.event_manager.onclick)

        # Create a placeholder while image data is loading
        self.initial_display()


    def initialize_image(self):
        # Creates a local composite of the original image data for display
        if self.parent.data.im_type == 'wv02_ms':
            self.display_image = utils.create_composite([self.parent.data.original_image[4, :, :],
                                                         self.parent.data.original_image[2, :, :],
                                                         self.parent.data.original_image[1, :, :]],
                                                         dtype=np.uint8)
# Miao: modified 6/9/2020
        elif self.parent.data.im_type == 'pan':
            self.display_image = utils.create_composite([self.parent.data.original_image[0, :, :],
                                                         self.parent.data.original_image[0, :, :],
                                                         self.parent.data.original_image[0, :, :]],
                                                         dtype=np.uint8)

        elif self.parent.data.im_type == 'srgb':
            self.display_image = utils.create_composite([self.parent.data.original_image[0, :, :],
                                                         self.parent.data.original_image[1, :, :],
                                                         self.parent.data.original_image[2, :, :]],
                                                         dtype=np.uint8)
        self.disp_xdim, self.disp_ydim = np.shape(self.display_image)[0:2]

        # a=self.display_image        
        # print(type(a), a.dtype, a.shape)
        # print(a)      # Debug Miao  

    def loading_display(self):

        plt.clf()

        loading_text = "Images are loading, please wait... "
        # Creates a image placeholder while the data is being loaded.
        ax = self.fig.add_subplot(1, 1, 1, adjustable='datalim', frame_on=False)
        ax.text(0.5, 0.5, loading_text, horizontalalignment='center', verticalalignment='center')
        ax.axis('off')

        # Updating the plots
        self.fig.canvas.draw()

    def initial_display(self):

        plt.clf()

        welcome_text = "No images have been loaded. Press <Initialize Image> to begin."
#        tds_text = "Training data file: \n {}".format(self.parent.data.tds_filename)
        image_text = "Images found: \n"
        if len(self.parent.data.available_images) == 0:
            image_text += 'None'
        else:
            for im in self.parent.data.available_images:
                image_text += im + '\n'

        # Creates a image placeholder while the data is being loaded.
        ax = self.fig.add_subplot(2, 1, 1)
 #       ax = self.fig.add_subplot(2, 1, 1, adjustable='datalim', frame_on=False)
        ax.text(0.5, 0.3, welcome_text, horizontalalignment='center', verticalalignment='bottom', weight='bold')
        ax.axis('off') # Remove x-, y-axis

        ax2 = self.fig.add_subplot(2, 1, 2, adjustable='datalim', frame_on=False)
#        ax2.text(0.5, 1, tds_text, horizontalalignment='center', verticalalignment='center')
        ax2.text(0.5, .9, image_text, horizontalalignment='center', verticalalignment='top')
        ax2.axis('off')

        # Updating the plots
        self.fig.canvas.draw()

    def update_images(self, x, y):
        
        global gauss_sigma0, feature_separation0
        
        # Clear the existing display
        plt.clf()


        zoom_size = self.parent.buttons.zoom
        zoom_size=int(zoom_size)

        
        x_min = y - zoom_size   # x_min: row, is onclick ydata 
        x_max = y + zoom_size   # x_max: row, is onclick ydata
        y_min = x - zoom_size   # y_min: col, is onclick xdata 
        y_max = x + zoom_size   # y_max: col, is onclick xdata 

        # Store the zoom window corner coordinates for reference in onclick()
        # xMin and yMin are defined backwards
        self.zoom_win_x = y_min
        self.zoom_win_y = x_min

        if x_min < 0:
            x_min = 0
            x_max = zoom_size*2-1
        if x_max >= self.disp_xdim:
            x_max = self.disp_xdim - 1
            x_min = x_max- zoom_size*2    # Need adjustment later Miao
        if y_min < 0:
            y_min = 0
            y_max = zoom_size*2-1
        if y_max >= self.disp_ydim:
            y_max = self.disp_ydim - 1
            y_min = y_max- zoom_size*2 

        # Image 2 (Zoomed in image, no highlighted segment)

        cropped_image = self.display_image[x_min:x_max, y_min:y_max]   #line 203

        image_data=cropped_image
#        print(image_data.shape)
        
        if self.parent.data.im_type == 'pan':
            image_data=cropped_image[:,:,0]
            image_data=np.reshape(image_data, (1, image_data.shape[0], image_data.shape[1]))
        
        if self.parent.data.im_type == 'srgb':
            image_data=np.stack( (image_data[:,:,0], image_data[:,:,1], image_data[:,:,2]), axis=0)  #(row, col, 3)-> (3, row, col)
        
     
        seg_image = segment_image(image_data, gauss_sigma0, feature_separation0, image_type=self.parent.data.im_type, merging_cut=30)
        
        
        if np.max(seg_image) > 0:
#        print(np.max(image_data))  # Donn't know why srgb has all zero value if with black background? 8/8/2020
        
#        watershed_result = mark_boundaries(image_data[0], seg_image)
            watershed_result = mark_boundaries(cropped_image, seg_image)  
            watershed_result = 255 * watershed_result
            watershed_result = watershed_result.astype(np.uint8) 
        
        else:
            watershed_result = np.zeros(np.shape(seg_image)).astype(np.uint8)
        
        color_image = watershed_result #(row, col, 3)
        
#        seg_result = None  # Is this necessary? Miao

        # Text instructions
        instructions = '''
        Segmentation methods description: \n
        Parameters:
         
         \n
        '''

        # Plotting onto the GUI
        ax = self.fig.add_subplot(2, 2, 1)
        ax.imshow(color_image, interpolation='None', vmin=0, vmax=255)
        ax.tick_params(axis='both',  # changes apply to the x-axis
                       which='both',  # both major and minor ticks are affected
                       bottom=False,  # ticks along the bottom edge are off
                       top=False,  # ticks along the top edge are off
                       left=False,
                       right=False,
                       labelleft=False,
                       labelbottom=False)
        ax.set_label('ax1')

        ax = self.fig.add_subplot(2, 2, 2)
        ax.imshow(cropped_image, interpolation='None', vmin=0, vmax=255)
        ax.tick_params(axis='both',  # changes apply to the x-axis
                       which='both',  # both major and minor ticks are affected
                       bottom=False,  # ticks along the bottom edge are off
                       top=False,  # ticks along the top edge are off
                       left=False,
                       right=False,
                       labelleft=False,
                       labelbottom=False)
        ax.set_label('ax2')

        ax = self.fig.add_subplot(2, 2, 3)
        ax.imshow(self.display_image, interpolation='None', vmin=0, vmax=255)
        ax.axvspan(y_min,
                   y_max,
                   1. - float(x_max) / self.disp_xdim,
                   1. - float(x_min) / self.disp_xdim,
                   color='red',
                   alpha=0.3)
        ax.set_xlim([0, np.shape(self.display_image)[1]])
        ax.tick_params(axis='both',  # changes apply to the x-axis
                       which='both',  # both major and minor ticks are affected
                       bottom=False,  # ticks along the bottom edge are off
                       top=False,  # ticks along the top edge are off
                       left=False,
                       right=False,
                       labelleft=False,
                       labelbottom=False)
        ax.set_label('ax3')

        ax = self.fig.add_subplot(2, 2, 4, adjustable='datalim', frame_on=False)
        ax.text(0.5, 0.5, instructions, horizontalalignment='center', verticalalignment='center')
        ax.axis('off')

        # Updating the plots
        self.fig.canvas.draw()


class DataManager:

    def __init__(self, available_images, username, im_type):
#    def __init__(self, available_images, tds_filename, username, im_type):
        # Image and segment data (populated in load_image())
        self.original_image = None
        self.segmented_image = None

        # Variable Values   (populated in load_training_data())
        self.label_vector = []
        self.segment_list = []
        self.feature_matrix = []
        self.tracker = 0                                    # Number of segment sets added from the current image
        self.im_index = 0                                   # Index for progressing through available images

        # Global Static Values
#        self.tds_filename = tds_filename
        self.username = username
        self.im_type = im_type
        self.available_images = available_images

        # Image Static Value (populated in load_image())
        self.wb_ref = None
        self.br_ref = None
        self.im_date = None
        self.im_name = None
        self.watershed_result = None
        
    def load_next_image(self):
        # Increment the image index
        self.im_index += 1
        # Loop im_index based on the available number of images
        self.im_index = self.im_index % len(self.available_images)
        # Load the new data
        self._load_image()


    def load_previous_image(self):
        # Increment the image index
        self.im_index -= 1
        # Loop im_index based on the available number of images
        self.im_index = self.im_index % len(self.available_images)
        # Load the new data
        self._load_image()
    def _load_image(self):
        # Loads the optical and segmented image data from disk. Should only be called from
        #   load_next_image method.
        full_image_name = self.available_images[self.im_index]

        self.im_name = os.path.splitext(os.path.split(full_image_name)[1])[0]

        src_ds = gdal.Open(full_image_name, gdal.GA_ReadOnly)

        # Read the image date from the metadata
        metadata = src_ds.GetMetadata()
        self.im_date = pp.parse_metadata(metadata, self.im_type)

        # Determine the datatype
        src_dtype = gdal.GetDataTypeSize(src_ds.GetRasterBand(1).DataType)

        # Calculate the reference points from the image histogram
        lower, upper, wb_ref, br_ref = pp.histogram_threshold(src_ds, src_dtype)
        self.wb_ref = np.array(wb_ref, dtype=c_uint8)
        self.br_ref = np.array(br_ref, dtype=c_uint8)

        # Load the image data
        image_data = src_ds.ReadAsArray()     # <class 'numpy.ndarray'> uint8 (3, 7471, 8242)
        
        # a=image_data        
        # print(type(a), a.dtype, a.shape)
        # print(a)      # Debug Miao  
        
#Miao        
        if image_data.ndim ==2:
            image_data=image_data.reshape((1,image_data.shape[0],image_data.shape[1]))

            

        # Close the GDAL dataset
        src_ds = None

        # Rescale the input dataset using a histogram stretch
        image_data = pp.rescale_band(image_data, lower, upper)
              
        # Apply a white balance to the image
        image_data = pp.white_balance(image_data, self.wb_ref.astype(np.float), float(np.amax(self.wb_ref)))

        # Convert the input data to c_uint8
        self.original_image = np.ndarray.astype(image_data, c_uint8) # Necessary



#     def get_num_labels(self):          #label_vector: Number of segment sets added from the current image
# #        print (self.label_vector)
#         return len(self.label_vector)


    # def trim_segment_list(self):
    #     self.segment_list = self.segment_list[:len(self.label_vector)]



class EventManager:

    def __init__(self, parent):
        self.parent = parent
        self.is_active = False                  # Prevents events from happening while images are loading

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def onclick(self, event):
        global x0, y0   # global variable of current mouth position
        if not self.is_active:
            return

        if event.inaxes is not None:
            axes_properties = event.inaxes.properties()
#            segment_id = -1
            x, y = 0, 0

            # If the mouse click was in the overview image
            if axes_properties['label'] == 'ax3':
                x = int(event.xdata)  # image pixel-- x coord of mouse in data coords
                y = int(event.ydata)  # y coord of mouse in data coords
#                segment_id = self.parent.data.segmented_image[y, x]

            # Either of the top zoomed windows
            if axes_properties['label'] == 'ax1' or axes_properties['label'] == 'ax2':
                win_x = int(event.xdata)
                win_y = int(event.ydata)
                x = self.parent.image_display.zoom_win_x + win_x
                y = self.parent.image_display.zoom_win_y + win_y
#                segment_id = self.parent.data.segmented_image[y, x]
            
            x0=x
            y0=y
            
            self.parent.image_display.update_images(x0,y0)


    def save(self):

        if self.parent.data.label_vector == []:
            return

        print("Saving...")

        username = self.parent.data.username

        prev_names = []
        prev_data = []
        try:
            with h5py.File(self.parent.data.tds_filename, 'r') as infile:
                # Compiles all of the user data that was in the previous training validation file so that
                # it can be added to the new file as well. (Because erasing and recreating a .h5 is easier
                # than altering an existing one)
                for prev_user in list(infile.keys()):
                    if prev_user != 'feature_matrix' and prev_user != 'segment_list' and prev_user != username:
                        prev_names.append(prev_user)
                        prev_data.append(infile[prev_user][:])
                infile.close()
        except OSError:
            pass

        # overwrite the h5 dataset with the updated information
        with h5py.File(self.parent.data.tds_filename, 'w') as outfile:
            outfile.create_dataset('feature_matrix', data=self.parent.data.feature_matrix)
            outfile.create_dataset(username, data=self.parent.data.label_vector)
            segment_list = np.array(self.parent.data.segment_list, dtype=np.string_)
            outfile.create_dataset('segment_list', data=segment_list)

            for i in range(len(prev_names)):
                outfile.create_dataset(prev_names[i], data=prev_data[i])

        print("Done.")

    def next_image(self):
        if not self.is_active:
            return

        self.deactivate()
        # Trim the unlabeled segments from segment list
#        self.parent.data.trim_segment_list()
        # Save the existing data
#        self.save()
        # Set the display to the loading screen
        self.parent.after(10, self.parent.image_display.loading_display())
        # Load the next image data
        self.parent.data.load_next_image()
        # Add the new data to the display class
        self.parent.image_display.initialize_image()
        # Update the display screen
        # Go to the next segment (which will add additional segments to the queue and update the display)
        self.parent.progress_bar.update_progress()
        self.activate()
        
        self.parent.image_display.update_images(100,100)
        
    def previous_image(self):

        self.deactivate()
        # Set the display to the loading screen
        self.parent.after(10, self.parent.image_display.loading_display())
        # Load the previous image data
        self.parent.data.load_previous_image()
        # Add the new data to the display class
        self.parent.image_display.initialize_image()
        # Update the display screen
        # Go to the next segment (which will add additional segments to the queue and update the display)
        self.parent.progress_bar.update_progress()
        self.activate()
#        self.next_segment()
        self.parent.image_display.update_images(100,100)
        
    def initialize_image(self):
        if len(self.parent.data.available_images) == 0:
            print("No images to load!")
            return
        # Check to make sure no data has been loaded
        if self.parent.data.im_name is not None:
            return
        # Previous image does all the loading work we need for the first image
        self.previous_image()


    def quit_event(self):
        # Exits the GUI, automatically saves progress
        self.save()
        self.parent.exit_gui()





class TrainingWindow(tk.Frame):

#    def __init__(self, parent, img_list, tds_filename, username, im_type, activate_autorun=False):
    def __init__(self, parent, img_list, username, im_type, activate_autorun=False):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title("Segmentaion Preview GUI")

        # self.parent.iconbitmap('vectorstock_7199163_icon.ico') # Designed by freepik (Image #7199163 at VectorStock.com)

        # Create the controlling buttons and place them on the right side.
        self.buttons = Buttons(self)
        self.buttons.grid(column=1, row=1, sticky="N") #Put buttons as an instance of object (class) Buttons, column=1, row=1, on Top

        # Manager for all the GUI events (e.g. button presses)
        self.event_manager = EventManager(self)    # Define event_manager functions, should be found in EventManager()

        # Data manager object
#        self.data = DataManager(img_list, tds_filename, username, im_type)
        self.data = DataManager(img_list, username, im_type)
#        self.data.load_training_data()

        # Create the image display window
        self.image_display = ImageDisplay(self)
        self.image_display.grid(column=0, row=0, rowspan=2) #Main (big) image view in column=0, row=0

        self.progress_bar = ProgressBar(self)
        self.progress_bar.grid(column=1, row=0)   # Progress info shown in col=1, row=0 (top right corner)

        self.progress_bar.update_progress()

    def exit_gui(self):
        self.parent.quit()
        self.parent.destroy()


# Returns all of the unique images in segment_list
def get_required_images(segment_list):
    image_list = []
    for seg_id in segment_list:
        if not seg_id[0] in image_list:
            image_list.append(seg_id[0])
    return image_list


# Finds all the unique images from the given directory
def scrape_dir(src_dir):
    image_list = []

    for ext in utils.valid_extensions:   # valid_extensions is a list ['.tif','.tiff','.jpg']
        raw_list = utils.get_image_paths(src_dir, keyword=ext) # utils.py module
        for raw_im in raw_list:
            image_list.append(raw_im)

    # Save only the unique entries
    image_list = list(set(image_list))
    utils.remove_hidden(image_list)

    return image_list

#-----------------------------------MAIN---------------------------------------

if __name__ == "__main__":
    
    #### Set Up Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("input", 
                        help="folder containing training images")
    parser.add_argument("image_type", type=str, choices=['srgb','wv02_ms','pan'],
                        help="image type: 'srgb', 'wv02_ms', 'pan'")
    parser.add_argument("--tds_file", type=str, default=None,
                        help='''Existing training dataset file. Will create a new one with this name if none exists.
                        default: <image_type>_training_data.h5''')
    parser.add_argument("--username", type=str, default=None,
                        help='''username to associate with the training set.
                             default: image_type''')
    parser.add_argument("-a", "--enable_autorun", action="store_true",
                        help='''Enables the use of the autorun function.''')

    # Parse Arguments
    args = parser.parse_args()
    input_dir = os.path.abspath(args.input)  # Find input folder
    image_type = args.image_type
    autorun_flag = args.enable_autorun

    # Add the images in the provided folder to the image list
    img_list = scrape_dir(input_dir)

#    tds_file = validate_tds_file(args.tds_file, input_dir, image_type)

    if args.username is None:
        user_name = image_type
    else:
        user_name = args.username

    root = tk.Tk()
    
    TrainingWindow(root, img_list, user_name, image_type,
                   activate_autorun=autorun_flag).pack(side='top', fill='both', expand=True)
        
        
#    TrainingWindow(root, img_list, tds_file, user_name, image_type,
#                   activate_autorun=autorun_flag).pack(side='top', fill='both', expand=True)
    root.mainloop()
