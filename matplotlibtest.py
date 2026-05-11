import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from multiprocessing import Process,shared_memory
import random
existing_shm = shared_memory.SharedMemory(name="cords")

# initial data
x = []
y = []

# creating the figure and axes object
fig, ax = plt.subplots()

# update function to update data and plot
def update(frame):
    # updating the data by adding one more point
    raw_data = bytes(existing_shm.buf[:20])
    x,y = raw_data.decode('utf-8').split(",")

    ax.clear()  # clearing the axes
    ax.scatter(x,y, s = y, c = 'b', alpha = 0.5)  # creating new scatter chart with updated data
    fig.canvas.draw()  # forcing the artist to redraw itself

anim = FuncAnimation(fig, update)
plt.show()