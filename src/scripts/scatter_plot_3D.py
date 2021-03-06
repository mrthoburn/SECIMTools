#!/usr/bin/env python
######################################################################################
# DATE: 2016/August/10
# 
# MODULE: scatter_plot_3D.py
#
# VERSION: 1.1
# 
# AUTHOR: Matt Thoburn (mthoburn@ufl.edu), Miguel Ibarra (miguelib@ufl.edu)
#
# DESCRIPTION: This is a standalone executable for graphing 3D scatter plots
# from wide data
#
################################################################################
# Import built-in libraries
import os
import logging
import argparse
from argparse import RawDescriptionHelpFormatter

# Import add-on libraries
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

# Import local data libraries
from dataManager import logger as sl
from dataManager.interface import wideToDesign

# Import local plotting libraries
from visualManager import module_scatter as scatter
from visualManager.manager_color import colorHandler
from visualManager.manager_figure import figureHandler

def getOptions(myOpts=None):
    description="Standa alone function to plot Scatter Plots 3D"
    parser = argparse.ArgumentParser(description=description, 
                        formatter_class=RawDescriptionHelpFormatter)
    standard = parser.add_argument_group(title='Standard input', 
                                description='Standard input for SECIM tools.')
    # Standard input
    standard = parser.add_argument_group(title="Standard input", 
                        description='Standard input for SECIM tools.')
    standard.add_argument( "-i","--input", dest="input", action='store', 
                        required=True, help="Input dataset in wide format.")
    standard.add_argument("-d" ,"--design",dest="design", action='store', 
                        required=False,default=False, help="Design file.")
    standard.add_argument("-id", "--ID",dest="uniqID", action='store', 
                        required=True, help="Name of the column with unique "\
                        "identifiers.")
    standard.add_argument("-g", "--group",dest="group", action='store', 
                        required=False, default=False, help="Name of the column"\
                        " with groups.")
    # Tool input
    tool = parser.add_argument_group(title="Tool especific input")
    tool.add_argument("-x" ,"--X",dest="x", action='store', 
                        required=True, help="Name of column for X values")
    tool.add_argument("-y", "--Y",dest="y", action='store', 
                        required=True, help="Name of column for Y values")
    tool.add_argument("-z", "--Z",dest="z", action='store', 
                        required=True, help="Name of column for Z values")
    # Tool output
    output = parser.add_argument_group(title="Output")
    output.add_argument("-f","--figure",dest="figure",action="store",
                        required=False, help="Path of figure.")
    # Plot options
    plot = parser.add_argument_group(title='Plot options')
    plot.add_argument("-pal","--palette",dest="palette",action='store',required=False, 
                        default="tableau", help="Name of the palette to use.")
    plot.add_argument("-col","--color",dest="color",action="store",required=False, 
                        default="Tableau_20", help="Name of a valid color scheme"\
                        " on the selected palette")
    plot.add_argument("-r", "--rotation", dest="rotation", action='store',
                        required=False, default=45,help="camera viewing rotation")
    plot.add_argument("-e", "--elevation", dest="elevation", action='store',
                        required=False, default=45,help="Camera vieweing elevation")
    args = parser.parse_args()
    # Standardize paths
    args.input  = os.path.abspath(args.input)
    args.figure = os.path.abspath(args.figure)
    if args.design:
        args.design = os.path.abspath(args.design)
    return(args)
     
def main(args):
    # Loading design
    if args.design:
        design = pd.DataFrame.from_csv(args.design,sep="\t")
        design.reset_index(inplace=True)
    else:
        design = False

    # Loading wide file
    wide = pd.DataFrame.from_csv(args.input,sep="\t")

    # Open Figure handler
    fh = figureHandler(proj="3d", figsize=(14,8))

    # If design file with group and the uniqID is "sampleID" then color by group
    if args.group and args.uniqID == "sampleID":
        glist=list(design[args.group])
        colorList, ucGroups = palette.getColorsByGroup(design=design,
                                group=args.group,uGroup=sorted(set(glist)))
    else:
        glist = list()
        colorList = palette.mpl_colors[0]
        ucGroups = dict()
    
    # Plot scatterplot 3D
    scatter.scatter3D(ax=fh.ax[0], x=list(wide[args.x]), y=list(wide[args.y]),
                    z=list(wide[args.z]), colorList=colorList)
    
    # Despine axis (spine = tick)
    fh.despine(fh.ax[0])

    # Give format to the plot
    fh.format3D(title=args.x + " vs " + args.y + " vs " + args.z, xTitle=args.x,
                yTitle=args.y, zTitle=args.z, rotation=float(args.rotation),
                elevation=float(args.elevation))
    
    # If groups are provided create a legend
    if args.group and args.uniqID == "sampleID":
        fh.makeLegend(ax=fh.ax[0],ucGroups=ucGroups,group=args.group)
        fh.shrink()

    # Saving figure to file
    with PdfPages(args.figure) as pdfOut:
        fh.addToPdf(dpi=600, pdfPages=pdfOut)
    logger.info("Script Complete!")

if __name__ == '__main__':
    # Command line options
    args   = getOptions()

    # Set logger
    logger = logging.getLogger()
    sl.setLogger(logger)

    # Stablishing color palette
    palette = colorHandler(pal=args.palette, col=args.color)
    logger.info(u"Using {0} color scheme from {1} palette".format(args.color,
                args.palette))

    # Run everything
    main(args)