from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
import pandas as pd
from itertools import chain
import argparse

parser = argparse.ArgumentParser(description='Make run plot')
parser.add_argument('-f', '--first', help="First line to include in plot", default=None, required=False)
parser.add_argument('-l', '--last', help="Last line to include in plot", default=None, required=False)
parser.add_argument('-i', '--input', help="CSV input file", default="inputs/data.csv", required=False)
parser.add_argument('-t', '--title', help="Plot title", default="", required=False)
args = parser.parse_args()


setnames = ['Noise: 1.2 Vpp']
check = True
line = True
errorOn = False

file_path = args.input
title = args.title

#row_ranges = [list(chain(range(374,400)))] # Driving only module 1 H2/H3, floating
#setnames = ['Driving module 1 (H2 & H3) cable']

row_ranges = [list(chain(range(635,648)))] # Driving only module 1 H2/H3, floating
#setnames = ['CO2 plant in']; title = "Module 1 cable driven, ferrite on Module 2"

#row_ranges = [list(chain(range(374,400))), list(chain(range(403, 427)))] # 1 cable, no ground vs. ground
#setnames = ['Floating', 'Ground to chassis']; title = "1.2 Vpp sine wave; only applied to Module 1 cable (Hybrids 2 & 3)"

#row_ranges = [list(chain(range(469,485))), list(chain(range(488, 504)))] # 1 cable, no ground vs. ground
#setnames = ['No ferrite', 'Ferrite on Mod. 1 cable']; title = "1.2 Vpp sine on Module 1 cable (Hybrids 2 & 3); ground to patch panel ground"

#row_ranges = [list(chain(range(488, 504))), list(chain(range(512, 528)))] # ferite gnd v no gournd
#setnames = ['Ferrite; GND', 'Ferrite; FLOAT']; title = "1.2 Vpp sine on Module 1 cable (Hybrids 2 & 3)"

#row_ranges = [list(chain(range(570, 589))), list(chain(range(593,610))), list(chain(range(615,629)))] # ferite gnd v no gournd
#setnames = ['HV', 'LV/GND', "GND"]; title = "1.2 Vpp sine on Module 1 induvidual wires:"

#row_ranges = [list(chain(range(191,217),range(218,222))), list(chain(range(229, 231), range(232, 244)))] # CO2 vs wire pusling
#setnames = ['2 Vpp on CO2 manifold', '1.2 Vpp on cables']

#row_ranges = [list(chain(range(279,307))), range(335,345)] # CO2 disconnected no ground v ground
#setnames = ['Plank floating', 'Ground to chassis']

#row_ranges = [list(chain(range(279,307)))] # CO2 disconnected 
#setnames = ['Plank floating']

Hybrids = [2,3,4,5]

if ((args.first is not None) and (args.last is not None)):
    row_ranges = [list(chain(range(int(args.first),int(args.last))))]

def main():

    x_values_list, y_values_lists, no_noise = parse_csv(file_path, row_ranges)
    plot_noise(x_values_list, y_values_lists, "Frequency (MHz)", "Average channel noise", title,
        x_lim=(1, 14), y_lim=(0.01, 17), aspect_ratio=0.6, y_lines=no_noise)

def parse_csv(file_path, row_ranges):
    df = pd.read_csv(file_path)
    
    x_values_list = []
    y_values_lists = []

    no_noise = [5,5,5,5]

    
    for row_range in row_ranges:
        if check:
            print(f"{df.iloc[row_range[0]-1,0]}")
            print(f"Rows: {df.iloc[row_range]}")
        selected_rows = df.iloc[row_range]
        selected_rows = selected_rows.astype({selected_rows.columns[4]: float}).sort_values(by=selected_rows.columns[4])

        x_values = selected_rows.iloc[:, 4].to_numpy()
        y_values = selected_rows.iloc[:, 7:11].astype(float).values.tolist()



        if x_values[0] == 0:
            x_values = np.delete(x_values, 0)
            no_noise = y_values.pop(0)


        x_values_list.append(x_values)
        y_values_lists.append(y_values)
        
    return x_values_list, y_values_lists, no_noise

def plot_noise(x_values_list, y_values_lists, x_label="X-axis", y_label="Y-axis", title="Scatter Plot",
               x_lim=None, y_lim=(0, 10), aspect_ratio=1.5, y_lines=None, markers=None):
    plt.style.use(hep.style.CMS)      
    colors = ['blue', 'red', 'green', 'orange']
    labels = ['Hybrid 2', 'Hybrid 3', 'Hybrid 4', 'Hybrid 5']
    default_markers = ['o', '^', 'D']
    default_lines = ['solid', 'dotted', 'dashdot']
    
    if markers is None:
        markers = default_markers[:len(x_values_list)]
    
    fig, ax = plt.subplots(figsize=(10, 7))
    biggestYVal = 0    
    smallestXVal = 100    
    biggestXVal = 0    
    for j, (x_values, y_values_list) in enumerate(zip(x_values_list, y_values_lists)):
        for i in Hybrids:
            y_values = [y_set[i-2] for y_set in y_values_list]
            if max(y_values) > biggestYVal:
                biggestYVal = max(y_values)
            if min(x_values) < smallestXVal:
                smallestXVal = min(x_values)
            if max(x_values) > biggestXVal:
                biggestXVal = max(x_values)
            face_color = 'white' if j % 2 == 1 else colors[i-2]
            edge_color = colors[i-2] 
            if errorOn:
                ax.errorbar(x_values, y_values, yerr=flatError(y_values, 0.1),
                            color=colors[i-2], zorder=0, alpha=0.2, linestyle='' )
            if line:
                ax.plot(x_values, y_values, 
                        marker=markers[j % len(markers)], markerfacecolor=face_color,
                        color=colors[i-2], alpha=0.70, linestyle=default_lines[j], zorder=10)
            else:
                ax.scatter(x_values, y_values,
                           facecolors=face_color, edgecolors=edge_color,
                           marker=markers[j % len(markers)], alpha=0.70, zorder=10)

    if y_lines:
        for i in Hybrids:
            ax.axhline(y=y_lines[i-2], color=colors[i-2], linestyle='dashed')
    
    legend_elements = []

    marker_elements = [Line2D([0], [0], color='black', linestyle='None', label=f"{setnames[markers.index(marker)]}",
                              marker=marker, markersize=8, markerfacecolor='none' if markers.index(marker) % 2 == 1 else 'black') for marker in markers]
    baseline_element = Line2D([0], [0], color='black', linestyle='dashed', lw=2, label='No noise')
    dummy_elements = [Line2D([0], [0], linestyle='None', label='') for i in range(3-len(setnames))]
    color_elements = [Line2D([0], [0], color=colors[i-2], lw=12, label=labels[i-2]) for i in Hybrids]
    if len(Hybrids) < 4: color_elements.extend([Line2D([0], [0], linestyle='None', label='') for i in range(4-len(Hybrids))])
    
    legend_elements.extend(marker_elements)
    legend_elements.append(baseline_element)
    legend_elements.extend(dummy_elements)  
    legend_elements.extend(color_elements)
    
    ax.legend(handles=legend_elements, loc='upper right', ncol=2, columnspacing=1.5)
    
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title, size='x-small')

    ax.set_ylim([0, biggestYVal*1.3])
    ax.set_xlim([smallestXVal-(biggestXVal*0.1), biggestXVal*1.1])


    plt.savefig('noise.png', dpi=400)
    plt.show()
    #plt.gcf().set_size_inches(10, 5)
    
def flatError(yVals, percentErr):
    rescale = [num * percentErr for num in yVals]
    return rescale

if __name__ == "__main__":
    main()
