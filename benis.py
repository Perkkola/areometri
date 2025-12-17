import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. PREPARE YOUR DATA
# Ideally, load the CSV you got from WebPlotDigitizer.
# For this example, I will create DUMMY data that mimics your image
# so you can run this script immediately to see the result.
# ---------------------------------------------------------

data = {
    # Simulating the '6 min' curves
    'Diameter_mm': [0.0003974002352170437,
0.0004396347386455457,
0.0004999205146280545,
0.0005403467363140061,
0.0005935379189444674,
0.0006339916101186609,
0.0006959181843404155,
0.0007387490282905029,
0.0007975747800159157], # X-axis
    'Reading_23C': [1.1087818734932073,
1.0990400848840567,
1.08271682705545,
1.069557112061729,
1.049814316125956,
1.0334821938230732,
1.0088612508310444,
0.9888697123746717,
0.9676610547381286], # Y-axis curve 1


}
df = pd.DataFrame(data)

fig = go.Figure()

# Add the main curve
fig.add_trace(go.Scatter(
    x=df['Diameter_mm'],
    y=df['Reading_23C'],
    mode='lines+markers',
    name='6 min (23°C)'
))

# ---------------------------------------------------------
# OPTION A: The Grid Method (Recommended)
# This forces the grid lines to appear EXACTLY at your specific values.
# ---------------------------------------------------------
specific_y_lines = [1.000, 1.010, 1.020, 1.030, 1.040]

fig.update_yaxes(
    # This tells Plotly: "Only draw grid lines at these exact numbers"
    tickvals=specific_y_lines,
    
    # Optional: formatting to show 3 decimal places (1.000)
    ticktext=["{:.3f}".format(x) for x in specific_y_lines], 
    
    # Grid styling
    showgrid=True,
    gridwidth=1,
    gridcolor='black', # Make them dark like the original image
)

# ---------------------------------------------------------
# OPTION B: The "add_hline" Method
# Use this if you want specific highlighted lines (like a limit)
# independent of the grid.
# ---------------------------------------------------------
# fig.add_hline(y=1.000, line_dash="dash", line_color="red")
# fig.add_hline(y=1.010, line_dash="dot", line_color="blue")


# ---------------------------------------------------------
# FINAL LAYOUT
# ---------------------------------------------------------
fig.update_layout(
    title="Hydrometer Analysis",
    xaxis_title="Grain Diameter d (mm)",
    yaxis_title="Hydrometer Reading",
    xaxis_type="log",
    
    # This mimics the white background with black axes of your image
    plot_bgcolor='white', 
    xaxis=dict(showline=True, linecolor='black', ticks='outside'),
    yaxis=dict(showline=True, linecolor='black', ticks='outside'),
    
    # Reverses Y axis (standard for hydrometers: 1.000 is usually top)
    yaxis_autorange="reversed" 
)

fig.show()