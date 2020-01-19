####
from bokeh.plotting import figure, output_file, show
from bokeh.models import CustomJS, TapTool
from bokeh.models.sources import ColumnDataSource
from bokeh.layouts import column, row
import matplotlib as mpl

mpl.use('Agg') ### important for rendering the rgba arrays
import matplotlib.pyplot as plt

import numpy as np

def generate_reference_figure(n=5):
        '''
        Generate dummy scatter with N dots as a bokeh figure
        '''
        p1 = figure(plot_width=400, plot_height=400,
                   tools="tap", title="Click the dots to switch images")
        ### in this case, "source origin" will refer to the active data of the
        ### interactive plot. We will need this later to pass to our JS code if we
        ### want to access it in the callback
        source_origin = ColumnDataSource(data=dict(
            x=np.arange(n),
            y=np.random.randint(0, 20, 5)
            ))

        p1.circle('x', 'y', size=20, source=source_origin)
        return p1, source_origin

def generate_some_rgba_img_graphs(n=1):
    """
    Input = int, number of charts te generate
    Output = list of generated rgba_imgs
    """
    rgba_img_list = []
    for ix in np.arange(n):
        x = np.linspace(0, 2, 1000)
        X, Y = np.meshgrid(x, x)
        data = np.sin((X+ix)**(ix+2) + Y**(ix+2))
        ### use plt to convert a data set to plt thing to rgba array
        im = plt.imshow(data)

        img = im.make_image('TkAgg"')
        rgba = img[0]
        rgba_img_list.append(rgba)
    return rgba_img_list


if __name__ == '__main__':
    ### out html output file
    output_file("rgba_img_toggle.html")

    ### The interactive plot as well as its data source
    scatter_fig, source_origin = generate_reference_figure()
    ### Figure to hold static data
    rgba_img_fig = figure(plot_width=400, plot_height=400,x_range=(0,1), y_range=(0,1),
               tools="tap", title="this is a static image")
    ### Create some random rgba_imgs
    rgba_img_list = generate_some_rgba_img_graphs(5)

    ### Put those images in a data source, which is a VERY IMPORTANT CLASS TO USE!!
    references = ColumnDataSource(data ={'imgs': rgba_img_list})

    ### Choose one of the images to use as the active image
    source = ColumnDataSource(data=dict(image = [rgba_img_list[0]]))

    ### Pass the ColumnDataSource to the static image holder. The keyword
    ### "source" tells the figure which dictionary to use, and the keyword
    ### "image" tell the figure which key to use to access the desired data from
    ### "source". With these method, we can change the value of source['image'],
    ### which will cause a corresponding change in the figure
    rgba_img_fig.image_rgba(image='image',source=source, x=0.0, y=0, dw=10, dh=1)

    ### Define JS to swap images: the args=dict passes the keys in the dict as
    ### local variables accessible in the JS code
    callback_img = CustomJS(args=dict(source=source,source_origin=source_origin, reference_imgs=references),
    code="""
        //this is how you print to the web console (viewable in browser for debugging)
        console.log(source_origin)

        //The source_origin data source knows which data has been selected(tapped) in the interactive plot
        var selected_indices = source_origin.selected['1d'].indices;

        //we can access both the index of the selection, and the value of the selection this way
        var selected_x_value = source_origin.data['x'][selected_indices[0]];

        //ow we access the ColumnDataSource which holds the active rgba_img
        var active = source['data'];

        //finally we use the x-value of the tapped circle to access the list of reference rgba_imgs
        var reference = reference_imgs['data']['imgs'][selected_x_value]

        // update the active rgba_img with the new one
        active['image'] = [reference];

        //trigger the change
        source.change.emit()
    """)

    ### Assign callback function to the callback we just wrote
    taptool = scatter_fig.select(type=TapTool)
    taptool.callback = callback_img

    ### Make an html
    show(row( scatter_fig,rgba_img_fig))
