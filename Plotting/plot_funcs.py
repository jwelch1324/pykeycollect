import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np


py.sign_in('jwelch1324','pzxu7DkSEfKysEA0MX9V')

def plot_tri_matrix(holdkey_matrix,qtkey):
    x = []
    y = []
    z = []
    c = []
    for i in range(38):
        for j in range(38):
            for k in range(38):
                khd = holdkey_matrix[i,j,k]
                tt = np.array(khd.timings)
                if len(tt) == 0:
                    continue
                mean = tt.mean()
                x.append(i)
                y.append(j)
                z.append(k)
                c.append(mean)
                
    text=list(map(lambda x: "({},{},{})<br>mean: {:.2f}".format(qtkey.get_key(x[0]),qtkey.get_key(x[1]),qtkey.get_key(x[2]),x[3]),zip(x,y,z,c)))
    tvals = [i for i in range(38)]
    ttext = list(map(lambda x: qtkey.get_key(x),tvals))
    trace = go.Scatter3d(
        x = np.array(x),
        y = np.array(y),
        z = np.array(z),
        text = text,
        hoverinfo = 'text',
        mode = 'markers',
        marker = dict(
            size=6,
            color=c,
            colorscale='Electric',
            opacity=0.8,            
        )
    )
    
    data = [trace]
    layout = go.Layout(
        margin=dict(l=0, r=0, b=0, t=0),
        scene=dict(
            xaxis=dict(
                title = 'First Key',
                tickvals=tvals,
                ticktext=ttext,
                tickangle=45,
            ),
            yaxis=dict(
                tickvals=tvals,
                ticktext=ttext,
                title = "Second Key",
                tickangle=90
            ),
            zaxis=dict(
                tickvals=tvals,
                ticktext=ttext,
                title="Third Key",
                tickangle=0
                
            )
        )
    )
    
    fig = go.Figure(data=data,layout=layout)
    py.iplot(fig)