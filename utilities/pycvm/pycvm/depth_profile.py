##
#  @file depth_profile.py
#  @brief Plots a 1D depth profile to an image or a pre-existing plot.
#  @author David Gill - SCEC <davidgil@usc.edu>
#  @version 14.7.0
#
#  Allows for generation of a 1D depth profile, either interactively, via
#  arguments, or through Python code in the class DepthProfile.

#  Imports
from common import Plot, Point, MaterialProperties, UCVM, UCVM_CVMS, plt
from scipy.interpolate import spline, splprep, splev
from scipy.interpolate import Rbf, InterpolatedUnivariateSpline
import scipy.interpolate as interpolate
import numpy as np
import pdb

##
#  @class DepthProfile
#  @brief Plots a 1D depth profile at a given @link common.Point Point @endlink.
#
#  Generates a 1D depth profile that can either be saved as a file or displayed
#  to the user. 
class DepthProfile:
    
    ##
    #  Initializes the 1D profile class.
    #
    #  @param startingpoint The @link common.Point starting point @endlink from which this plot should start.
    #  @param todepth The ending depth, in meters, where this plot should end.
    #  @param spacing The discretization interval in meters.
    #  @param cvm The CVM from which to retrieve these material properties.
    def __init__(self, startingpoint, todepth, spacing, cvm, threshold = None):
        if not isinstance(startingpoint, Point):
            raise TypeError("The starting point must be an instance of Point.")
        else:
            ## Defines the @link common.Point starting point @endlink for the depth profile.
            self.startingpoint = startingpoint
        
        if (todepth - self.startingpoint.depth) % spacing != 0:
            raise ValueError("%s\n%s\n%s" % ("The spacing value does not divide evenly into the requested depth. ", \
                          "Please make sure that the depth (%.2f - %.2f) divided by the spacing " % (todepth, startingpoint.depth), \
                          "%.2f has no remainder" % (spacing)))
        else:
            ## Defines the depth to which the plot should go in meters.
            self.todepth = todepth
            
        ## The discretization of the plot, in meters.
        self.spacing = spacing
        
        ## The CVM to use (must be installed with UCVM).
        self.cvm = cvm

        ## Private holding place for returned Vp data.        
        self.vplist = []
        ## Private holding place for returned Vs data.
        self.vslist = []
        ## Private holding place for returned density data.
        self.rholist = []

        ## Default threshold in simplified units
        self.threshold = threshold
    
    ## 
    #  Generates the depth profile in a format that is ready to plot.
    def getplotvals(self, properties=None, datafile = None):
        
        point_list = []
        
        # Generate the list of points.
 
#        for i in xrange(int(self.startingpoint.depth), int(self.todepth + 1), int(self.spacing)):
        for i in np.arange(self.startingpoint.depth, self.todepth + 1, self.spacing):
            point_list.append(Point(self.startingpoint.longitude, self.startingpoint.latitude, i))
            
        u = UCVM()
###MEI
        if (datafile != None) :
            print "\nUsing --> "+datafile
            print "expecting x ",self.num_x," y ",self.num_y
            data = u.import_binary(datafile, self.num_x, self.num_y)
        else:
            data = u.query(point_list, self.cvm)
        
        if(datafile != None) :
            for matprop in data:
                self.vplist.append(float(matprop.vp) / 1000)
                self.vslist.append(float(matprop.vs) / 1000)
                self.rholist.append(float(matprop.density) / 1000)
        else:  ## only read in 1 set at a time
            pass
# TODO: not sure how/what to store depth profile external data MEI 
    
    ##
    #  Adds the depth profile to a pre-existing plot.
    #
    #  @param plot The @link common.Plot Plot @endlink object to which we're plotting.
    #  @param properties An array of properties to plot. Can be vs, vp, or density.
    #  @param colors The colors that the properties should be plotted as. Optional.
    #  @param customlabels An associated array of labels to put for the legend. Optional.
    def addtoplot(self, plot, properties, colors = None, customlabels = None, datafile = None):
        
        # Check that plot is a Plot
        if not isinstance(plot, Plot):
            raise TypeError("Plot must be an instance of the class Plot.")
        
        # Get the material properties.
        self.getplotvals(properties = properties, datafile = datafile)
        
        max_x = 0
        yvals = []

        for i in xrange(int(self.startingpoint.depth), int(self.todepth + 1), int(self.spacing)):  
            yvals.append(i)       
        
        if customlabels != None and "vp" in properties: 
            vplabel = customlabels["vp"]
        else:
            vplabel = "Vp (km/s)" 
        
        if customlabels != None and "vs" in properties: 
            vslabel = customlabels["vs"]
        else:
            vslabel = "Vs (km/s)"  
        
        if customlabels != None and "density" in properties: 
            densitylabel = customlabels["density"]
        else:
            densitylabel = "Density (g/cm^3)"  

        if colors != None and "vp" in properties: 
            vpcolor = colors["vp"]
        else:
            vpcolor = "r" 
        
        if colors != None and "vs" in properties: 
            vscolor = colors["vs"]
        else:
            vscolor = "b"  
        
        if colors != None and "density" in properties: 
            densitycolor = colors["density"]
        else:
            densitycolor = "g"                
        
        if "vp" in properties:
            max_x = max(max_x, max(self.vplist))
            plot.addsubplot().plot(self.vplist, yvals, "-", color=vpcolor, label=vplabel)
        if "vs" in properties:
            max_x = max(max_x, max(self.vslist))
            plot.addsubplot().plot(self.vslist, yvals, "-", color=vscolor, label=vslabel)
## attempted to draw a smoothed line, not good
##            xs=np.array(self.vslist)
##            ys=np.array(yvals)
##            # spline parameters
##            s=3.0 # smoothness parameter
##            k=2 # spline order
##            nest=-1 # estimate of number of knots needed (-1 = maximal)
##            # find the knot points
##            tckp,u = splprep([xs,ys],s=s,k=k,nest=nest)
##            # evaluate spline, including interpolated points
##            newx,newy = splev(np.linspace(0,1,500),tckp)
##            plot.addsubplot().plot(newx, newy, "b-", label="smoothed"+vslabel)
            ## add a vline if there is a vs threshold
            if self.threshold != None : 
                plot.addsubplot().axvline(self.threshold/1000, color='k', linestyle='dashed')

        if "density" in properties:
            max_x = max(max_x, max(self.rholist))
            plot.addsubplot().plot(self.rholist, yvals, "-", color=densitycolor, label=densitylabel) 
        
        plt.legend(loc="lower left")
                
        if plt.ylim()[0] < plt.ylim()[1]:
            plt.gca().invert_yaxis() 
        
        if max_x > plt.xlim()[1]:
            plt.xlim(0, math.ceil(max_x / 0.5) * 0.5)

        plt.axis([0, max_x, int(self.todepth), int(self.startingpoint.depth)])
    
    ##
    #  Plots a new depth profile using all the default plotting options.
    #
    #  @param properties An array of material properties. Can be one or more of vp, vs, and/or density.
    #  @param filename If this is set, the plot will not be shown but rather saved to this location.
    def plot(self, properties, filename = None, meta = {}):

        if self.startingpoint.description == None:
            location_text = ""
        else:
            location_text = self.startingpoint.description + " "

        # Gets the better CVM description if it exists.
        try:
            cvmdesc = UCVM_CVMS[self.cvm]
        except: 
            cvmdesc = self.cvm

        # Call the plot object.
        p = Plot("%s%s Depth Profile From %sm To %sm at (%.2f,%.2f)" % (location_text, cvmdesc, self.startingpoint.depth, self.todepth, self.startingpoint.longitude, self.startingpoint.latitude), \
                 "Units (see legend)", "Depth (m)", None, 7, 10)

        # Add to plot.
        self.addtoplot(p, properties)
                
        if filename == None:
            plt.show()
        else:
            plt.savefig(filename)
