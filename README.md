# Unreal ViS-WP Synthetic Data Collector
Unreal script project for automatic collection of ground-truth synthetic data for segmentation tasks. The label structure obeys the ViS-WP structure.

![unreal_viswp](https://github.com/synthyconstruction/UnrealSynthyConstruction/blob/main/doc/unreal_viswp.gif) 

# Version History:

## Version 2.3 [IN DEVELOPMENT]:
- [X][main.py] Argument based code execution.
- [X][main.py] Flag-based support.
- [X][light] Automated point light deployment on random camera coordinates (150 above camera level).
- [camera] Automated canonical camera collection for all classes simultaneously.
- [X][bim_model] Random activation of elements per class (randomization).
- [X][material] Automated creation of customDepth material, along with its flag.

## Version 2.2:
- [camera] Support for all cubemap direction camera deployment in a single script.
- [camera] Better camera grid estimation now eliminates cameras that are floating in space due to the estimation of uneven bounding boxes of non-rectangular floor objects. 
- [camera] Canonical camera functionality is now supported. Per class image collection is one at a time.
- [material] Support for automatic material mapping (before it was based on element manual selection) on ALL element layers.
- [material] Support for automatic custom depth material assignment on all material levels.
- [bim_model] Support for automated floor object selection for deploying camera grid.
- [main.py] A more organized code structure.

## Version 1:
- [main.py] Base support for all functionalities.
- [camera] Manual camera setup per direction.
- [material] Automated label creation and mapping.
- [material] Semi-automatic material assignment per class.
- [bim_model] Manual floor selection to determine where cameras are created.

# Getting Started

## Unreal and Plugins
Get started with a compatible Unreal Engine Version and the necessary plugins:
1. Install Unreal Engine V4.27 from Epic Games website
2. Install Datasmith Plugin for Navisworks, Sketchup, Revit, or Rhino for Unreal V4.27, available on the Datasmith website [Download Datasmith](https://www.unrealengine.com/en-US/datasmith/plugins)
3. From the Epic Games Launcher, go to the Marketplace, and download and install Unreal DataSmith plugin for Unreal V4.27. *Note: your unreal installation may already come with DataSmith Preinstalled*
4. Launch a project with Unreal, and in the plugins section, enable the Python Editor Script Plugin [Unreal Official Instructions](https://docs.unrealengine.com/4.27/en-US/ProductionPipelines/ScriptingAndAutomation/Python/)

## Packages in Unreal Python
Install the necessary packages directly to the Unreal Python interpreter:
1. From CMD terminal run -->   "C:\Program Files\Epic Games\UE_4.26\Engine\Binaries\ThirdParty\Python3\Win64\python.exe" -m pip install MODULENAME
2. MODULENAMEs to be installed include: `unreal`, `numpy`, `matplotlib` and `math`

## Create and setup your first SIEProject
1. Launch Unreal and create a new empty project for Architecture & Engineering (this automatically enables the DataSmith plugin)
2. Enable the Python Scripting plugin from the Plugins wizard. You will be prompted to restart the engine. DO NOT RESTART IT, as we will be making more setups that will also require a project restart.
3. Configure your Python paths in the project by opening the **Edit > Project Settings**, and searching for Python in the search bar. Then, under the Additional Paths, add 5 new paths indicating where each of the folders of this repo are located. *Note: your paths will depend on where you downloaded this repository on your computer*:
   1.  `C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\ue_master\unreal_viswp\`
   2.  `C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\ue_master\unreal_viswp\materials`
   3.  `C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\ue_master\unreal_viswp\light`
   4.  `C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\ue_master\unreal_viswp\cameras`
   5.  `C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\ue_master\unreal_viswp\bim_model`
4. [RECOMMENDED] Change the autosave function by opening **Edit > Editor Settings**, and searching for autosave in the search bar. Change the following settings: 
   1. `Frequency in Minutes` = 60
   2. `Interaction Delay in Seconds` = 15
   3. `Warning in seconds` = 30 
5. Restart your project.

## Import project geometry using DataSmith 
1. Export from the modeling platform your model using the Datasmith Plugin. Depending on your arrangement of exports, you may create several `.udatasmith` files.
2. Upon relaunching your SIEProject, clean your new project from unnecessary default geometry and actors. *Note: Make sure to NOT delete the `SunSky` and `ExponentialHeightFog` elements.*
   
   ![delete_unwanted_elems](https://github.com/synthyconstruction/UnrealSynthyConstruction/blob/main/doc/img.png)
4. To begin importing new geometry, click the DataSmith button to open the wizard, and select the `.udatasmith` files of interest from step 1.
5. [RECOMMENDED] For better content browser organization, save all imported geometry in a separate folder in the Content Browser.
   
   ![SIEFolder_content_browser](https://github.com/synthyconstruction/UnrealSynthyConstruction/blob/main/doc/SIEFolder_content_browser.png)
   
7. Once the import begins, ensure to ONLY import `Geometry`, and `Materials & Textures`. Later on, we will be creating our own `Lights`, and `Cameras`.
   
   ![import_options](https://github.com/synthyconstruction/UnrealSynthyConstruction/blob/main/doc/import_options.png)

## Running main.py
1. Open the Python Scripting output console by enabling **Window > Developer Tool > Output Log**
2. On the console, you only need to type the name of the file `main.py` to execute it.
3. The main.py is currently not supporting flags in version 2.2. To run each case, you will be making use of boolean variables inside the code:
   
   1. `POST_PROCESS_VOL_CREATE = False`
   
   2. `CREATE_CAMERAS = False`
   3. `CREATE_CANONICAL_CAMERAS = False`
   4. `CAPTURE_CANONICAL_ELEMS = False`
   5. `TAKE_PHOTOS = False`
   
   6. `IMPORT_TEXTURES = False`
   7. `CREATE_MATERIAL = False`
   8. `APPLY_MATERIAL = False`
   
   9. `APPLY_DEPTH = False`
   
   10. `CREATE_LABELS = False`
   11. `APPLY_LABELS = False`
   12. `CREATE_PER_ELEMENT_MAP = False`
   
   13. `COUNT_ELEMS = True`

## Recommended code pipeline execution steps

### Collecting Rendered Images
![render](https://github.com/synthyconstruction/UnrealSynthyConstruction/blob/main/doc/render.png)

1. Create Cameras (`CREATE_CAMERAS = True`) and PostProcess Volume (`POST_PROCESS_VOL_CREATE = True`).
2. Run `main.py` from the output console.
3. Load Textures (`IMPORT_TEXTURES = True`), create material instances (`CREATE_MATERIAL = True`), and automatically apply them to objects (`APPLY_MATERIAL = True`).
4. Run `main.py` from the output console.
5. Wait for textures to load properly; this may take some time, depending on your computer specs.
6. Manually select up to 1000 cameras from your asset manager, and enable the photo capture function (`TAKE_PHOTOS = True`). *NOTE: selecting more than 1000 cameras at a time might result in desynchronization between the code execution and the rendering, resulting in some cameras not collecting their images. If this problem happens, reduce the number of cameras selected for every execution.*
7. Run `main.py` from the output console. 
8. Repeat steps 6 and 7 until done collecting images with all cameras.
9. By default, images are stored in `C:\Users\[USERNAME]\Documents\Unreal Projects\[PROJECTNAME]\Saved\Screenshots\Windows`. Copy them elsewhere to avoid overwriting these with other modalities later on.

### Collecting Depth Images
![depth_map](https://github.com/synthyconstruction/UnrealSynthyConstruction/blob/main/doc/depth_map.png)

*NOTE: make sure you have your cameras already created (see step 1). If you already have your cameras created, there is no need to run that step again.*
**Instructions to come later**

### Creating and Applying Label Maps
![rgb_mask](https://github.com/synthyconstruction/UnrealSynthyConstruction/blob/main/doc/rgb_mask.png)

*NOTE: make sure you have your cameras already created (see step 1). If you already have your cameras created, there is no need to run that step again.*
**Instructions to come later**

### Capturing SurfaceNormals
![surface_normal](https://github.com/synthyconstruction/UnrealSynthyConstruction/blob/main/doc/surface_normal.png)

*NOTE: make sure you have your cameras already created (see step 1). If you already have your cameras created, there is no need to run that step again.*
**Instructions to come later**

### Working with Canonical Cameras
![canonical_camera](https://github.com/synthyconstruction/UnrealSynthyConstruction/blob/main/doc/canonical_view.png)

*NOTE: make sure you have your cameras already created (see step 1). If you already have your cameras created, there is no need to run that step again.*
**Instructions to come later**
