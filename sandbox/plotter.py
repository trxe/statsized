import matplotlib.pyplot as plt
import polars as pl
import matplotlib.dates as mdates
import matplotlib.cm as cm
import psycopg

from typing import Any, Sequence

class DictRowFactory:
    def __init__(self, cursor: psycopg.Cursor[Any]):
        self.fields = [c.name for c in cursor.description]

    def __call__(self, values: Sequence[Any]) -> dict[str, Any]:
        return dict(zip(self.fields, values))

# Example: Adding a "sales" column to the data
conn = psycopg.connect(f"dbname=nhl user=trxe", row_factory=DictRowFactory)

shifts_per_game = conn.execute(""" 
                               SELECT period, player_id
                               FROM shifts 
                               WHERE game_id = 2024020861;""")
                            
                            #    datetime, 
                            #    start_time + ((period - 1) * INTERVAL '20 minutes') AS start, 
                            #    end_time + ((period - 1) * INTERVAL '20 minutes') AS end, 
                            #    shifts.game_id, shifts.player_id, first_name, last_name, shifts.team_id 
                            #    FULL OUTER JOIN games on shifts.game_id = games.game_id 
                            #    FULL OUTER JOIN players on players.player_id = shifts.player_id 
test = shifts_per_game.fetchall()
print(test)
# print(shifts_per_game.fetchall())

# # Convert strings to datetime objects
# data['start_time'] = pd.to_datetime(data['start_time'])
# data['end_time'] = pd.to_datetime(data['end_time'])

# # Normalize sales for color mapping (0 to 1)
# norm = plt.Normalize(vmin=min(data['sales']), vmax=max(data['sales']))

# # Create a figure and axis for plotting
# fig, ax = plt.subplots(figsize=(10, 6))

# # Create a colormap (using 'viridis' for better visibility)
# cmap = cm.inferno

# # Plot each player's shift as a horizontal bar, with color intensity based on sales
# for index, row in data.iterrows():
#     ax.barh(row['first_name'] + ' ' + row['last_name'],
#             (row['end_time'] - row['start_time']).seconds / 3600,  # Duration in hours
#             left=row['start_time'].hour + row['start_time'].minute / 60,
#             height=0.6,
#             color=cmap(norm(row['sales'])))  # Color based on sales

# # Format the x-axis to show time in hours
# ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# # Rotate the labels to avoid overlap
# plt.xticks(rotation=45)

# # Set labels
# plt.xlabel('Time')
# plt.ylabel('Player')

# # Title
# plt.title('Shift Chart with Sales-Based Color Intensity')

# # Add a colorbar
# sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# sm.set_array([])
# plt.colorbar(sm, ax=ax, label='Number of Sales')

# # Show the plot
# plt.tight_layout()
# plt.show()
